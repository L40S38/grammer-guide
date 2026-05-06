以下は **Cursorにそのまま投げる用の仕様書** として書いています。
前提として、Jupyter Notebookで編集・確認し、最終的には各セクションをHTML化してGitHub Pagesで静的配信できる構成です。

Jupyter Notebookはコード・説明文・可視化を同じ文書にまとめられ、`nbconvert` はNotebookをHTMLなどへ変換できます。`jupyter nbconvert --to FORMAT notebook.ipynb` という形でCLI変換できるため、Notebookベースの教材生成に向いています。([nbconvert.readthedocs.io][1]) Plotlyはインタラクティブ図をHTMLとして書き出せ、`include_plotlyjs` の指定でplotly.jsを埋め込むかCDN参照にするかを選べます。([Plotly][2]) GitHub PagesはGitHub Actionsワークフローで静的サイトを公開できるため、生成済みHTMLを`public/`などに出力してPagesへデプロイする構成にします。([GitHub Docs][3])

---

# Cursor実装用仕様書：TOEIC英文法・時間軸インフォグラフィック教材

## 1. 目的

TOEIC学習用に、英語の時制・完了形・仮定法・助動詞を **時間軸ベースで比較できる静的Web教材** を作成する。

初期開発・内容確認は **Jupyter Notebook** 上で行う。
最終成果物として、各セクションをHTML化し、GitHub Pagesで静的ページとして配信できるようにする。

教材の中心テーマは以下。

* V / V-ed / done / V-ing などの記号整理
* 時制・完了形を「現在・過去・未来」「一点・期間」「進行中・習慣・完了」で比較
* 条件文・仮定法を時間軸と現実度で比較
* 助動詞 + V と 助動詞 + have done の違い
* TOEICの `If you ___, please let us know.` 型の判断
* 最終的に「見た形 → 時間軸 → 状態 → 意味」で判定できる表を作る

---

## 2. 技術スタック

### 必須

* Python 3.10+
* Jupyter Notebook / JupyterLab
* pandas
* plotly
* jinja2
* nbconvert
* pathlib
* pydantic もしくは dataclasses
* GitHub Pages
* GitHub Actions

### 任意

* ipywidgets
  Notebook上でタブ表示する場合に使用。ただし、静的HTML化時の互換性を考え、最終公開ページでは必須にしない。
* beautifulsoup4
  nbconvert後のHTML加工に使う場合。
* mkdocs もしくは独自Jinjaテンプレート
  サイト全体のナビゲーション生成に使う場合。

---

## 3. 全体方針

### 3.1 Notebookは「確認用」、HTMLは「公開用」

Notebookは開発・確認・教材編集用とする。

公開用HTMLは、Notebookそのものをそのまま公開するのではなく、以下のどちらかで生成する。

#### 推奨方式：PythonスクリプトからHTML生成

```text
データ定義
↓
Plotly図生成
↓
pandas表生成
↓
Jinja2テンプレートに埋め込み
↓
section_01.html 〜 section_09.html と index.html を生成
```

#### 補助方式：NotebookからnbconvertでHTML生成

Notebook全体を確認用HTMLとして出力する。

```bash
jupyter nbconvert --to html notebooks/grammar_guide.ipynb --output-dir public/notebook
```

`nbconvert` はNotebookをHTML等に変換できるので、確認版・アーカイブ版として使う。([nbconvert.readthedocs.io][1])

---

## 4. ディレクトリ構成

以下の構成で実装する。

```text
toeic-grammar-timeline/
├─ README.md
├─ pyproject.toml
├─ requirements.txt
├─ .gitignore
├─ .github/
│  └─ workflows/
│     └─ deploy-pages.yml
│
├─ data/
│  ├─ grammar_sections.yaml
│  ├─ grammar_forms.yaml
│  ├─ grammar_tenses.yaml
│  ├─ grammar_conditionals.yaml
│  ├─ grammar_modals.yaml
│  ├─ grammar_modal_perfects.yaml
│  ├─ grammar_confusions.yaml
│  ├─ grammar_toeic_patterns.yaml
│  ├─ grammar_decision_table.yaml
│  └─ grammar_check_steps.yaml
│
├─ notebooks/
│  └─ grammar_guide.ipynb
│
├─ src/
│  ├─ grammar_guide/
│  │  ├─ __init__.py
│  │  ├─ models.py
│  │  ├─ load_data.py
│  │  ├─ render_tables.py
│  │  ├─ render_timeline.py
│  │  ├─ render_cards.py
│  │  ├─ build_site.py
│  │  └─ constants.py
│
├─ templates/
│  ├─ base.html
│  ├─ index.html.j2
│  ├─ section.html.j2
│  └─ components/
│     ├─ table.html.j2
│     ├─ timeline.html.j2
│     ├─ note_box.html.j2
│     └─ pattern_card.html.j2
│
├─ static/
│  ├─ css/
│  │  └─ style.css
│  └─ js/
│     └─ main.js
│
├─ public/
│  ├─ index.html
│  ├─ sections/
│  │  ├─ section_01.html
│  │  ├─ section_02.html
│  │  ├─ section_03.html
│  │  ├─ section_04.html
│  │  ├─ section_05.html
│  │  ├─ section_06.html
│  │  ├─ section_07.html
│  │  ├─ section_08.html
│  │  └─ section_09.html
│  ├─ assets/
│  │  ├─ css/
│  │  └─ js/
│  └─ .nojekyll
│
└─ scripts/
   ├─ build_site.py
   └─ export_notebook.py
```

