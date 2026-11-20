#!/usr/bin/env python3
"""Complete T1 slot 23 in the existing font distribution.

Requires Python 3, fontTools and t1utils, as does add-ts1-wordmarks.py.
The encoding vectors already name /cwm. Supply its empty Type 1
charstring and a zero-width TFM record with x-height and zero depth.
Preserve all existing character records, metric tables and font parameters.
Rerunning is harmless.
"""

from pathlib import Path
import re
import runpy
import struct


TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent / 'newtxtt'
add_outline = runpy.run_path(str(TOOLS / 'add-ts1-wordmarks.py'))['add_outline']


def add_metric(path):
    data = path.read_bytes()
    lengths = list(struct.unpack_from('>12H', data))
    lf, lh, bc, ec, nw, nh, nd, ni, nl, nk, ne, np = lengths
    if lf * 4 != len(data) or not bc <= 23 <= ec or np < 5:
        raise ValueError(f'{path}: unexpected metric structure')
    start = 24 + 4 * lh
    table = start + 4 * (ec - bc + 1)
    info = bytearray(data[start:table])
    widths = struct.unpack_from(f'>{nw}i', data, table)
    height_start = table + 4 * nw
    heights = struct.unpack_from(f'>{nh}i', data, height_start)
    # EC's compound word mark has the font's x-height, not cap height.
    xheight = struct.unpack_from('>i', data, len(data) - 4 * np + 16)[0]
    hi = min(range(1, nh), key=lambda i: abs(heights[i] - xheight))
    if abs(heights[hi] - xheight) * 1000 / 2**20 > 11:
        raise ValueError(f'{path}: excessive height quantization')
    # Index zero means absent; an additional zero entry is a real glyph.
    wi = next((i for i in range(1, nw) if widths[i] == 0), None)
    width_bytes = data[table:height_start]
    if wi is None:
        if nw >= 256:
            raise ValueError(f'{path}: no room for a zero-advance width')
        wi = nw
        width_bytes += bytes(4)
        lengths[0] += 1
        lengths[4] += 1
    record = bytes((wi, hi << 4, 0, 0))
    pos = 4 * (23 - bc)
    if info[pos:pos + 4] not in (bytes(4), record):
        raise ValueError(f'{path}: unexpected existing slot 23')
    info[pos:pos + 4] = record
    return (struct.pack('>12H', *lengths) + data[24:start] + info
            + width_bytes + data[height_start:])


def main():
    outputs = {}
    metrics, fonts, vectors = set(), set(), set()
    for line in (ROOT / 'map' / 'newtxtt.map').read_text().splitlines():
        enc = re.search(r'<\[(txtt[^\s]+\.enc)', line)
        if not enc:
            continue
        pfb = re.search(r'<([^\s]+\.pfb)', line)
        if not pfb:
            raise ValueError(f'invalid map entry: {line}')
        metrics.add(ROOT / 'tfm' / (line.split()[0] + '.tfm'))
        fonts.add(ROOT / 'type1' / pfb[1])
        vectors.add(ROOT / 'enc' / enc[1])
    if (len(metrics), len(fonts), len(vectors)) != (120, 4, 10):
        raise ValueError('unexpected T1 map inventory')
    for path in sorted(vectors):
        text = re.sub(r'%[^\n]*', '', path.read_text())
        glyphs = re.findall(r'/([^\s/]+)', text.split('[', 1)[1].split(']', 1)[0])
        if len(glyphs) != 256 or glyphs[23] != 'cwm':
            raise ValueError(f'{path}: slot 23 must already name cwm')
    for path in sorted(fonts):
        outputs[path] = add_outline(path)
    for path in sorted(metrics):
        outputs[path] = add_metric(path)
    changed = 0
    for path, content in outputs.items():
        if path.read_bytes() != content:
            path.write_bytes(content)
            changed += 1
    print(f'{changed} files changed; T1 wordmark present in {len(metrics)} metrics.')


if __name__ == '__main__':
    main()
