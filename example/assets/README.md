# Fonts

The renderer needs one CJK-capable font with Korean coverage. None is committed to
this repository.

```bash
bash assets/fetch-font.sh          # downloads Noto Sans CJK KR into assets/
# or
export EXPLAINER_FONT=/abs/path/to/your-font.otf
```

Resolution order used by `drawlib.font_path()`:

1. `$EXPLAINER_FONT`
2. `assets/NotoSansCJKkr-Regular.otf`
3. the first `.otf`/`.ttf` found in `assets/`

## Licensing

- Noto Sans CJK is distributed under the SIL Open Font License 1.1. Keep its licence
  file next to it in any package you ship (`assets/font-license.txt`).
- Do not ship a commercial font you have not licensed for redistribution, and never
  extract a font out of a document you were given — bundling the font is a separate
  right from reading the document.
- If you publish the output, the font licence and the content licence are separate
  obligations. Check both.