---

## 5. 生成物

### 5.1 Notebook

```text
notebooks/grammar_guide.ipynb
```

用途：

* データ確認
* 表の見た目確認
* Plotly時間軸の見た目確認
* 教材内容の編集・検証

Notebook内に以下のセクションを含める。

1. 記号の意味
2. 時制・完了形の一覧
3. 条件文・仮定法の一覧
4. 助動詞 + V の一覧
5. 助動詞 + have done の一覧
6. 特に混同しやすい形だけ比較
7. TOEICでの実戦判断：`If you ___, please let us know.`
8. 一番使える判定表
9. 見抜くコツ

### 5.2 静的HTML

```text
public/index.html
public/sections/section_01.html
...
public/sections/section_09.html
```

各セクションは単独HTMLページとして表示できること。

### 5.3 indexページ

`public/index.html` には、9セクションへのリンクカードを表示する。

---

## 6. 表示デザイン仕様

### 6.1 全体デザイン

先に作成したインフォグラフィック風の見た目をHTMLで再現する。

* 背景：薄い青〜白
* セクションカード：角丸、薄い影、白背景
* 見出し：濃い青・緑・紫・オレンジなど、セクションごとに色分け
* 表：ヘッダー行に色、罫線あり
* 時間軸：横方向に「過去 → 現在 → 未来」
* 現在点：中央に縦線
* 期間：横棒
* 一点：丸マーカー
* 完了：過去から基準時点に向かう矢印またはバー
* 非現実・反実仮想：点線、×印、薄い赤系背景
* TOEICで重要な注意：黄色のポイントボックス

### 6.2 色分け

```python
SECTION_COLORS = {
    1: "#1f5aa6",  # blue
    2: "#1b8a5a",  # green
    3: "#6f42c1",  # purple
    4: "#16836f",  # teal
    5: "#f07c00",  # orange
    6: "#1f5aa6",  # blue
    7: "#6f42c1",  # purple
    8: "#0d47a1",  # deep blue
    9: "#0d47a1",  # deep blue
}
```

### 6.3 レスポンシブ

* PC：横幅最大1100px
* スマホ：表は横スクロール許可
* Plotly図も横スクロールまたはレスポンシブ対応
* `overflow-x: auto` を `.table-wrapper` と `.plot-wrapper` に指定

---

## 7. データモデル仕様

### 7.1 基本データ構造

各文法項目は以下のキーを持つ。

```python
@dataclass
class GrammarItem:
    section: int
    id: str
    label: str
    form: str
    meaning_ja: str
    time_focus: str
    start: float | None
    end: float | None
    point_or_span: str
    state: str
    reality: str
    nuance: str
    example_en: str
    example_ja: str
    toeic_hint: str
    importance: int
```

### 7.2 `time_focus`

以下のいずれか。

```text
past
past_before_past
present
future
past_to_present
present_to_future
past_to_future
general
hypothetical_present_future
counterfactual_past
```

### 7.3 `point_or_span`

```text
point
span
habit
result
experience
progress
condition
not_applicable
```

### 7.4 `state`

```text
fact
habit
action_point
in_progress
completed
result
experience
possibility
ability
obligation
advice
deduction
counterfactual
polite_request
intention
```

### 7.5 時間軸の数値

時間軸は以下の数値で表す。

| 数値 | 意味    |
| -: | ----- |
| -5 | 過去より前 |
| -3 | 過去    |
|  0 | 現在    |
|  3 | 未来    |

例：

```yaml
start: -3
end: 0
```

は「過去から現在へのつながり」。

```yaml
start: -3
end: -3
```

は「過去の一点」。

```yaml
start: 0
end: 3
```

は「現在から未来」。

---

# 8. 各セクションの具体的内容

## Section 1：記号の意味

### 目的

以降の表で使う記号を先に定義する。

### 表示内容

タイトル：

```text
1. 記号の意味
```

説明文：

```text
この教材では、動詞の形を V / V-ed / done / V-ing のように一般化して表します。規則動詞では V-ed と done が同じ形になることがありますが、不規則動詞では異なる形になるので注意します。
```

### 表データ

