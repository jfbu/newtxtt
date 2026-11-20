#!/usr/bin/env python3
"""Restore TS1 glyphs already present in the Type 1 outlines.

Requires Python 3 and fontTools. Run from the repository root; rerunning
is harmless. Existing TFM character records and dimension tables are kept
byte-for-byte, so this does not perturb the metrics of any existing glyph.
"""

from pathlib import Path
import re
import struct

from fontTools import t1Lib
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.transformPen import TransformPen


ROOT = Path(__file__).resolve().parents[1] / 'newtxtt'
SLOTS = dict(enumerate(('grave', 'acute', 'circumflex', 'tilde',
                        'dieresis', 'hungarumlaut', 'ring', 'caron',
                        'breve', 'macron', 'dotaccent')))
SLOTS.update({21: 'endash', 22: 'emdash', 130: 'aciiacutedbl',
              160: 'guillbracketleft', 161: 'guillbracketright'})


def restore_vector(path):
    text = path.read_text()
    start, end = text.index('[') + 1, text.index(']')
    slots = iter(range(256))

    def replace(match):
        slot = next(slots)
        name = match.group()[1:]
        if slot not in SLOTS:
            return match.group()
        if name not in ('.notdef', SLOTS[slot]):
            raise ValueError(f'{path}: unexpected glyph {name} at slot {slot}')
        return '/' + SLOTS[slot]

    body = re.sub(r'/[^\s/]+', replace, text[start:end])
    if next(slots, None) is not None:
        raise ValueError(f'{path}: incomplete encoding vector')
    return (text[:start] + body + text[end:]).encode()


def glyph_dimensions(pfb, slant):
    glyphs = t1Lib.T1Font(str(pfb)).getGlyphSet()
    result = {}
    for slot, name in SLOTS.items():
        glyph = glyphs[name]
        pen = BoundsPen(glyphs)
        glyph.draw(TransformPen(pen, (1, 0, slant, 1, 0, 0)))
        _, bottom, right, top = pen.bounds
        result[slot] = (glyph.width, max(0, top), max(0, -bottom),
                        max(0, right - glyph.width))
    return result


def restore_tfm(path, dimensions):
    data = path.read_bytes()
    lengths = list(struct.unpack_from('>12H', data))
    lf, lh, bc, ec, nw, nh, nd, ni, nl, nk, ne, np = lengths
    if lf * 4 != len(data) or (nl, nk, ne) != (0, 0, 0):
        raise ValueError(f'{path}: unexpected TFM structure')
    offset = 24 + 4 * lh
    table = offset + 4 * (ec - bc + 1)
    info = bytearray(4 * bc) + bytearray(data[offset:table])
    tables = []
    pos = table
    for count in (nw, nh, nd, ni):
        tables.append(struct.unpack_from(f'>{count}i', data, pos))
        pos += 4 * count

    for slot, dims in dimensions.items():
        indices = []
        for dim, values in zip(dims, tables):
            target = dim * 2**20 / 1000
            # A zero-width index denotes a missing character, not a real glyph.
            start = 1 if not indices else 0
            index = min(range(start, len(values)), key=lambda i: abs(values[i] - target))
            error = abs(values[index] - target) * 1000 / 2**20
            if error > (1 if not indices else 11):
                raise ValueError(f'{path}: excessive quantization at slot {slot}: {error}')
            indices.append(index)
        width, height, depth, italic = indices
        record = bytes((width, (height << 4) | depth, italic << 2, 0))
        previous = info[4 * slot:4 * slot + 4]
        if previous not in (bytes(4), record):
            raise ValueError(f'{path}: refusing to overwrite existing slot {slot}')
        info[4 * slot:4 * slot + 4] = record

    # Extend the character table down to slot 0. All other table bytes,
    # including the header, checksum and font dimensions, are unchanged.
    lengths[0] += bc
    lengths[2] = 0
    return struct.pack('>12H', *lengths) + data[24:offset] + info + data[table:]


def main():
    outputs = {}
    for style in 'abcde':
        path = ROOT / 'enc' / f'tcx{style.upper()}ec.enc'
        outputs[path] = restore_vector(path)
    for prefix, pfb, slant in (
        ('newtcxtt', 'newtcxtt', 0), ('newtcxsl', 'newtcxtt', .167),
        ('newtcxbtt', 'newtcxbtt', 0), ('newtcxbsl', 'newtcxbtt', .167),
    ):
        dimensions = glyph_dimensions(ROOT / 'type1' / f'{pfb}.pfb', slant)
        for style in 'abcde':
            path = ROOT / 'tfm' / f'{prefix}{style}.tfm'
            outputs[path] = restore_tfm(path, dimensions)
    changed = 0
    for path, content in outputs.items():
        if path.read_bytes() != content:
            path.write_bytes(content)
            changed += 1
    print(f'{changed} files changed; {len(SLOTS)} slots restored.')


if __name__ == '__main__':
    main()
