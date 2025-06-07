# notebooks/templatetags/notebook_extras.py
"""
カスタムテンプレートタグ
"""
from django import template
from django.utils.safestring import mark_safe
from ..utils import format_price, format_percentage, calculate_days_ago
import json

register = template.Library()

@register.filter
def format_currency(value):
    """通貨フォーマット"""
    return format_price(value)

@register.filter
def format_percent(value):
    """パーセンテージフォーマット"""
    return format_percentage(value)

@register.filter
def days_ago(date):
    """〜前の表示"""
    return calculate_days_ago(date)

@register.filter
def json_encode(obj):
    """JSON エンコード"""
    return mark_safe(json.dumps(obj))

@register.simple_tag
def price_change_class(current_price, target_price):
    """価格変動クラス"""
    if not current_price or not target_price:
        return ""
    
    if target_price > current_price:
        return "text-green-600"
    elif target_price < current_price:
        return "text-red-600"
    else:
        return "text-gray-600"

@register.inclusion_tag('notebooks/partials/tag_list.html')
def render_tags(tags, max_display=5):
    """タグリスト表示"""
    return {
        'tags': tags[:max_display],
        'remaining_count': max(0, len(tags) - max_display)
    }

@register.inclusion_tag('notebooks/partials/price_display.html')
def render_price_info(notebook):
    """価格情報表示"""
    return {'notebook': notebook}