| 記号                | 意味        | 例1：work         | 例2：send         | 例3：write           | 注意              |
| ----------------- | --------- | --------------- | --------------- | ------------------ | --------------- |
| V                 | 動詞の原形     | work            | send            | write              | 助動詞の後ろ、命令文など    |
| V-s               | 三単現       | works           | sends           | writes             | 現在形で主語が三人称単数    |
| V-ed / did        | 過去形       | worked          | sent            | wrote              | 過去の一点、仮定法過去にも使う |
| done              | 過去分詞      | worked          | sent            | written            | 完了形・受動態で使う      |
| V-ing             | 現在分詞・動名詞  | working         | sending         | writing            | 進行形・動名詞         |
| be + V-ing        | 進行形       | is working      | is sending      | is writing         | その時点で進行中        |
| have + done       | 現在完了      | has worked      | has sent        | has written        | 過去から現在へのつながり    |
| had + done        | 過去完了      | had worked      | had sent        | had written        | 過去のある時点より前      |
| modal + V         | 助動詞 + 原形  | can work        | may send        | could write        | 助動詞の後ろは原形       |
| modal + have done | 助動詞 + 完了形 | may have worked | could have sent | would have written | 過去推量・過去仮定       |

### ポイントボックス

```text
ポイント：規則動詞では V-ed と done が同じ形になりますが、不規則動詞では異なります。
例：write → wrote / written, do → did / done, go → went / gone
```

---

## Section 2：時制・完了形の一覧

### 目的

時制を「いつ」「一点か期間か」「その時点でどんな状態か」で比較する。

### タイトル

```text
2. 時制・完了形の一覧：時間軸で理解
```

### 説明文

```text
時制は、単に「過去・現在・未来」だけでなく、「一点の出来事」か「期間」か、「習慣」か「進行中」か「完了」かで見ると整理しやすくなります。
```

### 表データ

| 形       | 一般形                   | 時間       | 一点/期間 | 状態          | 例文                                         | 日本語                   | TOEICでの見方      |
| ------- | --------------------- | -------- | ----- | ----------- | ------------------------------------------ | --------------------- | -------------- |
| 現在形     | V / V-s               | 現在・一般    | 習慣・一般 | 事実・習慣       | The office opens at 9.                     | そのオフィスは9時に開きます。       | 規則・事実          |
| 過去形     | V-ed / did            | 過去       | 一点    | 過去の出来事      | The office closed early yesterday.         | そのオフィスは昨日早く閉まりました。    | yesterdayなどと相性 |
| 未来表現    | will + V              | 未来       | 一点/期間 | 予定・予測       | We will send the invoice tomorrow.         | 明日請求書を送ります。           | 未来の予定・意志       |
| 現在進行形   | am/is/are + V-ing     | 現在       | 期間    | 今している最中     | She is reviewing the file.                 | 彼女は今ファイルを確認しています。     | 進行中・近い予定       |
| 過去進行形   | was/were + V-ing      | 過去       | 期間    | 過去のある時点で進行中 | They were preparing the room.              | 彼らは部屋を準備していました。       | 背景動作           |
| 現在完了    | have/has + done       | 過去→現在    | 期間/結果 | 完了・経験・結果    | We have received your application.         | 申請書を受け取りました。          | 今に関係がある        |
| 現在完了進行形 | have/has been + V-ing | 過去→現在    | 期間    | 継続中・途中経過    | We have been reviewing your application.   | 申請書を確認しているところです。      | ずっと続いている       |
| 過去完了    | had + done            | 過去より前→過去 | 一点/結果 | 過去の基準点までに完了 | The train had left when we arrived.        | 私たちが着いた時、電車は出発していました。 | 過去の過去          |
| 過去完了進行形 | had been + V-ing      | 過去より前→過去 | 期間    | 過去の基準点まで継続  | They had been waiting for an hour.         | 彼らは1時間待っていました。        | 過去までの継続        |
| 未来完了    | will have + done      | 現在→未来    | 期間/結果 | 未来の時点までに完了  | We will have completed the work by Friday. | 金曜までに仕事を終えているでしょう。    | by Fridayなどが目印 |

### 時間軸データ

| label   | start |  end | type  |
| ------- | ----: | ---: | ----- |
| 現在形     |     0 |    3 | habit |
| 過去形     |    -3 |   -3 | point |
| 未来表現    |     0 |    3 | span  |
| 現在進行形   |  -0.5 |  0.5 | span  |
| 過去進行形   |  -3.5 | -2.5 | span  |
| 現在完了    |    -3 |    0 | span  |
| 現在完了進行形 |    -3 |    0 | span  |
| 過去完了    |    -5 |   -3 | span  |
| 過去完了進行形 |    -5 |   -3 | span  |
| 未来完了    |     0 |    3 | span  |

### ポイントボックス

```text
ポイント：現在完了は「今から過去を振り返る」、過去完了は「過去のある時点からさらに前を振り返る」。
```

---

## Section 3：条件文・仮定法の一覧

### 目的

条件文を「if節の時点」「主節の時点」「現実度」で比較する。

### タイトル

```text
3. 条件文・仮定法の一覧：時間軸で理解
```

### 説明文

```text
条件文は「if節」と「主節」の組み合わせです。TOEICでは、if節だけでなく主節の形を見て、現実の話か仮定の話か、過去の話か未来の話かを判断します。
```

### 表データ

