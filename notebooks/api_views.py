# notebooks/api_views.py
"""
API ビュー（AJAX、REST API用）
"""
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import timedelta
from .models import Notebook, Entry
from .ai_analyzer import StockAnalysisAI
from .calculators import InvestmentCalculator
from .semantic_search import SemanticSearchEngine
from decimal import Decimal
import json

@login_required
@require_http_methods(["GET"])
def search_notebooks_api(request):
    """ノートブック検索API"""
    query = request.GET.get('q', '').strip()
    limit = int(request.GET.get('limit', 5))
    
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    notebooks = Notebook.objects.filter(
        user=request.user
    ).filter(
        title__icontains=query
    ) | Notebook.objects.filter(
        user=request.user
    ).filter(
        company_name__icontains=query
    ) | Notebook.objects.filter(
        user=request.user
    ).filter(
        stock_code__icontains=query
    ) | Notebook.objects.filter(
        user=request.user
    ).filter(
        tags__name__icontains=query
    )
    
    notebooks = notebooks.distinct()[:limit]
    
    results = []
    for notebook in notebooks:
        results.append({
            'id': str(notebook.pk),
            'title': notebook.title,
            'subtitle': notebook.subtitle,
            'stock_code': notebook.stock_code,
            'company_name': notebook.company_name,
            'tags': [tag.name for tag in notebook.tags.all()],
            'updated': notebook.updated_at.strftime('%Y年%m月%d日'),
            'url': notebook.get_absolute_url(),
            'entry_count': notebook.entry_count,
            'current_price': str(notebook.current_price) if notebook.current_price else None,
            'target_price': str(notebook.target_price) if notebook.target_price else None,
        })
    
    return JsonResponse({'results': results})

