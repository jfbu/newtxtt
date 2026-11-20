#!/usr/bin/env python3
"""Exercise newtxtt with pdfLaTeX, checking actual PDF font and glyph selection.

Requires Python 3, pypdf, and a working pdfLaTeX installation with T1/TS1.
Runs in temporary directories; uses the checkout, not installed newtxtt files.
Run from the repository root: python3 tools/test-latex.py

U+2260 (not equal) is not a T1 or TS1 text symbol; it is outside this test.
In pdfLaTeX it can be represented by the math command \\ensuremath{\\neq}.
"""

import os
from pathlib import Path
import re
import subprocess
import tempfile

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1] / 'newtxtt'
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


def run_case(directory, env, family, zero, quotes, tests):
    option = family + ',zerostyle=' + zero + (',straightquotes' if quotes else '')
    source = [r'\pdfmapfile{=newtxtt.map}', r'\input{glyphtounicode.tex}', r'\documentclass{article}',
              r'\usepackage[TS1,T1]{fontenc}', r'\usepackage[' + option + r']{newtxtt}',
              r'\pdfgentounicode=1', r'\tracinglostchars=3', r'\begin{document}']
    expected = []
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
    (directory / 'test.tex').write_text('\n'.join(source) + '\n')
    proc = subprocess.run(['pdflatex', '-halt-on-error', '-interaction=nonstopmode',
                           '-recorder', 'test.tex'], cwd=directory, env=env,
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if proc.returncode or re.search(r'Missing character|LaTeX Font Warning', proc.stdout):
        raise RuntimeError(option + '\n' + proc.stdout)
    # Ensure the package and both encoding-specific FD selections are local.
    inputs = (directory / 'test.fls').read_text().splitlines()
    name = 'newtxttz' if family == 'ttzdefault' else 'newtxtt'
    for filename in ('newtxtt.sty', 't1' + name + '.fd', 'ts1' + name + '.fd'):
        if not any(line.startswith('INPUT ') and Path(line[6:]).resolve() == ROOT / 'tex' / filename
                   for line in inputs):
            raise RuntimeError(f'{option}: did not load local {filename}')
    reader = PdfReader(directory / 'test.pdf')
    if len(reader.pages) != len(expected) + 1:
        raise RuntimeError(f'{option}: unexpected page count')
    for page, (label, metric, slot, unicode) in zip(reader.pages, expected):
        actual = list(glyphs(page))
        if (metric, slot) not in actual:
            raise RuntimeError(f'{option}: {label}: expected {metric}/{slot}, got {actual}')
        if unicode is not None and page.extract_text().strip() != unicode:
            raise RuntimeError(f'{option}: {label}: incorrect Unicode {page.extract_text()!r}')
    if ('newtcxtt' + zero, 136) not in list(glyphs(reader.pages[-1])):
        raise RuntimeError(f'{option}: itemize did not select the companion bullet')
    return len(expected)


def main():
    env = environment()
    tests = cases(env)
    count = 0
    with tempfile.TemporaryDirectory(prefix='newtxtt-test-') as temp:
        directory = Path(temp)
        for family in ('ttdefault', 'ttzdefault'):
            for zero in 'abcde':
                for quotes in (False, True):
                    count += run_case(directory, env, family, zero, quotes, tests)
                    print(f'{family}, zerostyle={zero}, straightquotes={quotes}: passed', flush=True)
    print(f'{count - 120} TS1 command/shape checks, 120 T1 wordmark checks and 20 itemize checks passed.')


if __name__ == '__main__':
    main()
