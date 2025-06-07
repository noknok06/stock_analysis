# notebooks/context_processors.py
"""
カスタムコンテキストプロセッサ
"""
from .utils import get_market_data_cache

def app_context(request):
    """アプリケーション共通コンテキスト"""
    return {
        'app_name': '株式分析記録アプリ',
        'app_version': '1.0.0',
        'market_data': get_market_data_cache(),
    }