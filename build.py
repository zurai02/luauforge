#!/usr/bin/env python3
"""Bundle LuauForge into ONE self-contained dist/index.html.

The result needs no folders, works when double-clicked, and works on GitHub Pages.
It embeds the CSS, all JavaScript (as a classic script, no ES modules) and the kb/*.md files.
Run:  python3 build.py
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent
ORDER = ['md', 'lint', 'kb', 'memory', 'llm', 'app']  # dependency order


def convert(name: str) -> str:
    src = (ROOT / 'js' / f'{name}.js').read_text()
    exports = re.findall(r'^export\s+(?:async\s+)?(?:const|let|function\*?|class)\s+(\w+)', src, flags=re.M)

    def import_repl(m):
        clause, mod = m.group(1).strip(), m.group(2)
        target = '__m_' + Path(mod).stem
        ns = re.match(r'\*\s+as\s+(\w+)', clause)
        if ns:
            return f'const {ns.group(1)} = {target};'
        return f'const {clause} = {target};'

    src = re.sub(r"^import\s+(.+?)\s+from\s+'(\./[\w.]+)';?\s*$", import_repl, src, flags=re.M)
    src = re.sub(r'^export\s+', '', src, flags=re.M)
    assert not re.search(r'^\s*(import|export)\s', src, flags=re.M), f'unconverted module syntax in {name}.js'
    ret = ', '.join(exports)
    return f'const __m_{name} = (() => {{\n{src}\nreturn {{ {ret} }};\n}})();\n'


def main():
    bundle = "'use strict';\n" + '\n'.join(convert(n) for n in ORDER)
    bundle = bundle.replace('</script', '<\\/script')

    kb = {f'kb/{p.name}': p.read_text() for p in sorted((ROOT / 'kb').glob('*.md'))}
    kb_json = json.dumps(kb).replace('</', '<\\/')

    html = (ROOT / 'index.html').read_text()
    css = (ROOT / 'style.css').read_text()
    html = html.replace('<link rel="stylesheet" href="style.css">', f'<style>\n{css}\n</style>')
    mod = '<script type="module" src="js/app.js"></script>'
    assert mod in html, 'module script tag not found in index.html'
    html = html.replace(
        mod,
        f'<script>window.__LUAUFORGE_KB__ = {kb_json};</script>\n<script>\n{bundle}\n</script>',
    )
    out = ROOT / 'dist' / 'index.html'
    out.parent.mkdir(exist_ok=True)
    out.write_text(html)
    print(f'wrote {out} ({out.stat().st_size // 1024} KB, {len(kb)} kb files embedded)')


if __name__ == '__main__':
    main()