@login_required
@require_http_methods(["POST"])
def ai_analyze_content_api(request):
    """AI内容分析API"""
    try:
        data = json.loads(request.body)
        content = data.get('content', '')
        title = data.get('title', '')
        
        if not content:
            return JsonResponse({'error': '分析する内容がありません'}, status=400)
        
        analyzer = StockAnalysisAI()
        analysis = analyzer.analyze_content(content, title)
        
        return JsonResponse({
            'success': True,
            'analysis': analysis
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': '不正なJSONデータです'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'分析エラー: {str(e)}'}, status=500)

@login_required
@require_http_methods(["POST"])
def calculate_investment_api(request):
    """投資計算API"""
    try:
        data = json.loads(request.body)
        calc_type = data.get('type')
        
        calculator = InvestmentCalculator()
        
        if calc_type == 'dividend_yield':
            result = calculator.dividend_yield(
                Decimal(str(data.get('annual_dividend', 0))),
                Decimal(str(data.get('stock_price', 0)))
            )
        elif calc_type == 'investment_amount':
            result = calculator.investment_amount(
                Decimal(str(data.get('stock_price', 0))),
                int(data.get('target_shares', 0))
            )
        elif calc_type == 'target_achievement':
            result = calculator.target_achievement(
                Decimal(str(data.get('current_price', 0))),
                Decimal(str(data.get('target_price', 0)))
            )
        elif calc_type == 'portfolio_weight':
            result = calculator.portfolio_weight(
                Decimal(str(data.get('investment_amount', 0))),
                Decimal(str(data.get('total_portfolio', 0)))
            )
        elif calc_type == 'compound_growth':
            result = calculator.compound_growth(
                Decimal(str(data.get('principal', 0))),
                Decimal(str(data.get('annual_rate', 0))),
                int(data.get('years', 0))
            )
        else:
            return JsonResponse({'error': '不正な計算タイプです'}, status=400)
        
        return JsonResponse({
            'success': True,
            'result': result
        })
        
    except (json.JSONDecodeError, ValueError, TypeError) as e:
        return JsonResponse({'error': f'入力データエラー: {str(e)}'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'計算エラー: {str(e)}'}, status=500)

@login_required
@require_http_methods(["GET"])
def dashboard_stats_api(request):
    """ダッシュボード統計API"""
    try:
        user_notebooks = Notebook.objects.filter(user=request.user)
        total_entries = Entry.objects.filter(notebook__user=request.user)
        
        # 統計計算
        stats = {
            'total_notebooks': user_notebooks.count(),
            'active_notebooks': user_notebooks.filter(
                updated_at__gte=timezone.now() - timedelta(days=30)
            ).count(),
            'total_entries': total_entries.count(),
            'monthly_entries': total_entries.filter(
                created_at__gte=timezone.now() - timedelta(days=30)
            ).count(),
        }
        
        # タグ統計
        tag_stats = {}
        for notebook in user_notebooks:
            for tag in notebook.tags.all():
                tag_stats[tag.name] = tag_stats.get(tag.name, 0) + 1
        
        popular_tags = sorted(tag_stats.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return JsonResponse({
            'success': True,
            'stats': stats,
            'popular_tags': [{'name': name, 'count': count} for name, count in popular_tags]
        })
        
    except Exception as e:
        return JsonResponse({'error': f'統計取得エラー: {str(e)}'}, status=500)

@login_required
@require_http_methods(["GET"])
def semantic_search_api(request):
    """セマンティック検索API"""
    try:
        query = request.GET.get('q', '').strip()
        limit = int(request.GET.get('limit', 10))
        
        if len(query) < 2:
            return JsonResponse({
                'success': True,
                'results': [],
                'message': 'クエリが短すぎます'
            })
        
        search_engine = SemanticSearchEngine()
        results = search_engine.semantic_search(query, request.user.id, limit)
        
        return JsonResponse({
            'success': True,
            'results': results,
            'query': query,
            'total_results': len(results)
        })
        
    except Exception as e:
        return JsonResponse({'error': f'セマンティック検索エラー: {str(e)}'}, status=500)

@login_required
@require_http_methods(["GET"])
def related_content_api(request, notebook_id):
    """関連コンテンツ推奨API"""
    try:
        limit = int(request.GET.get('limit', 5))
        
        search_engine = SemanticSearchEngine()
        related_content = search_engine.find_related_content(
            notebook_id, request.user.id, limit
        )
        
        return JsonResponse({
            'success': True,
            'related_content': related_content,
            'notebook_id': notebook_id
        })
        
    except Exception as e:
        return JsonResponse({'error': f'関連コンテンツ取得エラー: {str(e)}'}, status=500)

@login_required
@require_http_methods(["POST"])
def auto_categorize_api(request):
    """自動分類API"""
    try:
        data = json.loads(request.body)
        content = data.get('content', '')
        title = data.get('title', '')
        
        if not content:
            return JsonResponse({'error': '分析する内容がありません'}, status=400)
        
        search_engine = SemanticSearchEngine()
        categorization = search_engine.auto_categorize_content(content, title)
        
        return JsonResponse({
            'success': True,
            'categorization': categorization
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': '不正なJSONデータです'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'自動分類エラー: {str(e)}'}, status=500)

@login_required
@require_http_methods(["GET"])
def ai_insights_api(request, notebook_id):
    """AI洞察・推奨API"""
    try:
        notebook = Notebook.objects.get(pk=notebook_id, user=request.user)
        
        # ノート全体のAI分析
        search_engine = SemanticSearchEngine()
        full_text = search_engine._extract_full_text(notebook)
        
        analyzer = StockAnalysisAI()
        analysis = analyzer.analyze_content(full_text, notebook.title)
        
        # 自動分類
        categorization = search_engine.auto_categorize_content(full_text, notebook.title)
        
        # 関連コンテンツ
        related_content = search_engine.find_related_content(notebook_id, request.user.id, 3)
        
        # 改善提案
        improvement_suggestions = generate_improvement_suggestions(
            notebook, analysis, categorization
        )
        
        return JsonResponse({
            'success': True,
            'notebook_id': notebook_id,
            'ai_analysis': analysis,
            'categorization': categorization,
            'related_content': related_content,
            'improvement_suggestions': improvement_suggestions
        })
        
    except Notebook.DoesNotExist:
        return JsonResponse({'error': 'ノートが見つかりません'}, status=404)
    except Exception as e:
        return JsonResponse({'error': f'AI洞察取得エラー: {str(e)}'}, status=500)

def generate_improvement_suggestions(notebook, analysis, categorization):
    """改善提案生成"""
    suggestions = []
    
    # 分析深度による提案
    if categorization['analysis_depth'] == 'basic':
        suggestions.append({
            'type': 'analysis_depth',
            'title': '分析の詳細化',
            'description': '財務指標や競合比較などの詳細分析を追加することで、より深い洞察が得られます',
            'priority': 'high'
        })
    
    # エントリー数による提案
    if notebook.entry_count < 3:
        suggestions.append({
            'type': 'content_volume',
            'title': '記録の充実',
            'description': '定期的な分析記録の追加により、投資判断の変遷を追跡できます',
            'priority': 'medium'
        })
    
    # タグ活用提案
    current_tags = [tag.name for tag in notebook.tags.all()]
    suggested_tags = analysis.get('suggested_tags', [])
    missing_tags = [tag for tag in suggested_tags if tag not in current_tags]
    
    if missing_tags:
        suggestions.append({
            'type': 'tagging',
            'title': 'タグの追加',
            'description': f'AI推奨タグ「{", ".join(missing_tags[:3])}」の追加を検討してください',
            'priority': 'low'
        })
    
    # 投資戦略明確化提案
    if categorization['investment_strategy'] == 'diversified':
        suggestions.append({
            'type': 'strategy',
            'title': '投資戦略の明確化',
            'description': '具体的な投資戦略（成長投資、配当投資等）を明確にすることで、判断基準が明確になります',
            'priority': 'medium'
        })
    
    return suggestions