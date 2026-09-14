"""Convierte docs/paper/draft.md a HTML y luego a PDF/DOCX con LibreOffice, para contar páginas.
Conversor mínimo (títulos, párrafos, listas, tablas, imágenes, negrita, cursiva, código). Solo stdlib.
Uso: python3 docs/paper/build.py   →  docs/paper/build/draft.html, draft.pdf, draft.docx
"""
import html, os, re, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'draft.md')
OUT = os.path.join(HERE, 'build')
os.makedirs(OUT, exist_ok=True)


def wid(src):
    return 420 if 'fig1' in src else 440 if 'fig3' in src else 520


def b64(src):
    import base64
    return base64.b64encode(open(src, 'rb').read()).decode()


def hgt(src):
    import struct
    with open(src, 'rb') as f:
        head = f.read(24)
    w, h = struct.unpack('>II', head[16:24])
    return h / w


def inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r'`([^`]+)`', r'<code>\1</code>', t)
    t = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', t)
    t = re.sub(r'(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])', r'<i>\1</i>', t)
    return t


def convert(md):
    md = re.sub(r'<!--.*?-->', '', md, flags=re.S)
    lines = md.split('\n')
    out, para, i = [], [], 0

    def flush():
        if para:
            out.append('<p>' + inline(' '.join(para)) + '</p>')
            para.clear()

    while i < len(lines):
        ln = lines[i]
        if not ln.strip():
            flush(); i += 1; continue
        m = re.match(r'^(#{1,4})\s+(.*)', ln)
        if m:
            flush(); n = len(m.group(1)); out.append(f'<h{n}>{inline(m.group(2))}</h{n}>'); i += 1; continue
        m = re.match(r'^!\[(.*?)\]\((.*?)\)', ln)
        if m:
            flush()
            src = os.path.normpath(os.path.join(HERE, m.group(2)))
            out.append(f'<p class="fig"><img src="data:image/png;base64,{b64(src)}" width="{wid(src)}" height="{int(wid(src)*hgt(src))}"></p>'); i += 1; continue
        if ln.startswith('|'):
            flush(); rows = []
            while i < len(lines) and lines[i].startswith('|'):
                cells = [c.strip() for c in lines[i].strip().strip('|').split('|')]
                if not all(re.fullmatch(r'-+', c) for c in cells):
                    rows.append(cells)
                i += 1
            t = '<table>' + '<tr>' + ''.join(f'<th>{inline(c)}</th>' for c in rows[0]) + '</tr>'
            for r in rows[1:]:
                t += '<tr>' + ''.join(f'<td>{inline(c)}</td>' for c in r) + '</tr>'
            out.append(t + '</table>'); continue
        if re.match(r'^(\s*)([-*]|\d+\.)\s+', ln):
            flush(); ordered = bool(re.match(r'^\s*\d+\.', ln)); items = []
            while i < len(lines) and lines[i].strip():
                if re.match(r'^(\s*)([-*]|\d+\.)\s+', lines[i]):
                    items.append(re.sub(r'^(\s*)([-*]|\d+\.)\s+', '', lines[i]))
                else:
                    items[-1] += ' ' + lines[i].strip()
                i += 1
            tag = 'ol' if ordered else 'ul'
            out.append(f'<{tag}>' + ''.join(f'<li>{inline(x)}</li>' for x in items) + f'</{tag}>'); continue
        if ln.strip() == '---':
            flush(); out.append('<hr>'); i += 1; continue
        para.append(ln.strip()); i += 1
    flush()
    return '\n'.join(out)


CSS = """
@page { size: 8.5in 11in; margin: 1in; }
body { font-family: Arial, 'Liberation Sans', sans-serif; font-size: 11pt; line-height: 1.15; }
h1 { font-size: 20pt; } h2 { font-size: 14pt; margin-top: 14pt; } h3 { font-size: 12pt; }
p { margin: 0 0 6pt 0; text-align: left; }
table { border-collapse: collapse; font-size: 9.5pt; margin: 4pt 0 8pt 0; }
td, th { border: 1px solid #999; padding: 2pt 4pt; vertical-align: top; }
p.fig img { width: 16cm; }
code { font-family: 'DejaVu Sans Mono', monospace; font-size: 9.5pt; }
"""


def main():
    body = convert(open(SRC, encoding='utf8').read())
    doc = f"<html><head><meta charset='utf-8'><style>{CSS}</style></head><body>{body}</body></html>"
    h = os.path.join(OUT, 'draft.html')
    open(h, 'w', encoding='utf8').write(doc)
    for fmt in ('pdf:writer_pdf_Export', 'docx:MS Word 2007 XML'):
        subprocess.run(['soffice', '--headless', '--infilter=HTML (StarWriter)', '--convert-to', fmt, '--outdir', OUT, h],
                       check=True, capture_output=True)
    print('ok', OUT)


if __name__ == '__main__':
    main()
