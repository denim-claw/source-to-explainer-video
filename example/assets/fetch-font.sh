#!/usr/bin/env bash
# Fetch an OFL Korean-capable font into assets/. Run once before the first render.
# The font is NOT committed to this repository; the licence travels with the file.
#   bash fetch-font.sh          Noto Sans CJK KR (all examples)
#   bash fetch-font.sh mono     Noto Sans Mono CJK KR (code panels in example-debugger)
set -euo pipefail
cd "$(dirname "$0")"
DIR="Sans/OTF/Korean"
OUT="NotoSansCJKkr-Regular.otf"
if [ "${1:-}" = "mono" ]; then
  DIR="Sans/Mono"
  OUT="NotoSansMonoCJKkr-Regular.otf"
fi
if [ -f "$OUT" ]; then
  echo "already present: $(pwd)/$OUT"
  exit 0
fi
URLS=(
  "https://raw.githubusercontent.com/notofonts/noto-cjk/main/$DIR/$OUT"
  "https://github.com/notofonts/noto-cjk/raw/main/$DIR/$OUT"
  "https://cdn.jsdelivr.net/gh/notofonts/noto-cjk@main/$DIR/$OUT"
)
for u in "${URLS[@]}"; do
  echo "trying $u"
  if curl -fSL --retry 2 --connect-timeout 15 -o "$OUT.part" "$u"; then
    python3 - "$OUT.part" <<'PY'
import sys, pathlib
from PIL import ImageFont
p = pathlib.Path(sys.argv[1])
f = ImageFont.truetype(str(p), 24)
f.getbbox('한글 테스트')
print('font OK:', p.stat().st_size, 'bytes')
PY
    mv "$OUT.part" "$OUT"
    echo "installed $(pwd)/$OUT"
    exit 0
  fi
done
rm -f "$OUT.part"
echo "download failed. Install any CJK-capable OFL font manually as assets/$OUT"
echo "or point EXPLAINER_FONT at an absolute font path and re-run."
exit 1