| 種類   | if節           | 主節                          | 時間        | 現実度    | 例文                                                             | 日本語                      | コアイメージ      |
| ---- | ------------- | --------------------------- | --------- | ------ | -------------------------------------------------------------- | ------------------------ | ----------- |
| ゼロ条件 | If + V/V-s    | V/V-s                       | 一般事実      | 高い     | If water freezes, it expands.                                  | 水は凍ると膨張します。              | いつもそうなる     |
| 第1条件 | If + V/V-s    | will/can/may + V            | 未来        | 高め     | If it rains, we will cancel the event.                         | 雨ならイベントを中止します。           | 起こりうる未来     |
| 第2条件 | If + V-ed/did | would/could/might + V       | 現在・未来の仮定  | 低め     | If I had more time, I could help you.                          | もっと時間があれば手伝えるのに。         | もし今/未来が違ったら |
| 第3条件 | If + had done | would/could/might have done | 過去の仮定     | 実際とは違う | If you had asked me, I would have helped you.                  | 聞いてくれていたら手伝ったのに。         | もし過去が違ったら   |
| 混合条件 | If + had done | would/could/might + V       | 過去原因→現在結果 | 実際とは違う | If she had studied accounting, she could handle this task now. | 会計を勉強していたら、今この仕事をこなせるのに。 | 過去が違えば今が違う  |

### 時間軸データ

条件文は、if節と主節を別レーンで表示する。

| label | clause  | start | end | reality        |
| ----- | ------- | ----: | --: | -------------- |
| ゼロ条件  | if/main |    -3 |   3 | real           |
| 第1条件  | if      |     0 |   3 | likely         |
| 第1条件  | main    |     0 |   3 | likely         |
| 第2条件  | if      |     0 |   3 | hypothetical   |
| 第2条件  | main    |     0 |   3 | hypothetical   |
| 第3条件  | if      |    -3 |  -3 | counterfactual |
| 第3条件  | main    |    -3 |  -3 | counterfactual |
| 混合条件  | if      |    -3 |  -3 | counterfactual |
| 混合条件  | main    |     0 |   0 | counterfactual |

### ポイントボックス

```text
ポイント：第2条件は「現在・未来の仮定」、第3条件は「実際とは違う過去」。if節の形と主節の形をセットで見る。
```

---

## Section 4：助動詞 + V の一覧

### 目的

助動詞 + V が現在・未来の可能性、能力、丁寧さ、義務を表すことを整理する。

### タイトル

```text
4. 助動詞 + V の一覧：現在・未来の可能性・能力・丁寧さ
```

### 表データ

| 形          | 一般形      | 主な意味            | 時間       | 例文                                       | 日本語                  | ニュアンス          |
| ---------- | -------- | --------------- | -------- | ---------------------------------------- | -------------------- | -------------- |
| can + V    | can V    | できる・可能          | 現在・未来    | We can help you.                         | お手伝いできます。            | 能力・可能性。直接的     |
| could + V  | could V  | できるかもしれない・丁寧    | 現在・未来    | If you could attend, please let us know. | 出席できるようでしたらお知らせください。 | 丁寧・控えめな可能性     |
| may + V    | may V    | かもしれない・してもよい    | 現在・未来    | The plan may change.                     | 計画は変更されるかもしれません。     | 可能性・許可。ややフォーマル |
| might + V  | might V  | かもしれない          | 現在・未来    | It might arrive late.                    | 遅れて到着するかもしれません。      | mayより控えめ       |
| will + V   | will V   | するつもりだ・するだろう    | 未来       | We will contact you soon.                | すぐに連絡します。            | 意志・予測          |
| would + V  | would V  | するだろう・仮定ならする    | 現在・未来/仮定 | I would recommend this option.           | この選択肢をおすすめします。       | 丁寧な提案・仮定       |
| should + V | should V | すべき・するはず        | 現在・未来    | It should arrive today.                  | 今日届くはずです。            | 助言・見込み         |
| must + V   | must V   | しなければならない・に違いない | 現在・未来    | You must wear a badge.                   | バッジを着用しなければなりません。    | 義務・強い推量        |

### 時間軸データ

基本的にすべて `start: 0, end: 3`。
`would + V` は仮定モードとして点線表示可能。

### ポイントボックス

```text
ポイント：could V は「過去にできた」だけではなく、現在・未来の丁寧な可能性にも使う。
```

---

## Section 5：助動詞 + have done の一覧

### 目的

`modal + have done` が過去に向かう形であることを整理する。

### タイトル

```text
5. 助動詞 + have done の一覧：過去推量・過去仮定
```

### 表データ

| 形                | 一般形              | 主な意味             | 時間 | 例文                                 | 日本語                  | ニュアンス        |
| ---------------- | ---------------- | ---------------- | -- | ---------------------------------- | -------------------- | ------------ |
| may have done    | may have done    | 〜したかもしれない        | 過去 | He may have forgotten it.          | 彼はそれを忘れた可能性があります。    | 過去推量。可能性やや高め |
| might have done  | might have done  | 〜したかもしれない        | 過去 | He might have forgotten it.        | 彼はそれを忘れたかもしれません。     | 過去推量。控えめ     |
| could have done  | could have done  | 〜できたかもしれない／できたのに | 過去 | We could have finished it earlier. | もっと早く終えられたかもしれません。   | 可能性・機会       |
| would have done  | would have done  | 〜しただろうに          | 過去 | I would have joined the meeting.   | 会議に参加しただろうに。         | 過去の反実仮想      |
| should have done | should have done | 〜すべきだった          | 過去 | You should have checked it.        | それを確認すべきでした。         | 後悔・助言        |
| must have done   | must have done   | 〜したに違いない         | 過去 | She must have missed it.           | 彼女はそれを見落としたに違いありません。 | 強い推量         |
| can’t have done  | can’t have done  | 〜したはずがない         | 過去 | He can’t have approved it.         | 彼がそれを承認したはずがありません。   | 強い否定推量       |

