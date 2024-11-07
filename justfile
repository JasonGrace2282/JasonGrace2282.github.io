live:
  sphinx-autobuild . build/html/

html:
  sphinx-build -M html . build/

build-strict:
  sphinx-build -M html . build/ -n -W
