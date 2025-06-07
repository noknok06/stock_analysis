# 🧾 コーディング規約（AI支援開発用）

## 📁 一般原則

**DRY原則（Don't Repeat Yourself）**を守る。
→ 同じコード・ロジック・CSSは複製せず共通化する。

**KISS原則（Keep It Simple, Stupid）**を意識し、できるだけ簡潔な構造にする。

不要なコメント・デバッグコード（console.log, print, alertなど）は納品前に削除する。

🖼️ HTML
セマンティックなタグを使う（<header>, <main>, <section>, <footer> など）。

インデントはスペース2または4（プロジェクトで統一）。

class属性の命名は**BEM（Block__Element--Modifier）**に準拠するのが望ましい。

アクセシビリティ（alt, aria-*）も意識。

🎨 CSS / TailwindCSS

## 共通原則

クラスのコピペを禁止：共通スタイルは共通クラスやCSS変数で管理。

できる限り ユーティリティファースト（Tailwindなど） でスタイリング。

カスタムCSSを使う場合は /styles ディレクトリにまとめ、再利用可能にする。

インラインスタイルは禁止。

Tailwindの注意点
カスタムクラスで命名が必要な場合、tw-やapp-などのプレフィックスを使用。

同じスタイルを複数箇所に書く場合は @apply を使って共通化。

レスポンシブ対応は sm: md: lg: を適切に使う。

## 🧠 JavaScript / TypeScript

関数は1機能に限定。長くなりすぎたら分割。

変数名・関数名は意味のある英単語で命名（例：fetchUserData, isAuthenticated）。

varは禁止。必ず const or let。

非同期処理は async/await を使い、try/catch でエラーハンドリング。

マジックナンバーは禁止。定数で定義。

## 🐍 Python（Django等）

PEP8準拠（インデント4スペース / snake_case）。

ビュー関数は短く、ロジックはサービス層やフォームクラスなどへ分離。

バリデーションやDBアクセスは必ず例外処理で囲む。

共通処理はutils.pyやmixins.pyなどに切り出す。