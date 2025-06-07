#!/bin/bash
# setup.sh - 株式分析記録アプリ（フェーズ2）セットアップスクリプト

set -e  # エラー時に停止

# 色付きメッセージ用
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 株式分析記録アプリ（フェーズ2）セットアップ開始${NC}"
echo "=========================================="

# Python バージョンチェック
echo -e "${YELLOW}📋 Python バージョンチェック...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 がインストールされていません${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
REQUIRED_VERSION="3.9"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo -e "${RED}❌ Python 3.9+ が必要です（現在: $PYTHON_VERSION）${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Python $PYTHON_VERSION 確認${NC}"

# プロジェクトディレクトリ確認
if [ ! -f "manage.py" ]; then
    echo -e "${RED}❌ Djangoプロジェクトディレクトリで実行してください${NC}"
    exit 1
fi

# 仮想環境作成・有効化
echo -e "${YELLOW}🔧 仮想環境セットアップ...${NC}"
if [ ! -d "venv" ]; then
    echo "仮想環境を作成中..."
    python3 -m venv venv
fi

echo "仮想環境を有効化中..."
source venv/bin/activate

# pip アップグレード
echo -e "${YELLOW}⬆️  pip アップグレード...${NC}"
pip install --upgrade pip

# 依存関係インストール
echo -e "${YELLOW}📦 依存関係インストール...${NC}"
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo -e "${RED}❌ requirements.txt が見つかりません${NC}"
    exit 1
fi

# 環境変数ファイル設定
echo -e "${YELLOW}⚙️  環境設定...${NC}"
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${GREEN}✅ .env.example から .env を作成しました${NC}"
        echo -e "${YELLOW}💡 .env ファイルを必要に応じて編集してください${NC}"
    else
        echo -e "${YELLOW}⚠️  .env.example が見つかりません。手動で .env を作成してください${NC}"
    fi
else
    echo -e "${GREEN}✅ .env ファイルが既に存在します${NC}"
fi

# ログディレクトリ作成
echo -e "${YELLOW}📁 ログディレクトリ作成...${NC}"
mkdir -p logs
echo -e "${GREEN}✅ logs/ ディレクトリ作成完了${NC}"

# 静的ファイルディレクトリ作成
echo -e "${YELLOW}📁 静的ファイルディレクトリ作成...${NC}"
mkdir -p static staticfiles media
echo -e "${GREEN}✅ 静的ファイルディレクトリ作成完了${NC}"

# データベースマイグレーション
echo -e "${YELLOW}🗄️  データベースセットアップ...${NC}"
python manage.py makemigrations
python manage.py migrate

echo -e "${GREEN}✅ データベースマイグレーション完了${NC}"

# スーパーユーザー作成確認
echo -e "${YELLOW}👤 管理ユーザー作成...${NC}"
read -p "管理ユーザーを作成しますか？ (y/N): " create_superuser
if [[ $create_superuser =~ ^[Yy]$ ]]; then
    python manage.py createsuperuser
else
    echo "管理ユーザーは後で 'python manage.py createsuperuser' で作成できます"
fi

# サンプルデータ作成確認
echo -e "${YELLOW}📊 サンプルデータ作成...${NC}"
read -p "サンプルデータを作成しますか？ (y/N): " create_sample
if [[ $create_sample =~ ^[Yy]$ ]]; then
    python manage.py create_sample_data
    echo -e "${GREEN}✅ サンプルデータ作成完了${NC}"
else
    echo "サンプルデータは後で 'python manage.py create_sample_data' で作成できます"
fi

# AI分析初期化確認
echo -e "${YELLOW}🤖 AI分析初期化...${NC}"
read -p "AI分析を初期化しますか？ (y/N): " init_ai
if [[ $init_ai =~ ^[Yy]$ ]]; then
    echo "AI分析を実行中..."
    python manage.py run_ai_analysis --limit 10
    echo -e "${GREEN}✅ AI分析初期化完了${NC}"
else
    echo "AI分析は後で 'python manage.py run_ai_analysis' で実行できます"
fi

# 静的ファイル収集
echo -e "${YELLOW}📦 静的ファイル収集...${NC}"
python manage.py collectstatic --noinput

echo -e "${GREEN}✅ 静的ファイル収集完了${NC}"

# セットアップ完了
echo ""
echo -e "${GREEN}🎉 セットアップ完了！${NC}"
echo "=========================================="
echo -e "${BLUE}🚀 サーバー起動方法:${NC}"
echo "  source venv/bin/activate"
echo "  python manage.py runserver"
echo ""
echo -e "${BLUE}📝 アクセスURL:${NC}"
echo "  アプリケーション: http://127.0.0.1:8000/"
echo "  管理画面: http://127.0.0.1:8000/admin/"
echo ""
echo -e "${BLUE}🛠️  便利なコマンド:${NC}"
echo "  AI分析実行: python manage.py run_ai_analysis"
echo "  サンプルデータ作成: python manage.py create_sample_data"
echo "  テスト実行: python manage.py test"
echo ""
echo -e "${BLUE}📚 フェーズ2の新機能:${NC}"
echo "  ✨ AI支援分析・タグ推奨"
echo "  🔍 セマンティック検索"
echo "  🤝 関連コンテンツ推奨"
echo "  📊 自動分類・洞察生成"
echo "  ⚡ リアルタイムAI分析"
echo ""
echo -e "${YELLOW}💡 次のステップ:${NC}"
echo "  1. .env ファイルを確認・調整"
echo "  2. サーバーを起動してアプリケーションをテスト"
echo "  3. AI機能をお試しください！"