"""Собирает самодостаточный index.html из source/index.dev.html.

Запуск (из корня репозитория):
    npm i esbuild react@18 react-dom@18 @supabase/supabase-js@2   # один раз, в папке source/
    python3 source/build.py
"""
import re, subprocess, pathlib

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
NM = HERE / 'node_modules'

src = (HERE / 'index.dev.html').read_text(encoding='utf-8')
m = re.search(r'<script type="text/babel"[^>]*>(.*?)</script>', src, re.S)
(HERE / '_app.jsx').write_text(m.group(1), encoding='utf-8')
(HERE / '_sb.js').write_text("import { createClient } from '@supabase/supabase-js'; window.supabase = { createClient };", encoding='utf-8')

esb = str(NM / '.bin' / 'esbuild')
subprocess.run([esb, str(HERE / '_app.jsx'), '--loader:.jsx=jsx', '--minify', '--target=es2017', '--outfile=' + str(HERE / '_app.js'), '--log-level=warning'], check=True)
subprocess.run([esb, str(HERE / '_sb.js'), '--bundle', '--minify', '--format=iife', '--target=es2017', '--outfile=' + str(HERE / '_sb.out.js'), '--log-level=warning'], check=True)

def inline(path):
    return '<script>' + pathlib.Path(path).read_text(encoding='utf-8').replace('</script', '<\\/script') + '</script>'

guard = """<script>window.addEventListener('error',function(e){var r=document.getElementById('root');if(r&&r.querySelector('.boot'))r.innerHTML='<div class="boot" style="font-size:18px;padding:20px;text-align:center">Не удалось запустить приложение: '+(e.message||'ошибка')+'</div>';});</script>"""
body = '\n'.join([guard,
                  inline(NM / 'react/umd/react.production.min.js'),
                  inline(NM / 'react-dom/umd/react-dom.production.min.js'),
                  inline(HERE / '_sb.out.js'),
                  inline(HERE / '_app.js')])

out = re.sub(r'<script src="https://unpkg.com[^"]+"[^>]*></script>\n', '', src)
out = out.replace(m.group(0), body)
(ROOT / 'index.html').write_text(out, encoding='utf-8')
for f in ['_app.jsx', '_app.js', '_sb.js', '_sb.out.js']:
    (HERE / f).unlink()
print('index.html:', len(out) // 1024, 'KB')
