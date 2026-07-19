import codecs
import re

with codecs.open('core/coreapp/static/coreapp/js/main.js', 'r', 'utf-8') as f:
    js = f.read()

# 1. Null-safe btnResetScan event listener
# btnResetScan.addEventListener('click', (e) => {
#    ...
# });
js = re.sub(
    r'(btnResetScan\.addEventListener\(\'click\',.*?\}\);)',
    r'if (btnResetScan) { \1 }',
    js,
    flags=re.DOTALL
)

# 2. Null-safe laserLine
js = js.replace("laserLine.classList.remove('hidden');", "if (laserLine) laserLine.classList.remove('hidden');")
js = js.replace("laserLine.classList.add('hidden');", "if (laserLine) laserLine.classList.add('hidden');")

with codecs.open('core/coreapp/static/coreapp/js/main.js', 'w', 'utf-8') as f:
    f.write(js)

print("Runtime errors fixed in main.js")
