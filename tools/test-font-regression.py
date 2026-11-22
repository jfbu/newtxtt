#!/usr/bin/env python3
"""Exercise newtxtt with pdfLaTeX, checking actual PDF font and glyph selection.

Requires Python 3, pypdf, and a working pdfLaTeX installation with T1/TS1.
Uses the checkout, not installed newtxtt files.
Generate fixtures explicitly: python3 tools/test-font-regression.py --generate
Run checked-in fixtures: python3 tools/test-font-regression.py
Sources, expectations and textual results are retained under tests/.

U+2260 (not equal) is not a T1 or TS1 text symbol; it is outside this test.
In pdfLaTeX it can be represented by the math command \\ensuremath{\\neq}.
"""

import argparse
import json
import os
from pathlib import Path
import re
import subprocess

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1] / 'newtxtt'
TESTS = ROOT.parent / 'tests'
SHAPES = [('m', 'n', 'newtcxtt'), ('m', 'sl', 'newtcxsl'),
          ('b', 'n', 'newtcxbtt'), ('b', 'sl', 'newtcxbsl')]
# Check the character semantics independently of the distributed encoding names.
UNICODE = {96: '`', 136: '•', 169: '©', 177: '±', 130: '˝',
           160: '⁅', 161: '⁆', 144: '₲', 171: '🄯', 134: '‖',
           32: '␢', 91: '⟦', 93: '⟧', 45: '⹀', 79: '◯',
           98: '*', 99: '⚮', 100: '†', 109: '⚭', 126: '˷',
           127: '⹀', 128: '˘', 129: 'ˇ', 131: '˵', 143: '₦',
           145: '₱', 147: '℞', 153: '¶', 154: '฿', 156: '⁒',
           159: '℠', 168: '¨', 173: '℗', 175: '¯', 180: '´'}


def environment():
    env = os.environ.copy()
    for var, directory in [('TEXINPUTS', 'tex'), ('TFMFONTS', 'tfm'),
                           ('T1FONTS', 'type1'), ('ENCFONTS', 'enc'),
                           ('TEXFONTMAPS', 'map')]:
        env[var] = str(ROOT / directory) + os.pathsep + env.get(var, '') + os.pathsep
    return env


def cases(env):
    kernel = subprocess.check_output(['kpsewhich', 'ts1enc.def'], env=env, text=True).strip()
    if not kernel:
        raise RuntimeError('Cannot locate ts1enc.def')
    declarations = re.findall(r'\\DeclareText(Symbol|Accent)\s*\{(\\\w+)\}\{TS1\}\{(\d+)\}',
                              Path(kernel).read_text())
    if not set(UNICODE).issubset({int(slot) for _, _, slot in declarations}):
        raise RuntimeError(f'Unexpected TS1 declarations in {kernel}')
    result = []
    for kind, command, slot in declarations:
        slot = int(slot)
        # T1 has its own definitions for these symbols; exercise TS1 explicitly.
        expression = (r'\UseTextSymbol{TS1}{' + command + '}'
                      if slot in (36, 163, 167) else command)
        if kind == 'Accent':
            expression += '{OO}' if slot in (26, 27, 28, 29) else '{A}'
        result.append((command, expression, slot, UNICODE.get(slot)))
    result.extend([(r'\capitalcedilla', r'\capitalcedilla{A}', 11, None),
                   (r'\capitalogonek', r'\capitalogonek{A}', 12, None),
                   (r'\textasteriskcentered', r'\textasteriskcentered', 42, None),
                   (r'\textcircled', r'\textcircled{A}', 79, None)])
    return result


def glyphs(page):
    """Return (TFM name, encoded byte) pairs from actual PDF text operations."""
    fonts = page['/Resources']['/Font']
    metric = None
    for operands, operator in page.get_contents().operations:
        if operator == b'Tf':
            font = fonts[operands[0]].get_object()
            cmap = font['/ToUnicode'].get_data().decode('ascii')
            match = re.search(r'/Ordering \(([^)]+)\)', cmap)
            metric = match.group(1).split('-')[0] if match else ''
        elif operator in (b'Tj', b'TJ'):
            strings = operands[0] if operator == b'TJ' else operands
            for string in strings:
                if hasattr(string, 'original_bytes'):
                    yield from ((metric, byte) for byte in string.original_bytes)


