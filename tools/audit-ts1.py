#!/usr/bin/env python3
"""Read-only TS1 inventory: run from the repository root (Python + fontTools).

Use --ts1enc PATH to select the LaTeX kernel's ts1enc.def explicitly.
Missing kernel slots are reported, not treated as consistency errors.
"""

import argparse
from pathlib import Path
import re
import struct
import subprocess

from fontTools import t1Lib
from fontTools.pens.boundsPen import BoundsPen


def metric_widths(path):
    data = path.read_bytes()
    _, lh, bc, ec, nw, *_ = struct.unpack_from('>12H', data)
    start = 24 + 4 * lh
    table = start + 4 * (ec - bc + 1)
    widths = struct.unpack_from(f'>{nw}i', data, table)
    return {
        i: widths[data[start + 4 * (i - bc)]] * 1000 / 2**20
        for i in range(bc, ec + 1) if data[start + 4 * (i - bc)]
    }


def vector(path):
    body = re.sub(r'%[^\n]*', '', path.read_text()).split('[', 1)[1].split(']', 1)[0]
    names = re.findall(r'/([^\s/]+)', body)
    if len(names) != 256:
        raise ValueError(f'{path}: expected 256 slots, got {len(names)}')
    return names


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ts1enc', type=Path)
    args = parser.parse_args()
    kernel = args.ts1enc or Path(subprocess.check_output(
        ['kpsewhich', 'ts1enc.def'], text=True).strip())
    declarations = re.findall(
        r'\\DeclareText(?:Symbol|Accent)\s*\{\\(\w+)\}\{TS1\}\{(\d+)\}',
        kernel.read_text())
    required = {int(slot): command for command, slot in declarations}
    root = Path(__file__).resolve().parents[1] / 'newtxtt'
    vectors = {z: vector(root / 'enc' / f'tcx{z.upper()}ec.enc') for z in 'abcde'}
    map_lines = (root / 'map' / 'newtxtt.map').read_text().splitlines()
    maps = {line.split()[0]: line for line in map_lines if line.strip() and not line.startswith('%')}
    errors = []
    missing = {}
    outlines = {}
    for prefix, pfb in [('newtcxtt', 'newtcxtt'), ('newtcxsl', 'newtcxtt'),
                        ('newtcxbtt', 'newtcxbtt'), ('newtcxbsl', 'newtcxbtt')]:
        if pfb not in outlines:
            glyphs = t1Lib.T1Font(str(root / 'type1' / f'{pfb}.pfb')).getGlyphSet()
            widths = {}
            for name, glyph in glyphs.items():
                glyph.draw(BoundsPen(glyphs))
                widths[name] = glyph.width
            outlines[pfb] = widths
        widths = outlines[pfb]
        for z, names in vectors.items():
            font = prefix + z
            metric = metric_widths(root / 'tfm' / f'{font}.tfm')
            encoded = {i for i, name in enumerate(names) if name != '.notdef'}
            if encoded != metric.keys():
                errors.append(f'{font}: vector-only {sorted(encoded - metric.keys())}; '
                              f'metric-only {sorted(metric.keys() - encoded)}')
            line = maps.get(font, '')
            if f'<[tcx{z.upper()}ec.enc' not in line or f'<{pfb}.pfb' not in line:
                errors.append(f'{font}: wrong or absent map entry')
            for i in encoded & metric.keys():
                name = names[i]
                if name not in widths:
                    errors.append(f'{font} slot {i}: no outline {name}')
                elif abs(metric[i] - widths[name]) > 1:
                    errors.append(f'{font} slot {i}: metric width {metric[i]:.3f}, '
                                  f'outline width {widths[name]}')
            absent = tuple(sorted(required.keys() - encoded))
            missing.setdefault(absent, []).append(font)
    print(f'Checked {sum(map(len, missing.values()))} metric/vector/map combinations.')
    for slots, fonts in missing.items():
        print(f'Unencoded kernel-declared slots ({len(fonts)} metrics):')
        for slot in slots:
            print(f'  {slot:3d}  {required[slot]}')
    for pfb, widths in outlines.items():
        encoded_names = set().union(*vectors.values())
        print(f'{pfb}: outlines unused by all five vectors:')
        print('  ' + ', '.join(sorted(widths.keys() - encoded_names)))
    for error in errors:
        print('ERROR:', error)
    print(f'{len(errors)} consistency errors.')
    return bool(errors)


if __name__ == '__main__':
    raise SystemExit(main())
