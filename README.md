# research_UA

比較三套「程式碼知識圖譜」工具的研究筆記 —— 它們怎麼建圖、怎麼查圖，
以及全自動建出來的圖有哪些看不出來的缺失。

比較對象：

| 工具 | 出處 |
|---|---|
| Understand-Anything | `egonex-ai/understand-anything` |
| graphify | `graphify-labs/graphify` |
| codegraph | `colbymchenry/codegraph` |

每一項結論都對照過三套工具的原始碼；Oracle DDL 的部分是實際安裝解析器、
跑過真實語法後的結果。

---

## 主要文件

| 檔案 | 說明 |
|---|---|
| [`docs/kg-comparison.md`](docs/kg-comparison.md) | **主文件。** 建圖比較、edge 為什麼難建、查圖比較、三個實測踩到的坑 |
| [`docs/kg-comparison.html`](docs/kg-comparison.html) | 同一份內容的網頁版，雙擊即可開啟；`Cmd/Ctrl + P` 可匯出 A4 橫式 PDF |

線上版（artifact）：<https://claude.ai/artifact/7m46RSfa8YgCWsbWAEujkU>

### 文件結構

1. **怎麼建圖** —— 解析方式、node 怎麼來、edge 怎麼來、有沒有用 LLM、存成什麼
2. **為什麼 edge 這麼難建** —— 型別推導的三段流程、三套各走到第幾步、六種斷鏈情況、edge 可信度分級
3. **怎麼用圖** —— 查詢工具、入口參數、起始 node、擴散邏輯、回傳內容、可調參數
4. **三個實際踩到的坑** —— Oracle 外鍵消失、方向記反造成的假陰性、查詢結果沒有順序

---

## 工具

### `tools/oracle_prep.py`

graphify 讀 `.sql` 建資料表 node 時，**Oracle 專有型別會讓外鍵整批消失**，
而且不會報錯 —— 表的數量完全正常，你不會知道少了什麼。

實測（`tools/fixtures/oracle_test.sql`）：

```
處理前   表/視圖:3   FK:0   ← 外鍵全部遺失
處理後   表/視圖:3   FK:1   ← 恢復
```

元兇是 `VARCHAR2` / `NUMBER(10,0)` 這類 Oracle 專有寫法讓欄位區塊解析失敗，
寫在裡面的外鍵一起陪葬。這支腳本只動型別名稱、型別參數與實體儲存子句，
**不碰表名、欄位名、約束、FK**。

```bash
python3 tools/oracle_prep.py < in.sql > out.sql

# 批次
find . -name '*.sql' -exec sh -c \
  'python3 tools/oracle_prep.py < "$1" > "${1%.sql}.clean.sql"' _ {} \;
```

先自我檢查一下你的 DDL 有沒有中這個問題：

```bash
PYTHONPATH=/path/to/graphify python3 -c "
from pathlib import Path; from graphify.extractors.sql import extract_sql
r = extract_sql(Path('你的檔.sql'))
print('表:', len([n for n in r['nodes'] if n.get('source_location')]))
print('FK:', len([e for e in r['edges'] if e['relation']=='references']))
"
```

表數正常、FK 是 0 → 就是這個問題。

> 這支腳本只涵蓋已驗證過的語法。真實 DDL 裡的 `PARTITION BY RANGE`、
> `LOB (...) STORE AS`、`GENERATED ALWAYS AS IDENTITY` 等尚未處理 ——
> 跑過一輪比對 FK 數，不足的再補規則。

---

## Skill

### `skills/codegraph-guardrails/`

給 code agent 用的查詢紀律：本專案的讀圖慣例、已知盲區、不准做的推論。

> ⚠️ **尚未完成** —— 「入口點」與「命名慣例」兩節還是範本，需要依實際專案填寫。
> 另外「這張圖回答不了的問題」那節可以用第 4 節「三個坑」的實測結果補強。

---

## 歸檔

`docs/archive/` 下的兩份早期文件，內容已大半被主文件覆蓋，保留作為過程記錄：

- `blindspots.html` —— 靜態分析的盲區
- `query-arch.html` —— 三種查詢架構

---

## 重新產生網頁版

`docs/kg-comparison.html` 由 `docs/src/kg-comparison.artifact.html` 產生
（後者是 artifact 的原始檔，不含 HTML 骨架）：

```bash
python3 docs/src/build-standalone.py
```
