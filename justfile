live:
  sphinx-autobuild . build/html/

final:
  sphinx-build -M html . build/
