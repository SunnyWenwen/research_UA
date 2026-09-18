#!/usr/bin/env python3
"""由 artifact 原始檔產生可獨立開啟／列印的 HTML。

artifact 平台會自動包上 <!doctype html> / <head> / <body> 骨架，
所以 kg-comparison.artifact.html 本身沒有那一層。這支腳本補上骨架
與列印樣式，產出可以雙擊開啟、也可以匯出 A4 橫式 PDF 的單一檔案。

用法：
    python3 docs/src/build-standalone.py
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "docs" / "src" / "kg-comparison.artifact.html"
OUT = ROOT / "docs" / "kg-comparison.html"

HEAD = '''<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
'''

RESET = '''
<style>
:root{color-scheme:light dark}
body{margin:0}img{max-width:100%}[hidden]{display:none!important}
@media print{
  @page{size:A4 landscape;margin:11mm}
  :root{--paper:#fff;--surface:#fff;--surface-2:#f2f5f6;--ink:#111;--ink-2:#333;--ink-3:#666;--rule:#ccc;--rule-strong:#999}
  body{background:#fff;font-size:9.5pt}
  .wrap{max-width:none;padding:0}
  .scroller{overflow:visible;border:1px solid #999}
  table{min-width:0;font-size:8pt}table.wide5{min-width:0}
  thead th{position:static;background:#f2f5f6}
  section,.verdict,.trap,.flow,.key,.alarm,.steps,.ladder,.chain{break-inside:avoid;page-break-inside:avoid}
  section{margin-top:26px}header{padding-block:0 12px}
  h3.sub{margin-top:24px}
  tbody tr{break-inside:avoid;page-break-inside:avoid}
  a{text-decoration:none;color:inherit}
}
</style>
'''

MARKER = '</style>\n\n<div class="wrap">'


def main() -> None:
    src = SRC.read_text(encoding="utf-8")
    if MARKER not in src:
        raise SystemExit(f"找不到分隔標記，來源檔格式可能已改變：{SRC}")
    head, body = src.split(MARKER, 1)
    OUT.write_text(
        HEAD + head + "</style>\n" + RESET
        + '</head>\n<body>\n<div class="wrap">' + body
        + "\n</body>\n</html>\n",
        encoding="utf-8",
    )
    print(f"寫入 {OUT.relative_to(ROOT)}（{OUT.stat().st_size:,} bytes）")


if __name__ == "__main__":
    main()
