# Optional SVG line-art kit

Transparent actor layers for an existing explainer renderer. The original ink and motion primitives are from [JDhruv14/line-art-animation](https://github.com/JDhruv14/line-art-animation) at `c43d698913cf0ad44f984c7ae14c5348010594d3`, MIT; see `LICENSE-line-art.txt`. No source documents, fonts, narration, or video are bundled.

## Capture a demo

From the repository root, with Python, Node 22.18+, esbuild, and Chrome/Chromium installed:

```sh
mkdir -p /path/to/demo
npx esbuild assets/line-art/review-actors.ts --bundle --format=esm --outfile=/path/to/demo/review-actors.js
cp assets/line-art/index.html /path/to/demo/index.html
python3 -m http.server 5187 --bind 127.0.0.1 --directory /path/to/demo
```

In a second terminal:

```sh
node assets/line-art/capture.ts 'http://127.0.0.1:5187/?debug' /path/to/demo/rgba 12 30 720 410
```

Set `CHROME` to a browser executable if needed. A frame count of `0` runs only the forward/reverse seek checks. Await `__render(t)` and use scene-local absolute time; do not reverse-integrate springs. See [the integration guide](../../references/line-art-pillow-hybrid.md) for layout, timing, and QA.
