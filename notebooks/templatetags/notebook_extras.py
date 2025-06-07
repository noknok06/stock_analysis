# notebooks/templatetags/notebook_extras.py
"""
カスタムテンプレートタグ
"""
from django import template
from django.utils.safestring import mark_safe
from django.utils.html import format_html
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


@register.filter
def ai_strategy_label(strategy_code):
    """AI投資戦略の日本語ラベル"""
    labels = {
        'dividend_income': '配当収入',
        'growth_investing': '成長投資',
        'value_investing': 'バリュー投資',
        'short_term_trading': '短期取引',
        'long_term_holding': '長期保有',
        'diversified': '分散投資',
    }
    return labels.get(strategy_code, strategy_code)


@register.filter
def ai_content_type_label(content_type):
    """AIコンテンツタイプの日本語ラベル"""
    labels = {
        'earnings_analysis': '決算分析',
        'news_analysis': 'ニュース分析',
        'technical_analysis': 'テクニカル分析',
        'fundamental_analysis': 'ファンダメンタル分析',
        'calculation': '計算',
        'risk_analysis': 'リスク分析',
        'general_memo': '一般メモ',
    }
    return labels.get(content_type, content_type)


@register.filter
def ai_sentiment_label(sentiment):
    """AIセンチメントの日本語ラベル"""
    labels = {
        'positive': 'ポジティブ',
        'negative': 'ネガティブ',
        'neutral': 'ニュートラル',
    }
    return labels.get(sentiment, sentiment)


@register.simple_tag
def ai_strategy_badge(strategy_code):
    """AI投資戦略バッジ"""
    if not strategy_code:
        return ""
    
    strategy_colors = {
        'dividend_income': 'bg-green-100 text-green-800',
        'growth_investing': 'bg-blue-100 text-blue-800',
        'value_investing': 'bg-yellow-100 text-yellow-800',
        'short_term_trading': 'bg-red-100 text-red-800',
        'long_term_holding': 'bg-purple-100 text-purple-800',
        'diversified': 'bg-gray-100 text-gray-800',
    }
    
    color_class = strategy_colors.get(strategy_code, 'bg-gray-100 text-gray-800')
    label = ai_strategy_label(strategy_code)
    
    return format_html(
        '<span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium {}">{}</span>',
        color_class, label
    )


@register.simple_tag
def ai_sentiment_badge(sentiment):
    """AIセンチメントバッジ"""
    if not sentiment:
        return ""
    
    sentiment_colors = {
        'positive': 'bg-green-100 text-green-800',
        'negative': 'bg-red-100 text-red-800',
        'neutral': 'bg-gray-100 text-gray-800',
    }
    
    color_class = sentiment_colors.get(sentiment, 'bg-gray-100 text-gray-800')
    label = ai_sentiment_label(sentiment)
    
    return format_html(
        '<span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium {}">{}</span>',
        color_class, label
    )


@register.simple_tag
def ai_score_bar(score, width="100px"):
    """AI分析スコアプログレスバー"""
    if not score or score <= 0:
        return ""
    
    if score >= 80:
        color = '#22c55e'  # green
    elif score >= 50:
        color = '#f59e0b'  # amber
    else:
        color = '#ef4444'  # red
    
    return format_html(
        '<div class="flex items-center gap-2">'
        '<div style="width: {}; background: #e5e7eb; border-radius: 4px; height: 16px;">'
        '<div style="width: {}%; background: {}; height: 16px; border-radius: 4px;"></div>'
        '</div>'
        '<span class="text-xs font-medium">{}</span>'
        '</div>',
        width, score, color, score
    )


@register.filter
def ai_analysis_depth_label(depth):
    """AI分析深度の日本語ラベル"""
    labels = {
        'detailed': '詳細',
        'moderate': '中程度',
        'basic': '基本',
    }
    return labels.get(depth, depth)


@register.simple_tag
def ai_depth_indicator(depth):
    """AI分析深度インジケーター"""
    if not depth:
        return ""
    
    depth_colors = {
        'detailed': 'text-green-600',
        'moderate': 'text-yellow-600',
        'basic': 'text-gray-600',
    }
    
    color_class = depth_colors.get(depth, 'text-gray-600')
    label = ai_analysis_depth_label(depth)
    
    return format_html(
        '<span class="inline-flex items-center gap-1 {}"><i data-lucide="brain" class="w-3 h-3"></i>{}</span>',
        color_class, label
    )


@register.filter
def truncate_smart(value, length=100):
    """スマート切り詰め（単語境界を考慮）"""
    if not value or len(value) <= length:
        return value
    
    # 指定長さより短い位置で単語境界を探す
    truncated = value[:length]
    last_space = truncated.rfind(' ')
    
    if last_space > length * 0.8:  # 80%以上の位置にスペースがあれば
        return value[:last_space] + '...'
    else:
        return truncated + '...'


@register.simple_tag
def related_content_count(notebook):
    """関連コンテンツ数を取得"""
    # 実際の実装では SemanticSearchEngine を使用
    # ここでは簡易版
    from ..semantic_search import SemanticSearchEngine
    
    try:
        search_engine = SemanticSearchEngine()
        related = search_engine.find_related_content(str(notebook.pk), notebook.user.id, 5)
        return len(related)
    except:
        return 0


@register.inclusion_tag('notebooks/partials/ai_insights_summary.html')
def render_ai_insights(notebook):
    """AI洞察サマリー表示"""
    return {
        'notebook': notebook,
        'has_ai_data': bool(notebook.ai_analysis_cache),
        'strategy': notebook.ai_investment_strategy,
        'score': notebook.ai_analysis_score,
    }


@register.filter
def confidence_percentage(value):
    """信頼度をパーセンテージ表示"""
    if value is None:
        return "-"
    return f"{int(value * 100)}%"


@register.simple_tag
def ai_last_analyzed_status(last_analyzed):
    """AI最終分析日時のステータス"""
    if not last_analyzed:
        return format_html('<span class="text-gray-500 text-xs">未分析</span>')
    
    from django.utils import timezone
    from datetime import timedelta
    
    now = timezone.now()
    diff = now - last_analyzed
    
    if diff.days == 0:
        status = "最新"
        color = "text-green-600"
    elif diff.days <= 7:
        status = f"{diff.days}日前"
        color = "text-yellow-600"
    else:
        status = "要更新"
        color = "text-red-600"
    
    return format_html('<span class="{} text-xs">{}</span>', color, status)


@register.filter
def highlight_keywords(text, keywords):
    """キーワードをハイライト"""
    if not keywords or not text:
        return text
    
    import re
    
    highlighted = text
    for keyword in keywords[:5]:  # 最大5個まで
        pattern = re.compile(re.escape(keyword), re.IGNORECASE)
        highlighted = pattern.sub(
            f'<mark class="bg-yellow-200 px-1 rounded">{keyword}</mark>',
            highlighted
        )
    
    return mark_safe(highlighted)