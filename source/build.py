import re, subprocess, pathlib
src = pathlib.Path('/home/claude/05/index.html').read_text()
m = re.search(r'<script type="text/babel"[^>]*>(.*?)</script>', src, re.S)
jsx = m.group(1)
pathlib.Path('app.jsx').write_text(jsx)
subprocess.run(['npx','esbuild','app.jsx','--loader:.jsx=jsx','--minify','--target=es2017','--outfile=app.js','--log-level=warning'], check=True)
js = pathlib.Path('app.js').read_text().replace('</script','<\\/script')
react = pathlib.Path('node_modules/react/umd/react.production.min.js').read_text()
rdom = pathlib.Path('node_modules/react-dom/umd/react-dom.production.min.js').read_text()
# remove CDN scripts
out = re.sub(r'<script src="https://unpkg.com[^"]+"[^>]*></script>\n', '', src)
guard = """window.addEventListener('error',function(e){var r=document.getElementById('root');if(r&&r.querySelector('.boot'))r.innerHTML='<div class="boot" style="font-size:18px;padding:20px;text-align:center">Не удалось запустить приложение: '+(e.message||'ошибка')+'</div>';});"""
body = f"<script>{guard}</script>\n<script>{react}</script>\n<script>{rdom}</script>\n<script>{js}</script>"
out = out[:m.start()] + body + out[m.end():] if False else out.replace(m.group(0), body)
pathlib.Path('/home/claude/05/index.html').write_text(out)
print(len(out)//1024,'KB')