def generate_case(family, zero, quotes, tests):
    option = family + ',zerostyle=' + zero + (',straightquotes' if quotes else '')
    source = [r'\pdfmapfile{=newtxtt.map}', r'\input{glyphtounicode.tex}', r'\documentclass{article}',
              r'\usepackage[TS1,T1]{fontenc}', r'\usepackage[' + option + r']{newtxtt}',
              r'\usepackage{upquote}', r'\pdfgentounicode=1', r'\tracinglostchars=3',
              r'\begin{document}', r'\begingroup\catcode58=13\catcode61=13',
              r'\shipout\hbox{\verb|`|}', r'\endgroup']
    # The first TS1 use must be in verbatim, before any normal TS1 selection.
    expected = [(r'\verb|`|', 'newtcxtt' + zero, 96, '`')]
    for series, shape, prefix in SHAPES:
        source.append(r'\normalfont\fontseries{' + series + r'}\fontshape{' + shape + r'}\selectfont')
        for label, expression, slot, unicode in tests:
            source.append(r'\shipout\hbox{' + expression + '}')
            expected.append((label, prefix + zero, slot, unicode))
    # Exercise T1 compound word marks in all six distinct shapes.
    for series, base in [('m', 'newtxtt'), ('b', 'newtxbtt')]:
        base += 'z' if family == 'ttzdefault' else ''
        for shape, suffix in [('n', ''), ('sl', 'sl'), ('sc', 'sc')]:
            source.append(r'\normalfont\fontseries{' + series + r'}\fontshape{' + shape + r'}\selectfont')
            source.append(r'\shipout\hbox{A\textcompwordmark B}')
            expected.append((r'\textcompwordmark', base + suffix + zero + ('q' if quotes else ''), 23, None))
    source.extend([r'\normalfont\setcounter{page}{1}',
                   r'\begin{itemize}\item Item\end{itemize}', r'\end{document}'])
    name = 'newtxttz' if family == 'ttzdefault' else 'newtxtt'
    expected.append(('itemize', 'newtcxtt' + zero, 136, None))
    stem = f'generated-{family}-{zero}-{int(quotes)}'
    write_fixture(stem, source, name, True, expected)


def generate_direct_nfss(family):
    source = [r'\pdfmapfile{=newtxtt.map}', r'\input{glyphtounicode.tex}', r'\documentclass{article}',
              r'\usepackage[TS1,T1]{fontenc}', r'\pdfgentounicode=1', r'\tracinglostchars=3',
              r'\begin{document}', r'\shipout\hbox{\usefont{T1}{' + family + r'}{m}{n}\textcopyleft}',
              r'\end{document}']
    write_fixture('generated-direct-' + family, source, family, False,
                  [(r'\textcopyleft', 'newtcxtta', 171, '🄯')])


def write_fixture(stem, source, family, package, expected):
    (TESTS / (stem + '.tex')).write_text('\n'.join(source) + '\n', encoding='utf-8')
    # First line describes the FD requirements; remaining lines describe pages.
    records = [dict(family=family, package=package)] + expected
    (TESTS / (stem + '.expected')).write_text(
        ''.join(json.dumps(record, ensure_ascii=False) + '\n' for record in records),
        encoding='utf-8')


def generate(env):
    TESTS.mkdir(exist_ok=True)
    tests = cases(env)
    for family in ('ttdefault', 'ttzdefault'):
        for zero in 'abcde':
            for quotes in (False, True):
                generate_case(family, zero, quotes, tests)
    for family in ('newtxtt', 'newtxttz'):
        generate_direct_nfss(family)


def run_case(spec, env):
    stem = spec.stem
    metadata, *expected = [json.loads(line) for line in spec.read_text(encoding='utf-8').splitlines()]
    result = []
    errors = []
    proc = subprocess.run(['pdflatex', '-halt-on-error', '-interaction=nonstopmode',
                           '-recorder', stem + '.tex'], cwd=TESTS, env=env,
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if proc.returncode or re.search(r'Missing character|LaTeX Font Warning', proc.stdout):
        errors.append('Compilation failed or reported missing glyphs/font warnings')
    else:
        inputs = (TESTS / (stem + '.fls')).read_text().splitlines()
        paths = {(TESTS / line[6:]).resolve() for line in inputs if line.startswith('INPUT ')}
        family = metadata['family']
        required = ['t1' + family + '.fd', 'ts1' + family + '.fd', 'newtxtt-ts1-unicode.tex']
        if metadata['package']:
            required.append('newtxtt.sty')
        elif any(path.name == 'newtxtt.sty' for path in paths):
            errors.append('Direct NFSS test unexpectedly loaded newtxtt.sty')
        for filename in required:
            if ROOT / 'tex' / filename not in paths:
                errors.append('Did not load local ' + filename)
        reader = PdfReader(TESTS / (stem + '.pdf'))
        if len(reader.pages) != len(expected):
            errors.append(f'Expected {len(expected)} pages, got {len(reader.pages)}')
        for number, (page, (label, metric, slot, unicode)) in enumerate(zip(reader.pages, expected), 1):
            actual = list(glyphs(page))
            extracted = page.extract_text().strip() if unicode is not None else None
            result.append(json.dumps([number, label, actual, extracted], ensure_ascii=False))
            if (metric, slot) not in actual or (not metadata['package'] and actual != [(metric, slot)]):
                errors.append(f'Page {number}: {label}: expected {metric}/{slot}, got {actual}')
            if unicode is not None and extracted != unicode:
                errors.append(f'Page {number}: {label}: incorrect Unicode {extracted!r}')
    result.extend('FAIL: ' + error for error in errors)
    (TESTS / (stem + '.txt')).write_text('\n'.join(result) + '\n', encoding='utf-8')
    if errors:
        print(f'{stem}: FAILED (see tests/{stem}.txt and .log)', flush=True)
    else:
        print(f'{stem}: passed', flush=True)
    return not errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--generate', action='store_true', help='regenerate test sources and expectations only')
    args = parser.parse_args()
    env = environment()
    if args.generate:
        generate(env)
        return
    specs = sorted(TESTS.glob('generated-*.expected'))
    if not specs:
        raise RuntimeError('No checked-in tests found; run --generate explicitly')
    results = [run_case(spec, env) for spec in specs]
    print(f'{sum(results)}/{len(results)} generated test documents passed.')
    if not all(results):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