### 時間軸データ

すべて過去側に配置。

| label            | start | end | style                    |
| ---------------- | ----: | --: | ------------------------ |
| may have done    |    -3 |  -3 | point_uncertain          |
| might have done  |    -3 |  -3 | point_uncertain          |
| could have done  |    -3 |  -3 | point_possible           |
| would have done  |    -3 |  -3 | point_counterfactual     |
| should have done |    -3 |  -3 | point_regret             |
| must have done   |    -3 |  -3 | point_deduction          |
| can’t have done  |    -3 |  -3 | point_negative_deduction |

### ポイントボックス

```text
ポイント：modal + have done は基本的に「過去のこと」についての推量・仮定・後悔を表す。
```

---

## Section 6：特に混同しやすい形だけ比較

### 目的

見た目が似ている形を、時間軸と意味で比較する。

### タイトル

```text
6. 特に混同しやすい形だけ比較
```

### 表データ

| 比較する形           | 時間軸      | 一点/期間 | 主な意味                 | 例文                                      | 日本語                  | 混同ポイント    |
| --------------- | -------- | ----- | -------------------- | --------------------------------------- | -------------------- | --------- |
| could V         | 現在・未来    | 一点/期間 | できるかもしれない・丁寧に「できるなら」 | If you could reply, please let us know. | 返信できるようでしたらお知らせください。 | 過去とは限らない  |
| could have done | 過去       | 一点    | できたかもしれない／できたのに      | We could have sent it yesterday.        | 昨日送ることもできました。        | 現在・未来ではない |
| would V         | 現在・未来の仮定 | 一点/期間 | 〜するだろう               | I would choose this option.             | 私ならこの選択肢を選びます。       | 仮定上の話     |
| would have done | 過去の仮定    | 一点    | 〜しただろうに              | I would have chosen this option.        | 私ならこの選択肢を選んでいたでしょう。  | 過去の話      |
| may V           | 現在・未来    | 一点/期間 | 〜かもしれない              | The price may change.                   | 価格が変わるかもしれません。       | 未来の可能性    |
| may have done   | 過去       | 一点    | 〜したかもしれない            | The price may have changed.             | 価格が変わった可能性があります。     | 過去の可能性    |
| might V         | 現在・未来    | 一点/期間 | 〜かもしれない              | The meeting might end early.            | 会議は早く終わるかもしれません。     | 控えめな推量    |
| might have done | 過去       | 一点    | 〜したかもしれない            | The meeting might have ended early.     | 会議は早く終わったかもしれません。    | 過去推量      |
| had done        | 過去より前→過去 | 一点/結果 | 〜していた                | The train had left when we arrived.     | 着いた時には電車は出ていました。     | 過去の過去     |
| have/has done   | 過去→現在    | 期間/結果 | 〜した／している             | The event has started.                  | イベントは始まっています。        | 今に関係する    |

### 可視化

* 左に形
* 中央に時間軸バー
* 右に「混同ポイント」
* `could V` と `could have done` を同じ色系で比較
* `would V` と `would have done` を同じ色系で比較
* `may V` と `may have done` を同じ色系で比較

### ポイントボックス

```text
ポイント：形が似ていても、時間軸が違う。have done が付くと、多くの場合「過去側」に視点が移る。
```

---

## Section 7：TOEICでの実戦判断：`If you ___, please let us know.`

### 目的

依頼表現の後ろに来る場合の選択肢判断を整理する。

### タイトル

```text
7. TOEICでの実戦判断：If you ___, please let us know.
```

### 説明文

```text
後ろが please let us know / please contact us / please confirm / please reply by Friday などの依頼表現なら、「これから対応できるかどうか」を聞いている可能性が高いです。
```

### 自然な候補

| 形         | 意味              | 例文                                                  | 日本語                        | 判定 |
| --------- | --------------- | --------------------------------------------------- | -------------------------- | -- |
| could + V | 〜できるようでしたら      | If you could send the document, please let us know. | 書類を送れるようでしたらお知らせください。      | ◎  |
| can + V   | 〜できるなら          | If you can send the document, please let us know.   | 書類を送れるならお知らせください。          | ○  |
| V / V-s   | 〜するなら           | If you send the document, please let us know.       | 書類を送る場合はお知らせください。          | ○  |
| would + V | 〜していただける意向があるなら | If you would send the document, please let us know. | 書類を送っていただけるようでしたらお知らせください。 | △  |

