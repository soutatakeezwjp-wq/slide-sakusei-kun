# スライド作成くん

Image genで、日本語の横長16:9スライド画像とPDFを作るためのCodexスキルです。

白背景、上下の青い横棒、フッターなし、送付先会社名なしの形式で、研修資料・提案資料・説明スライドを作ることを想定しています。

上下の横棒は、Image genに描かせず、後処理またはPPTX上の図形で機械的に追加します。色は必ず `#78a9ff` に統一します。

## できること

- 粗い日本語メモからスライド構成を整理
- 各ページをImage genでスライド画像として生成
- PNG画像をPDFにまとめる
- PPTX上で上下の青い棒を編集可能な長方形として配置
- 確認用のコンタクトシートを作る
- 顧客にそのまま見せやすい、清潔な日本語資料に寄せる

## 重要なルール

- 各スライド画像そのものをImage genで生成します。
- Image genには上下の棒を描かせません。
- 上下の棒は `#78a9ff` で機械的に追加します。
- 表紙だけImage gen、残りをPillowやHTMLで代替生成する使い方はしません。
- ローカル処理は、生成済みPNGのコピー、リネーム、上下棒の追加、PDF/PPTX化、コンタクトシート化、サイズ確認に使います。
- 生成画像の実寸は確認しますが、native 4Kや最高解像度を保証する表現は避けます。

## インストール

このリポジトリをCodexのスキルディレクトリへ配置してください。

```bash
mkdir -p ~/.codex/skills
git clone https://github.com/soutatakeezwjp-wq/slide-sakusei-kun.git ~/.codex/skills/slide-sakusei-kun
```

その後、Codexで次のように依頼します。

```text
スライド作成くんで、このメモを上下青線入りの日本語スライドにして。全ページImage genで作って、PNGとPDFにまとめて。
```

## PDF / PPTX化

生成済みPNGをPDF、PPTX、確認用コンタクトシートにまとめる場合は、補助スクリプトを使えます。

```bash
python scripts/make_pdf_and_contact_sheet.py ./generated-slides \
  --out slides.pdf \
  --pptx slides.pptx \
  --png-dir final_png \
  --contact-sheet contact_sheet.png
```

デフォルトでは、上下棒は `#78a9ff`、高さは1080px換算で42pxです。必要な場合だけ変更できます。

```bash
python scripts/make_pdf_and_contact_sheet.py ./generated-slides \
  --out slides.pdf \
  --bar-color '#78a9ff' \
  --bar-height 42
```

## 使い方の例

```text
以下の内容を研修スライドにしてください。

1枚目: タイトル
NotebookLMの使い方

2枚目: できること
資料を読み込む
質問する
音声やスライドにする

3枚目: まとめ
まず資料を入れて、小さく試す
```

## 出力物

基本的には次の成果物を作ります。

- PNG画像一式
- PDF
- PPTX
- 確認用コンタクトシート

## 同梱ファイル

- `SKILL.md`: Codexスキル本体
- `references/style-guide.md`: スライドの見た目のルール
- `scripts/make_pdf_and_contact_sheet.py`: 生成済み画像からPDFと確認用一覧を作る補助スクリプト
- `agents/openai.yaml`: Codex UI向けの説明メタデータ

## 注意

このリポジトリには、特定顧客の資料、生成済み画像、個人情報、APIキーは含めていません。
