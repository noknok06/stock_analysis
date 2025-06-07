    # notebooks/utils.py
"""
ユーティリティ関数集
"""
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
import hashlib
import json

def generate_cache_key(prefix: str, *args) -> str:
    """キャッシュキー生成"""
    key_data = f"{prefix}:{'_'.join(map(str, args))}"
    return hashlib.md5(key_data.encode()).hexdigest()

def get_market_data_cache():
    """市場データ取得（キャッシュ付き）"""
    cache_key = 'market_data'
    data = cache.get(cache_key)
    
    if data is None:
        # 実際のAPIコールの代わりに模擬データ
        data = [
            {'name': '日経平均', 'value': '33,486.89', 'change': '+156.32', 'change_percent': '+0.47%'},
            {'name': 'TOPIX', 'value': '2,418.56', 'change': '+8.94', 'change_percent': '+0.37%'},
            {'name': 'USD/JPY', 'value': '149.85', 'change': '+0.23', 'change_percent': '+0.15%'},
        ]
        # 5分間キャッシュ
        cache.set(cache_key, data, 300)
    
    return data

def format_price(price):
    """価格フォーマット"""
    if price is None:
        return "-"
    return f"¥{price:,.0f}"

def format_percentage(value):
    """パーセンテージフォーマット"""
    if value is None:
        return "-"
    return f"{value:+.1f}%"

def calculate_days_ago(date):
    """日数計算"""
    now = timezone.now()
    diff = now - date
    
    if diff.days == 0:
        hours = diff.seconds // 3600
        if hours == 0:
            minutes = diff.seconds // 60
            return f"{minutes}分前"
        return f"{hours}時間前"
    elif diff.days == 1:
        return "昨日"
    elif diff.days < 7:
        return f"{diff.days}日前"
    elif diff.days < 30:
        weeks = diff.days // 7
        return f"{weeks}週間前"
    else:
        months = diff.days // 30
        return f"{months}ヶ月前"