### 不自然になりやすい候補

| 形               | なぜ不自然か              | 例文                                                       | 判定 |
| --------------- | ------------------- | -------------------------------------------------------- | -- |
| had done        | 過去に〜していたなら、という意味になる | If you had sent the document, please let us know.        | ×  |
| would have done | 過去に〜しただろうに、という意味になる | If you would have sent the document, please let us know. | ×  |
| have been V-ing | ずっと〜しているなら、になり文脈依存  | If you have been reviewing it, please let us know.       | △  |

### フローチャート

1. 後半に依頼表現があるか？
2. その依頼は「今から/これから」の対応確認か？
3. できるかどうかを聞いているか？
4. できるなら `could + V`、直接なら `can + V`、行為条件なら `V/V-s`
5. 過去仮定なら `had done` / `would have done` だが、この依頼パターンでは基本的に不自然

### ポイントボックス

```text
ポイント：please let us know 型は、基本的に「これからできるかどうか」を聞く。過去の仮定ではなく、現在・未来の可能性を見る。
```

---

## Section 8：一番使える判定表

### 目的

問題で形を見たときに、時間軸と状態を即判定する一覧。

### タイトル

```text
8. 一番使える判定表：見た形 → 時間軸 → 状態
```

### 表データ

| 見た形                 | まず考える意味     | 時間軸      | 一点/期間 | 状態        | 例文                                                | TOEICヒント      |
| ------------------- | ----------- | -------- | ----- | --------- | ------------------------------------------------- | ------------- |
| V / V-s             | 事実・条件・習慣    | 現在・未来/一般 | 習慣・一般 | 事実・習慣     | If it arrives, please inspect it.                 | 条件文では未来でも現在形  |
| V-ed / did          | 過去、または仮定法   | 過去 or 仮定 | 一点    | 過去の出来事/仮定 | If we received it, we would call you.             | 過去形か仮定法か文脈で判断 |
| have/has done       | 今につながる完了・経験 | 過去→現在    | 期間/結果 | 完了・経験・結果  | We have updated the schedule.                     | 今に関係がある       |
| had done            | 過去のある時点より前  | 過去より前→過去 | 一点/結果 | 過去の過去     | The report had been submitted.                    | 過去完了 or 第3条件  |
| will V              | 未来・意志・予定    | 未来       | 一点/期間 | 予定・予測     | We will send the details.                         | 未来の基本         |
| would V             | 仮定上の結果・丁寧表現 | 現在・未来/仮定 | 一点/期間 | 仮定・丁寧     | I would recommend checking the policy.            | 丁寧表現にも使う      |
| could V             | 可能性・能力・丁寧表現 | 現在・未来    | 一点/期間 | 可能・丁寧     | If you could reply today, we would appreciate it. | 過去とは限らない      |
| may/might V         | 現在・未来の可能性   | 現在・未来    | 一点/期間 | 可能性       | The event may be postponed.                       | 未来の可能性        |
| would have done     | 過去の反実仮想     | 過去       | 一点    | 反実仮想      | We would have called you.                         | 過去に〜しただろうに    |
| may/might have done | 過去推量        | 過去       | 一点    | 推量        | The manager may have approved the request.        | 過去の可能性        |
| should have done    | すべきだった      | 過去       | 一点    | 後悔・助言     | You should have attached the receipt.             | 過去への助言        |
| must have done      | したに違いない     | 過去       | 一点    | 強い推量      | She must have misunderstood the instructions.     | 過去への強い推量      |

### ポイントボックス

```text
ポイント：迷ったら、まず「いつのことか」を決める。次に「一点か期間か」「進行中か完了か」「現実か仮定か」を見る。
```

---

## Section 9：見抜くコツ

### 目的

実際のTOEIC問題で迷ったときの判断手順を固定する。

### タイトル

```text
9. 見抜くコツ：判断手順
```

### 手順カード

#### Step 1：何と何をつないでいるか？

```text
単語か、句か、節かを見る。
```

例：

```text
either by email or through the online portal
→ 前置詞句どうし
```

#### Step 2：時間はいつか？

```text
過去 / 現在 / 未来 / 過去より前 / 過去から現在
```

例：

```text
had done
→ 過去の基準点より前
```

#### Step 3：一点か期間か？

```text
一点の出来事か、ある期間続いているのかを見る。
```

例：

```text
was V-ing
→ 過去のある期間で進行中
```

#### Step 4：その時点での状態は？

```text
進行中、習慣、完了、経験、結果、推量、仮定のどれかを見る。
```

#### Step 5：現実の話か、仮定・想像の話か？

```text
if節、would、could、might、had done などを見る。
```

#### Step 6：後ろの文脈・依頼表現を見る

```text
please let us know / please contact us / please confirm があれば、これからの対応確認の可能性が高い。
```

### 例題カード

```text
If you ___ one of those instead, please let us know.
```

選択肢：

| 選択肢             | 形            | 判定 |
| --------------- | ------------ | -- |
| would have done | 過去の反実仮想      | ×  |
| had done        | 過去の仮定        | ×  |
| have been V-ing | 継続中          | △  |
| could V         | 現在・未来の可能性/丁寧 | ◎  |

