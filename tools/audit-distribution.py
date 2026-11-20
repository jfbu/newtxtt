#!/usr/bin/env python3
"""Read-only audit of newtxtt's FD, map, ENC, TFM and PFB relationships.

Requires Python 3 and fontTools. Optionally compare against an unpacked
original newtxtt directory with --reference PATH. Exit 1 if discrepancies
are found; unmapped legacy metrics are informational.
"""

import argparse
from collections import defaultdict
from pathlib import Path
import re
import struct

from fontTools import t1Lib
from fontTools.pens.boundsPen import BoundsPen


ROOT = Path(__file__).resolve().parents[1] / 'newtxtt'


def read_metric(path):
    data = path.read_bytes()
    lf, lh, bc, ec, nw, nh, nd, ni, nl, nk, ne, np = struct.unpack_from('>12H', data)
    if lf * 4 != len(data):
        raise ValueError(f'{path.name}: invalid TFM length')
    start = 24 + 4 * lh
    end = start + 4 * (ec - bc + 1)
    pos = end
    tables = []
    for n in (nw, nh, nd, ni):
        tables.append(struct.unpack_from(f'>{n}i', data, pos))
        pos += 4 * n
    records = {}
    for slot in range(bc, ec + 1):
        w, hd, it, rem = data[start + 4 * (slot - bc):start + 4 * (slot - bc + 1)]
        if w:
            records[slot] = (tables[0][w], tables[1][hd >> 4], tables[2][hd & 15],
                             tables[3][it >> 2], it & 3, rem)
    return records, data[24:start], data[pos:]


def read_vector(path):
    text = re.sub(r'%[^\n]*', '', path.read_text())
    head, body = text.split('[', 1)
    name = re.search(r'/([^\s/]+)', head)[1]
    glyphs = re.findall(r'/([^\s/]+)', body.split(']', 1)[0])
    if len(glyphs) != 256:
        raise ValueError(f'{path.name}: expected 256 encoding slots')
    return name, glyphs


def read_font(path):
    font = t1Lib.T1Font(str(path))
    glyphs = font.getGlyphSet()
    widths = {}
    for name, glyph in glyphs.items():
        glyph.draw(BoundsPen(glyphs))
        widths[name] = glyph.width
    return font, widths


def program(charstring):
    charstring.decompile()
    return tuple(charstring.program)


