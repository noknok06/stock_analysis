#!/bin/bash
# setup_quick.sh - クイックセットアップスクリプト

set -e  # エラー時に停止

# 色付きメッセージ用
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 株式分析記録アプリ（AI機能付き）クイックセットアップ${NC}"
echo "=========================================="

# 必要なディレクトリの作成
echo -e "${YELLOW}📁 ディレクトリ作成...${NC}"
mkdir -p logs
mkdir -p static
mkdir -p staticfiles
mkdir -p media

# 必要なパッケージのインストール
echo -e "${YELLOW}📦 必要なパッケージをインストール中...${NC}"

# 基本的なパッケージ
pip install Django==4.2.7
pip install django-taggit==4.0.0
pip install python-decouple==3.8

# 追加の依存関係（AI機能用）
pip install numpy==1.24.3
pip install scikit-learn==1.3.0

echo -e "${GREEN}✅ パッケージインストール完了${NC}"

# データベースマイグレーション
echo -e "${YELLOW}🗄️  データベースセットアップ...${NC}"
python manage.py makemigrations
python manage.py migrate

echo -e "${GREEN}✅ データベースマイグレーション完了${NC}"

# スーパーユーザー作成（オプション）
echo -e "${YELLOW}👤 管理ユーザー作成...${NC}"
echo "管理ユーザーを作成しますか？ (y/N)"
read -r create_superuser
if [[ $create_superuser =~ ^[Yy]$ ]]; then
    echo "ユーザー名: admin"
    echo "パスワード: admin123"
    echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'admin123')" | python manage.py shell
    echo -e "${GREEN}✅ 管理ユーザー作成完了 (admin/admin123)${NC}"
fi

# サンプルデータ作成
echo -e "${YELLOW}📊 サンプルデータ作成...${NC}"
python manage.py create_sample_data || echo "サンプルデータコマンドをスキップ"

# 静的ファイル収集
echo -e "${YELLOW}📦 静的ファイル収集...${NC}"
python manage.py collectstatic --noinput

echo ""
echo -e "${GREEN}🎉 セットアップ完了！${NC}"
echo "=========================================="
echo -e "${BLUE}🚀 サーバー起動方法:${NC}"
echo "  python manage.py runserver"
echo ""
echo -e "${BLUE}📝 アクセスURL:${NC}"
echo "  アプリケーション: http://127.0.0.1:8000/"
echo "  管理画面: http://127.0.0.1:8000/admin/ (admin/admin123)"
echo ""
echo -e "${BLUE}✨ AI機能:${NC}"
echo "  ✓ 自動タグ推奨"
echo "  ✓ セマンティック検索"  
echo "  ✓ 関連コンテンツ推奨"
echo "  ✓ リアルタイム分析"