### まとめボックス

```text
まとめ：時間軸 × 状態 × 文脈で判断する。
特に please let us know 型では、「過去にどうだったか」ではなく「これから可能か」を見る。
```

---

# 9. 可視化仕様

## 9.1 時間軸図

Plotlyで実装する。

### 関数名

```python
render_time_axis(items: list[GrammarItem], title: str) -> str
```

### 戻り値

HTML文字列。

PlotlyはHTML出力できる。`include_plotlyjs=False` にして、ページ側でCDNを1回だけ読み込む。Plotlyの`write_html`/`to_html`には、plotly.jsの読み込み方法を指定する`include_plotlyjs`があり、`False`は既にページ内でplotly.jsを読み込む場合に使える。([plotly.github.io][4])

### 表示仕様

* x軸：過去より前 / 過去 / 現在 / 未来
* y軸：文法項目
* 現在位置 `x=0` に縦線
* `point_or_span == point` は丸マーカー
* `point_or_span == span` はバー
* `reality == counterfactual` は点線または赤
* hoverに以下を表示：

  * 形
  * 意味
  * 時間
  * 状態
  * 例文
  * TOEICヒント

## 9.2 表

pandas StylerでHTML生成する。

pandasの`Styler.to_html`は、StylerをHTML/CSS形式に書き出せる。([Pandas][5]) また、StylerはDataFrameやSeriesをHTML/CSSでスタイル付けするための機能として説明されている。([Pandas][6])

### 関数名

```python
render_styled_table(df: pd.DataFrame, section_id: int) -> str
```

### 仕様

* ヘッダー背景はセクションカラー
* セル内改行を許可
* スマホでは横スクロール
* 重要セルは太字
* `判定`列があれば：

  * ◎：緑
  * ○：薄緑
  * △：黄
  * ×：赤

---

# 10. HTMLテンプレート仕様

## 10.1 `base.html`

必須要素：

* `<meta charset="utf-8">`
* viewport設定
* title
* stylesheet読み込み
* Plotly CDN読み込み
* 共通ヘッダー
* 共通フッター

Plotly CDNを使う場合、生成HTMLは軽くなるがインターネット接続が必要。Plotlyのドキュメントにも、CDN指定ではHTMLが軽くなる一方、ライブラリ読み込みにネット接続が必要と説明されている。([Plotly][7])

## 10.2 `section.html.j2`

入力：

```python
{
    "section_id": 1,
    "title": "...",
    "description": "...",
    "table_html": "...",
    "timeline_html": "...",
    "cards_html": "...",
    "point_box": "...",
    "prev_url": "...",
    "next_url": "..."
}
```

表示順：

1. セクション見出し
2. 説明
3. 時間軸図がある場合は表示
4. 表
5. カード/フローチャート
6. ポイントボックス
7. 前後セクションリンク

---

# 11. Notebook仕様

Notebookには以下のセルを作る。

## 11.1 初期設定セル

```python
from grammar_guide.load_data import load_all_data
from grammar_guide.render_tables import render_styled_table
from grammar_guide.render_timeline import render_time_axis
from IPython.display import HTML, display, Markdown

data = load_all_data("../data")
```

## 11.2 各セクション表示セル

例：

```python
display(Markdown("# 2. 時制・完了形の一覧：時間軸で理解"))
display(HTML(render_time_axis(data["tenses"], "時制・完了形の時間軸")))
display(HTML(render_styled_table(data["tenses_df"], section_id=2)))
```

Notebookは人間が確認するためのものなので、1〜9セクションを縦に表示する。

---

# 12. ビルド仕様

## 12.1 ローカルビルド

```bash
python scripts/build_site.py
```

または

```bash
python -m grammar_guide.build_site
```

処理：

1. `data/*.yaml` を読み込む
2. DataFrame化
3. 各セクションの表HTML生成
4. 各セクションのPlotly HTML生成
5. Jinja2テンプレートでHTML生成
6. `public/` に出力
7. `public/.nojekyll` を作成

## 12.2 Notebook HTML出力

```bash
jupyter nbconvert --to html notebooks/grammar_guide.ipynb --output-dir public/notebook
```

---

# 13. GitHub Pagesデプロイ仕様

GitHub Actionsで `public/` をPagesへデプロイする。

GitHub PagesはActionsワークフローで公開でき、外部CIでビルド成果物をデプロイする場合は`.nojekyll`ファイルを含めることが一般的に説明されている。([GitHub Docs][3])

`.github/workflows/deploy-pages.yml`：

```yaml
name: Deploy GitHub Pages

on:
  push:
    branches:
      - main
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: false

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          pip install -r requirements.txt

      - name: Build site
        run: |
          python scripts/build_site.py

      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: public

  deploy:
    environment:
      name: github-pages
    runs-on: ubuntu-latest
    needs: build

    steps:
      - name: Deploy to GitHub Pages
        uses: actions/deploy-pages@v4
```

`actions/deploy-pages` は、事前にアップロードされたPages成果物をデプロイするActionとして説明されている。([GitHub][8])

