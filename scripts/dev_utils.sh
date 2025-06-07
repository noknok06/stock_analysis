#!/bin/bash
# scripts/dev_utils.sh - 開発用ユーティリティスクリプト

# 色付きメッセージ用
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# ヘルプメッセージ
show_help() {
    echo -e "${BLUE}🛠️  株式分析記録アプリ 開発用ユーティリティ${NC}"
    echo "=============================================="
    echo ""
    echo -e "${YELLOW}使用方法:${NC}"
    echo "  ./scripts/dev_utils.sh [command]"
    echo ""
    echo -e "${YELLOW}利用可能なコマンド:${NC}"
    echo "  setup           - 初期セットアップ"
    echo "  run             - 開発サーバー起動"
    echo "  migrate         - データベースマイグレーション"
    echo "  test            - テスト実行"
    echo "  ai-analysis     - AI分析実行"
    echo "  sample-data     - サンプルデータ作成"
    echo "  shell           - Djangoシェル起動"
    echo "  clean           - キャッシュ・ログクリア"
    echo "  backup          - データベースバックアップ"
    echo "  restore         - データベース復元"
    echo "  deps            - 依存関係更新"
    echo "  lint            - コード品質チェック"
    echo "  format          - コードフォーマット"
    echo "  logs            - ログ確認"
    echo "  status          - システム状態確認"
    echo "  help            - このヘルプを表示"
    echo ""
}

# 仮想環境確認・有効化
activate_venv() {
    if [ ! -d "venv" ]; then
        echo -e "${RED}❌ 仮想環境が見つかりません。setup を実行してください${NC}"
        exit 1
    fi
    
    if [[ "$VIRTUAL_ENV" == "" ]]; then
        echo -e "${YELLOW}🔄 仮想環境を有効化中...${NC}"
        source venv/bin/activate
    fi
}

# セットアップ
cmd_setup() {
    echo -e "${BLUE}🚀 プロジェクトセットアップ実行${NC}"
    ./setup.sh
}

# 開発サーバー起動
cmd_run() {
    activate_venv
    echo -e "${GREEN}🚀 開発サーバー起動中...${NC}"
    echo "URL: http://127.0.0.1:8000/"
    python manage.py runserver
}

# マイグレーション
cmd_migrate() {
    activate_venv
    echo -e "${YELLOW}🗄️  データベースマイグレーション実行${NC}"
    python manage.py makemigrations
    python manage.py migrate
    echo -e "${GREEN}✅ マイグレーション完了${NC}"
}

# テスト実行
cmd_test() {
    activate_venv
    echo -e "${BLUE}🧪 テスト実行中...${NC}"
    
    # カバレッジ付きテスト
    if command -v pytest &> /dev/null; then
        echo "pytest でテスト実行..."
        pytest --cov=notebooks --cov-report=html --cov-report=term
    else
        echo "Django テストランナーでテスト実行..."
        python manage.py test
    fi
    
    echo -e "${GREEN}✅ テスト完了${NC}"
}

# AI分析実行
cmd_ai_analysis() {
    activate_venv
    echo -e "${PURPLE}🤖 AI分析メニュー${NC}"
    echo "1) 対象確認（dry-run）"
    echo "2) 新規データのみ分析"
    echo "3) 全データ強制分析"
    echo "4) 特定ユーザーのみ"
    read -p "選択してください (1-4): " choice
    
    case $choice in
        1)
            python manage.py run_ai_analysis --dry-run
            ;;
        2)
            python manage.py run_ai_analysis --limit 50
            ;;
        3)
            python manage.py run_ai_analysis --force
            ;;
        4)
            read -p "ユーザー名を入力: " username
            python manage.py run_ai_analysis --user "$username"
            ;;
        *)
            echo -e "${RED}❌ 無効な選択です${NC}"
            ;;
    esac
}

# サンプルデータ作成
cmd_sample_data() {
    activate_venv
    echo -e "${YELLOW}📊 サンプルデータ作成中...${NC}"
    python manage.py create_sample_data
    echo -e "${GREEN}✅ サンプルデータ作成完了${NC}"
}

# Djangoシェル
cmd_shell() {
    activate_venv
    echo -e "${BLUE}🐍 Djangoシェル起動${NC}"
    python manage.py shell_plus --ipython
}

# キャッシュ・ログクリア
cmd_clean() {
    echo -e "${YELLOW}🧹 クリーンアップ実行中...${NC}"
    
    # キャッシュクリア
    if [ -d "__pycache__" ]; then
        find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
        echo "✅ Python キャッシュクリア"
    fi
    
    # ログファイルクリア
    if [ -d "logs" ]; then
        > logs/django.log 2>/dev/null || true
        > logs/ai_analysis.log 2>/dev/null || true
        echo "✅ ログファイルクリア"
    fi
    
    # Django キャッシュクリア
    activate_venv
    python manage.py clear_cache 2>/dev/null || echo "Django キャッシュクリア（コマンドが見つからない場合はスキップ）"
    
    echo -e "${GREEN}✅ クリーンアップ完了${NC}"
}

# データベースバックアップ
cmd_backup() {
    activate_venv
    echo -e "${BLUE}💾 データベースバックアップ作成${NC}"
    
    backup_dir="backups"
    mkdir -p "$backup_dir"
    
    timestamp=$(date +"%Y%m%d_%H%M%S")
    backup_file="$backup_dir/db_backup_$timestamp.json"
    
    python manage.py dumpdata --natural-foreign --natural-primary --indent 2 > "$backup_file"
    
    echo -e "${GREEN}✅ バックアップ作成完了: $backup_file${NC}"
}

