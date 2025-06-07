# notebooks/api_views.py
"""
API ビュー（AJAX、REST API用）
"""
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from .models import Notebook, Entry
from .ai_analyzer import StockAnalysisAI
from .calculators import InvestmentCalculator
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
