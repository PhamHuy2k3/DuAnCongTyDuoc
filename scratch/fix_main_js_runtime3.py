import codecs
import re

with codecs.open('core/coreapp/static/coreapp/js/main.js', 'r', 'utf-8') as f:
    js = f.read()

# Make fileLoadedView null safe
js = js.replace("fileLoadedView.classList", "if (fileLoadedView) fileLoadedView.classList")
# Make loadedFileName null safe
js = js.replace("loadedFileName.textContent", "if (loadedFileName) loadedFileName.textContent")

# Make sim-content null safe
js = re.sub(
    r'(document\.getElementById\(\'sim-content-[^\']+\'\))\.textContent\s*=\s*([^;]+);',
    r'if (\1) \1.textContent = \2;',
    js
)

with codecs.open('core/coreapp/static/coreapp/js/main.js', 'w', 'utf-8') as f:
    f.write(js)

print("Runtime errors 3 fixed in main.js")