# データベース復元
cmd_restore() {
    activate_venv
    echo -e "${YELLOW}📥 データベース復元${NC}"
    
    if [ ! -d "backups" ]; then
        echo -e "${RED}❌ backups ディレクトリが見つかりません${NC}"
        return 1
    fi
    
    echo "利用可能なバックアップファイル:"
    ls -la backups/
    
    read -p "復元するファイル名を入力: " backup_file
    
    if [ -f "backups/$backup_file" ]; then
        echo -e "${YELLOW}⚠️  既存データが削除されます。続行しますか？ (y/N)${NC}"
        read confirm
        if [[ $confirm =~ ^[Yy]$ ]]; then
            python manage.py flush --noinput
            python manage.py loaddata "backups/$backup_file"
            echo -e "${GREEN}✅ 復元完了${NC}"
        fi
    else
        echo -e "${RED}❌ ファイルが見つかりません${NC}"
    fi
}

# 依存関係更新
cmd_deps() {
    activate_venv
    echo -e "${BLUE}📦 依存関係更新中...${NC}"
    
    pip install --upgrade pip
    pip install -r requirements.txt
    
    echo -e "${GREEN}✅ 依存関係更新完了${NC}"
}

# コード品質チェック
cmd_lint() {
    activate_venv
    echo -e "${BLUE}🔍 コード品質チェック中...${NC}"
    
    # flake8
    if command -v flake8 &> /dev/null; then
        echo "flake8 チェック..."
        flake8 notebooks/ stock_analysis/ --max-line-length=100 --exclude=migrations
    fi
    
    echo -e "${GREEN}✅ コード品質チェック完了${NC}"
}

# コードフォーマット
cmd_format() {
    activate_venv
    echo -e "${BLUE}✨ コードフォーマット中...${NC}"
    
    # black
    if command -v black &> /dev/null; then
        echo "black フォーマット..."
        black notebooks/ stock_analysis/ --line-length=100 --exclude=migrations
    fi
    
    # isort
    if command -v isort &> /dev/null; then
        echo "isort インポート整理..."
        isort notebooks/ stock_analysis/ --profile=black
    fi
    
    echo -e "${GREEN}✅ コードフォーマット完了${NC}"
}

# ログ確認
cmd_logs() {
    echo -e "${BLUE}📋 ログ確認${NC}"
    echo "1) Django ログ"
    echo "2) AI分析ログ" 
    echo "3) エラーログ"
    echo "4) リアルタイム監視"
    read -p "選択してください (1-4): " choice
    
    case $choice in
        1)
            if [ -f "logs/django.log" ]; then
                tail -50 logs/django.log
            else
                echo -e "${YELLOW}⚠️  ログファイルが見つかりません${NC}"
            fi
            ;;
        2)
            if [ -f "logs/ai_analysis.log" ]; then
                tail -50 logs/ai_analysis.log
            else
                echo -e "${YELLOW}⚠️  ログファイルが見つかりません${NC}"
            fi
            ;;
        3)
            if [ -f "logs/django.log" ]; then
                grep -i "error\|exception\|critical" logs/django.log | tail -20
            fi
            ;;
        4)
            echo "リアルタイム監視中... (Ctrl+C で終了)"
            if [ -f "logs/django.log" ]; then
                tail -f logs/django.log
            fi
            ;;
        *)
            echo -e "${RED}❌ 無効な選択です${NC}"
            ;;
    esac
}

# システム状態確認
cmd_status() {
    echo -e "${BLUE}📊 システム状態確認${NC}"
    echo "=================================="
    
    # Python バージョン
    echo -e "${YELLOW}Python:${NC} $(python3 --version)"
    
    # 仮想環境状態
    if [[ "$VIRTUAL_ENV" != "" ]]; then
        echo -e "${YELLOW}仮想環境:${NC} ✅ 有効 ($VIRTUAL_ENV)"
    else
        echo -e "${YELLOW}仮想環境:${NC} ❌ 無効"
    fi
    
    # データベース状態
    if [ -f "db.sqlite3" ]; then
        db_size=$(ls -lah db.sqlite3 | awk '{print $5}')
        echo -e "${YELLOW}データベース:${NC} ✅ 存在 ($db_size)"
    else
        echo -e "${YELLOW}データベース:${NC} ❌ 未作成"
    fi
    
    # ログファイル状態
    if [ -d "logs" ]; then
        log_count=$(ls logs/ 2>/dev/null | wc -l)
        echo -e "${YELLOW}ログファイル:${NC} $log_count 個"
    else
        echo -e "${YELLOW}ログファイル:${NC} ❌ ディレクトリなし"
    fi
    
    # AI機能状態
    activate_venv 2>/dev/null
    if python -c "from notebooks.ai_analyzer import StockAnalysisAI; print('OK')" 2>/dev/null; then
        echo -e "${YELLOW}AI機能:${NC} ✅ 利用可能"
    else
        echo -e "${YELLOW}AI機能:${NC} ❌ エラーあり"
    fi
    
    echo "=================================="
}

# メイン処理
case "${1:-help}" in
    setup)
        cmd_setup
        ;;
    run)
        cmd_run
        ;;
    migrate)
        cmd_migrate
        ;;
    test)
        cmd_test
        ;;
    ai-analysis)
        cmd_ai_analysis
        ;;
    sample-data)
        cmd_sample_data
        ;;
    shell)
        cmd_shell
        ;;
    clean)
        cmd_clean
        ;;
    backup)
        cmd_backup
        ;;
    restore)
        cmd_restore
        ;;
    deps)
        cmd_deps
        ;;
    lint)
        cmd_lint
        ;;
    format)
        cmd_format
        ;;
    logs)
        cmd_logs
        ;;
    status)
        cmd_status
        ;;
    help|*)
        show_help
        ;;
esac