---

# 14. 実装タスク一覧

## Task 1：プロジェクト雛形作成

* ディレクトリ作成
* `requirements.txt` 作成
* `pyproject.toml` 作成
* `.gitignore` 作成

`requirements.txt`：

```txt
pandas
plotly
jinja2
pyyaml
nbconvert
jupyter
```

## Task 2：データYAML作成

`data/`配下に9セクション分のYAMLを作成する。

まずはこの仕様書の表データをそのままYAML化する。

## Task 3：データ読み込み

`src/grammar_guide/load_data.py`

要件：

* YAMLを読み込む
* GrammarItemに変換
* DataFrameにも変換
* セクションごとに取得できるようにする

## Task 4：表レンダリング

`src/grammar_guide/render_tables.py`

要件：

* pandas Stylerで表HTML生成
* セクションごとにヘッダー色変更
* 判定列の色付け
* 横スクロール対応ラッパーを付与

## Task 5：時間軸レンダリング

`src/grammar_guide/render_timeline.py`

要件：

* Plotlyで横軸時間図を作る
* 現在線を入れる
* hover表示を作る
* `include_plotlyjs=False`, `full_html=False` でHTML断片を返す

## Task 6：カード・フローチャートレンダリング

`src/grammar_guide/render_cards.py`

要件：

* Section 7 の自然/不自然カード
* Section 9 のStepカード
* ポイントボックス生成

## Task 7：サイト生成

`src/grammar_guide/build_site.py`

要件：

* `public/index.html` 生成
* `public/sections/section_01.html` 〜 `section_09.html` 生成
* CSS/JSコピー
* `.nojekyll` 作成

## Task 8：Notebook作成

`notebooks/grammar_guide.ipynb`

要件：

* 9セクションを順に表示
* HTMLレンダリング関数を使って、公開ページと近い見た目で確認できる
* 開発者がデータを変更したらNotebook上でも反映できる

## Task 9：GitHub Actions

* Pagesデプロイワークフロー作成
* mainブランチpushでビルド・デプロイ

---

# 15. 受け入れ条件

以下を満たすこと。

1. `python scripts/build_site.py` で `public/` にHTMLが生成される
2. `public/index.html` から9セクションに移動できる
3. 各セクションHTMLが単独で開ける
4. Section 2, 3, 5, 6, 8 に時間軸図がある
5. Section 1〜9すべてに表またはカード形式の内容がある
6. 表はスマホ幅で横スクロールできる
7. Plotly図がGitHub Pages上で表示される
8. Notebook上でも同じデータから表と図を確認できる
9. GitHub ActionsでGitHub Pagesにデプロイできる
10. 文法データはPythonコードに直書きせず、原則YAMLで管理する

---

# 16. 実装時の注意

* 画像生成結果をOCRして使わない。内容はこの仕様書の表データを正とする。
* 文法説明は、後から修正しやすいようにYAMLで持つ。
* PlotlyのHTML断片は `full_html=False` で生成する。
* plotly.jsは各セクションで重複埋め込みしない。
* `public/.nojekyll` を必ず作る。
* Notebookは公開用HTMLの唯一の生成元にしない。Notebookは確認用、公開HTMLはスクリプト生成を基本にする。
* GitHub Pagesではサーバーサイド処理は使えないため、すべて静的HTML/CSS/JSで完結させる。

---

# 17. 最初に作る最小版

最初の実装では、以下だけでよい。

```text
Section 1：表のみ
Section 2：時間軸 + 表
Section 3：時間軸 + 表
Section 7：カード + 表
Section 8：時間軸 + 表
index.html
GitHub Pages deploy
```

その後、Section 4, 5, 6, 9を追加する。

---

この仕様で作ると、**Notebookで編集・検証 → 静的HTMLにビルド → GitHub Pagesで公開** という流れがかなり安定します。

[1]: https://nbconvert.readthedocs.io/en/latest/usage.html?utm_source=chatgpt.com "Using as a command line tool - nbconvert - Read the Docs"
[2]: https://plotly.com/python/interactive-html-export/?utm_source=chatgpt.com "Interactive html export in Python"
[3]: https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site?utm_source=chatgpt.com "Configuring a publishing source for your GitHub Pages site"
[4]: https://plotly.github.io/plotly.py-docs/generated/plotly.io.write_html.html?utm_source=chatgpt.com "plotly.io.write_html — 6.6.0 documentation"
[5]: https://pandas.pydata.org/docs/reference/api/pandas.io.formats.style.Styler.to_html.html?utm_source=chatgpt.com "pandas.io.formats.style.Styler.to_html"
[6]: https://pandas.pydata.org/docs/user_guide/style.html?utm_source=chatgpt.com "Table Visualization — pandas 3.0.2 documentation - PyData |"
[7]: https://plotly.com/python-api-reference/generated/plotly.io.html?utm_source=chatgpt.com "plotly.io package — 6.6.0 documentation"
[8]: https://github.com/actions/deploy-pages?utm_source=chatgpt.com "GitHub - actions/deploy-pages"
