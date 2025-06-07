# notebooks/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import Notebook, Entry
import json


@admin.register(Notebook)
class NotebookAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'user', 'stock_code', 'current_price', 'target_price', 
        'entry_count', 'ai_analysis_score', 'ai_investment_strategy', 'updated_at'
    ]
    list_filter = [
        'created_at', 'updated_at', 'is_public', 'ai_investment_strategy',
        'ai_last_analyzed'
    ]
    search_fields = ['title', 'company_name', 'stock_code', 'user__username']
    readonly_fields = [
        'created_at', 'updated_at', 'entry_count', 'ai_analysis_cache_display',
        'ai_analysis_score', 'ai_investment_strategy', 'ai_last_analyzed'
    ]
    
    fieldsets = (
        ('基本情報', {
            'fields': ('user', 'title', 'subtitle', 'stock_code', 'company_name')
        }),
        ('投資目標', {
            'fields': ('investment_goal', 'current_price', 'target_price', 'risk_factors')
        }),
        ('AI分析結果', {
            'fields': (
                'ai_analysis_score', 'ai_investment_strategy', 'ai_last_analyzed',
                'ai_analysis_cache_display'
            ),
            'classes': ('collapse',)
        }),
        ('メタデータ', {
            'fields': ('entry_count', 'is_public', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def ai_analysis_cache_display(self, obj):
        """AI分析キャッシュの見やすい表示"""
        if obj.ai_analysis_cache:
            formatted_json = json.dumps(obj.ai_analysis_cache, indent=2, ensure_ascii=False)
            return format_html('<pre style="white-space: pre-wrap;">{}</pre>', formatted_json)
        return "分析データなし"
    ai_analysis_cache_display.short_description = "AI分析詳細"
    
    def ai_investment_strategy(self, obj):
        """投資戦略の色分け表示"""
        strategy_colors = {
            'dividend_income': '#22c55e',  # green
            'growth_investing': '#3b82f6',  # blue
            'value_investing': '#f59e0b',  # amber
            'short_term_trading': '#ef4444',  # red
            'long_term_holding': '#8b5cf6',  # violet
            'diversified': '#6b7280',  # gray
        }
        
        strategy_labels = {
            'dividend_income': '配当収入',
            'growth_investing': '成長投資',
            'value_investing': 'バリュー投資',
            'short_term_trading': '短期取引',
            'long_term_holding': '長期保有',
            'diversified': '分散投資',
        }
        
        if obj.ai_investment_strategy:
            color = strategy_colors.get(obj.ai_investment_strategy, '#6b7280')
            label = strategy_labels.get(obj.ai_investment_strategy, obj.ai_investment_strategy)
            return format_html(
                '<span style="color: {}; font-weight: bold;">{}</span>',
                color, label
            )
        return "-"
    ai_investment_strategy.short_description = "AI推定戦略"
    
    def ai_analysis_score(self, obj):
        """分析スコアのプログレスバー表示"""
        score = obj.ai_analysis_score
        if score > 0:
            color = '#22c55e' if score >= 80 else '#f59e0b' if score >= 50 else '#ef4444'
            return format_html(
                '<div style="width: 100px; background: #e5e7eb; border-radius: 4px;">'
                '<div style="width: {}%; background: {}; height: 16px; border-radius: 4px; '
                'text-align: center; color: white; font-size: 12px; line-height: 16px;">{}</div></div>',
                score, color, score
            )
        return "-"
    ai_analysis_score.short_description = "AI分析スコア"


@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'notebook', 'entry_type', 'ai_content_type', 'ai_sentiment', 
        'ai_analysis_score', 'created_at'
    ]
    list_filter = [
        'entry_type', 'ai_content_type', 'ai_sentiment', 'created_at'
    ]
    search_fields = ['title', 'content', 'notebook__title']
    readonly_fields = [
        'created_at', 'updated_at', 'ai_analysis_cache_display',
        'ai_content_type', 'ai_sentiment', 'ai_analysis_score'
    ]
    
    fieldsets = (
        ('基本情報', {
            'fields': ('notebook', 'entry_type', 'title', 'content')
        }),
        ('AI分析結果', {
            'fields': (
                'ai_content_type', 'ai_sentiment', 'ai_analysis_score',
                'ai_analysis_cache_display'
            ),
            'classes': ('collapse',)
        }),
        ('メタデータ', {
            'fields': ('metadata', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def ai_analysis_cache_display(self, obj):
        """AI分析キャッシュの見やすい表示"""
        if obj.ai_analysis_cache:
            formatted_json = json.dumps(obj.ai_analysis_cache, indent=2, ensure_ascii=False)
            return format_html('<pre style="white-space: pre-wrap;">{}</pre>', formatted_json)
        return "分析データなし"
    ai_analysis_cache_display.short_description = "AI分析詳細"
    
    def ai_content_type(self, obj):
        """コンテンツタイプの表示"""
        type_labels = {
            'earnings_analysis': '決算分析',
            'news_analysis': 'ニュース分析',
            'technical_analysis': 'テクニカル分析',
            'fundamental_analysis': 'ファンダメンタル分析',
            'calculation': '計算',
            'risk_analysis': 'リスク分析',
            'general_memo': '一般メモ',
        }
        
        if obj.ai_content_type:
            label = type_labels.get(obj.ai_content_type, obj.ai_content_type)
            return format_html('<span style="font-weight: bold;">{}</span>', label)
        return "-"
    ai_content_type.short_description = "AI推定タイプ"
    
    def ai_sentiment(self, obj):
        """センチメントの色分け表示"""
        sentiment_colors = {
            'positive': '#22c55e',
            'negative': '#ef4444',
            'neutral': '#6b7280',
        }
        
        sentiment_labels = {
            'positive': 'ポジティブ',
            'negative': 'ネガティブ',
            'neutral': 'ニュートラル',
        }
        
        if obj.ai_sentiment:
            color = sentiment_colors.get(obj.ai_sentiment, '#6b7280')
            label = sentiment_labels.get(obj.ai_sentiment, obj.ai_sentiment)
            return format_html(
                '<span style="color: {}; font-weight: bold;">{}</span>',
                color, label
            )
        return "-"
    ai_sentiment.short_description = "AI感情分析"
    
    def ai_analysis_score(self, obj):
        """分析スコアのプログレスバー表示"""
        score = obj.ai_analysis_score
        if score > 0:
            color = '#22c55e' if score >= 80 else '#f59e0b' if score >= 50 else '#ef4444'
            return format_html(
                '<div style="width: 80px; background: #e5e7eb; border-radius: 4px;">'
                '<div style="width: {}%; background: {}; height: 14px; border-radius: 4px; '
                'text-align: center; color: white; font-size: 11px; line-height: 14px;">{}</div></div>',
                score, color, score
            )
        return "-"
    ai_analysis_score.short_description = "AI分析スコア"


# 管理画面のカスタマイズ
admin.site.site_header = "株式分析記録アプリ 管理画面"
admin.site.site_title = "株式分析記録アプリ"
admin.site.index_title = "管理画面ホーム"