#!/usr/bin/env python3
"""Add the two TS1 zero-advance compound-word marks.

Requires Python 3, fontTools, t1disasm and t1asm. Both slots use the
same empty /cwm outline (Unicode U+200C); their TFM heights differ.
The existing glyph programs, metric records and font dimensions are
preserved. Run from the repository root; rerunning is harmless.
"""

from pathlib import Path
import re
import struct
import subprocess

from fontTools import t1Lib
from fontTools.pens.boundsPen import BoundsPen


ROOT = Path(__file__).resolve().parents[1] / 'newtxtt'
SLOTS = (23, 31)


def add_outline(path):
    data = path.read_bytes()
    source = subprocess.check_output(['t1disasm'], input=data)
    if re.search(rb'^/cwm \{', source, re.M):
        if not re.search(rb'^/cwm \{\s*0 0 hsbw\s*endchar\s*\}', source, re.M):
            raise ValueError(f'{path}: unexpected existing cwm')
        return data
    pattern = rb'(/CharStrings )(\d+)( dict dup begin\n)'
    def replace(match):
        return (match[1] + str(int(match[2]) + 1).encode() + match[3]
                + b'/cwm {\n\t0 0 hsbw\n\tendchar\n\t} ND\n')
    expected, count = re.subn(pattern, replace, source)
    if count != 1:
        raise ValueError(f'{path}: unexpected CharStrings dictionary')
    result = subprocess.check_output(['t1asm', '-b'], input=expected)
    if subprocess.check_output(['t1disasm'], input=result) != expected:
        raise ValueError(f'{path}: Type 1 reassembly did not preserve source')
    return result


def add_vector(path):
    text = path.read_text()
    start, end = text.index('[') + 1, text.index(']')
    slots = iter(range(256))
    def replace(match):
        slot = next(slots)
        if slot not in SLOTS:
            return match[0]
        if match[0] not in ('/.notdef', '/cwm'):
            raise ValueError(f'{path}: unexpected glyph at {slot}')
        return '/cwm'
    body = re.sub(r'/[^\s/]+', replace, text[start:end])
    if next(slots, None) is not None:
        raise ValueError(f'{path}: incomplete encoding vector')
    return (text[:start] + body + text[end:]).encode()


def wordmark_heights(path):
    glyphs = t1Lib.T1Font(str(path)).getGlyphSet()
    heights = []
    for name in ('A', 'h'):
        pen = BoundsPen(glyphs)
        glyphs[name].draw(pen)
        heights.append(pen.bounds[3])
    return heights


def add_metrics(path, heights):
    data = path.read_bytes()
    lengths = list(struct.unpack_from('>12H', data))
    lf, lh, bc, ec, nw, nh, *_ = lengths
    if lf * 4 != len(data) or bc > min(SLOTS) or ec < max(SLOTS):
        raise ValueError(f'{path}: unexpected TFM structure')
    offset = 24 + 4 * lh
    table = offset + 4 * (ec - bc + 1)
    info = bytearray(data[offset:table])
    widths = struct.unpack_from(f'>{nw}i', data, table)
    ht_table = table + 4 * nw
    ht_values = struct.unpack_from(f'>{nh}i', data, ht_table)
    # Width index zero means absent; a second zero represents a real glyph.
    index = next((i for i in range(1, nw) if widths[i] == 0), None)
    width_bytes = data[table:ht_table]
    if index is None:
        if nw >= 256:
            raise ValueError(f'{path}: no room for a zero-advance width')
        index = nw
        width_bytes += bytes(4)
        lengths[0] += 1
        lengths[4] += 1
    for slot, height in zip(SLOTS, heights):
        target = height * 2**20 / 1000
        hi = min(range(1, nh), key=lambda i: abs(ht_values[i] - target))
        error = abs(ht_values[hi] - target) * 1000 / 2**20
        if error > 11:
            raise ValueError(f'{path}: excessive height quantization: {error}')
        record = bytes((index, hi << 4, 0, 0))
        pos = 4 * (slot - bc)
        if info[pos:pos + 4] not in (bytes(4), record):
            raise ValueError(f'{path}: unexpected existing slot {slot}')
        info[pos:pos + 4] = record
    return (struct.pack('>12H', *lengths) + data[24:offset] + info
            + width_bytes + data[ht_table:])


def main():
    outputs = {}
    for font in ('newtcxtt', 'newtcxbtt'):
        path = ROOT / 'type1' / f'{font}.pfb'
        outputs[path] = add_outline(path)
    for style in 'abcde':
        path = ROOT / 'enc' / f'tcx{style.upper()}ec.enc'
        outputs[path] = add_vector(path)
    for prefix, text_font in (('newtcxtt', 'newtxtt'), ('newtcxsl', 'newtxtt'),
                              ('newtcxbtt', 'newtxbtt'), ('newtcxbsl', 'newtxbtt')):
        heights = wordmark_heights(ROOT / 'type1' / f'{text_font}.pfb')
        for style in 'abcde':
            path = ROOT / 'tfm' / f'{prefix}{style}.tfm'
            outputs[path] = add_metrics(path, heights)
    changed = 0
    for path, content in outputs.items():
        if path.read_bytes() != content:
            path.write_bytes(content)
            changed += 1
    print(f'{changed} files changed; two TS1 wordmarks added.')


if __name__ == '__main__':
    main()