def compare_reference(reference, metrics, fonts, errors):
    count = 0
    for path in sorted((reference / 'tfm').glob('*.tfm')):
        if path.stem not in metrics:
            errors.append(f'reference metric removed: {path.name}')
            continue
        old, header, tail = read_metric(path)
        new, new_header, new_tail = metrics[path.stem]
        if header != new_header or tail != new_tail:
            errors.append(f'{path.name}: TFM header or auxiliary tables changed')
        for slot, rec in old.items():
            if new.get(slot) != rec:
                errors.append(f'{path.name}: existing metric changed at {slot}')
        count += 1
    print(f'Reference metrics compared: {count}')
    count = 0
    for path in sorted((reference / 'type1').glob('*.pfb')):
        if path.name not in fonts:
            errors.append(f'reference outline removed: {path.name}')
            continue
        old = t1Lib.T1Font(str(path))
        old.parse()
        new = fonts[path.name][0]
        for key in ('FontName', 'FontMatrix', 'FontBBox', 'Encoding'):
            if old[key] != new[key]:
                errors.append(f'{path.name}: {key} changed')
        for name, glyph in old['CharStrings'].items():
            other = new['CharStrings'].get(name)
            if other is None or program(glyph) != program(other):
                errors.append(f'{path.name}: existing charstring changed: {name}')
        if ([program(s) for s in old['Private']['Subrs']]
                != [program(s) for s in new['Private']['Subrs']]):
            errors.append(f'{path.name}: subroutines changed')
        count += 1
    print(f'Reference Type 1 fonts compared: {count}')
    if (reference / 'map' / 'newtxtt.map').read_bytes() != (ROOT / 'map' / 'newtxtt.map').read_bytes():
        errors.append('reference font map changed')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference', type=Path, help='original unpacked newtxtt directory')
    args = parser.parse_args()
    errors = []
    metrics = {p.stem: read_metric(p) for p in sorted((ROOT / 'tfm').glob('*.tfm'))}
    vectors = {p.name: read_vector(p) for p in sorted((ROOT / 'enc').glob('*.enc'))}
    fonts = {p.name: read_font(p) for p in sorted((ROOT / 'type1').glob('*.pfb'))}
    maps = {}
    groups = defaultdict(list)
    used_vectors, used_fonts = set(), set()
    for line in (ROOT / 'map' / 'newtxtt.map').read_text().splitlines():
        if not line.strip() or line.lstrip().startswith('%'):
            continue
        name, psname, *_ = line.split()
        if name in maps:
            errors.append(f'duplicate map entry: {name}')
            continue
        maps[name] = line
        enc_match = re.search(r'<\[([^\s]+\.enc)', line)
        pfb_match = re.search(r'<([^\s]+\.pfb)', line)
        if not enc_match or not pfb_match:
            errors.append(f'{name}: malformed map entry')
            continue
        enc, pfb = enc_match[1], pfb_match[1]
        if name not in metrics or enc not in vectors or pfb not in fonts:
            errors.append(f'{name}: missing map dependency ({enc}, {pfb})')
            continue
        used_vectors.add(enc)
        used_fonts.add(pfb)
        encoding_name, glyph_names = vectors[enc]
        font, widths = fonts[pfb]
        if font['FontName'] != psname:
            errors.append(f'{name}: PostScript font name mismatch')
        if not re.search(r'\b' + re.escape(encoding_name) + r'\s+ReEncodeFont\b', line):
            errors.append(f'{name}: PostScript encoding name mismatch')
        recs = metrics[name][0]
        encoded = {i for i, n in enumerate(glyph_names) if n != '.notdef'}
        missing = tuple((i, glyph_names[i]) for i in sorted(encoded - recs.keys()))
        no_outline = tuple((i, glyph_names[i]) for i in sorted(encoded) if glyph_names[i] not in widths)
        surplus = tuple(sorted(recs.keys() - encoded))
        wrong_width = []
        for i in sorted(encoded & recs.keys()):
            glyph = glyph_names[i]
            if glyph in widths:
                actual = recs[i][0] * 1000 / 2**20
                if abs(actual - widths[glyph]) > 1:
                    wrong_width.append((i, glyph, round(actual, 3), widths[glyph]))
        family = 'TS1' if enc.startswith('tcx') else 'T1'
        groups[(family, missing, no_outline, surplus, tuple(wrong_width))].append(name)

    selections = 0
    for path in sorted((ROOT / 'tex').glob('*.fd')):
        for prefix, quoted in re.findall(r'\\newtxtt@@scale\s+(\w+)\\newtxtt@@fig(\\newtxtt@@upq)?', path.read_text()):
            for z in 'abcde':
                for q in ('', 'q') if quoted else ('',):
                    name = prefix + z + q
                    selections += 1
                    if name not in metrics or name not in maps:
                        errors.append(f'{path.name}: unresolved font selection {name}')

    print(f'TFM files: {len(metrics)}; encoding vectors: {len(vectors)}; Type 1 fonts: {len(fonts)}')
    print(f'Unique map entries: {len(maps)}; direct FD selections: {selections}')
    print('Unmapped TFM files: ' + (', '.join(sorted(metrics.keys() - maps.keys())) or 'none'))
    print('Unreferenced encoding files: ' + (', '.join(sorted(vectors.keys() - used_vectors)) or 'none'))
    print('Unreferenced Type 1 fonts: ' + (', '.join(sorted(fonts.keys() - used_fonts)) or 'none'))
    inconsistent = 0
    for (family, missing, no_outline, surplus, wrong_width), names in sorted(groups.items()):
        print(f'{family}: {len(names)} mapped metrics')
        if not (missing or no_outline or surplus or wrong_width):
            print('  All encoded glyphs and metric advance widths agree.')
            continue
        inconsistent += len(names)
        for label, values in (('encoded slots without metrics', missing),
                              ('encoded slots without outlines', no_outline),
                              ('metric slots without encoding', surplus),
                              ('advance width mismatches', wrong_width)):
            if values:
                print(f'  {label}: {values}')
    if args.reference:
        compare_reference(args.reference, metrics, fonts, errors)
    for error in errors:
        print('ERROR:', error)
    print(f'{inconsistent} mapped metrics with discrepancies; {len(errors)} other errors.')
    return bool(inconsistent or errors)


if __name__ == '__main__':
    raise SystemExit(main())
