# notebooks/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import timedelta
from .models import Notebook, Entry
from .forms import NotebookForm, EntryForm
from taggit.models import Tag
from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib import messages
from .ai_analyzer import StockAnalysisAI
from .calculators import InvestmentCalculator
from .utils import get_market_data_cache

def dashboard_view(request):
    """統合ダッシュボード"""
    # 統計データの計算
    if request.user.is_authenticated:
        user_notebooks = Notebook.objects.filter(user=request.user)
        total_notebooks = user_notebooks.count()
        active_notebooks = user_notebooks.filter(
            updated_at__gte=timezone.now() - timedelta(days=30)
        ).count()
        total_entries = Entry.objects.filter(notebook__user=request.user).count()
        monthly_entries = Entry.objects.filter(
            notebook__user=request.user,
            created_at__gte=timezone.now() - timedelta(days=30)
        ).count()
        
        # 最近のノート
        recent_notebooks = user_notebooks[:6]
    else:
        total_notebooks = active_notebooks = total_entries = monthly_entries = 0
        recent_notebooks = []
    
    # 市場データ（模擬データ）
    market_data = [
        {'name': '日経平均', 'value': '33,486.89', 'change': '+156.32', 'change_percent': '+0.47%'},
        {'name': 'TOPIX', 'value': '2,418.56', 'change': '+8.94', 'change_percent': '+0.37%'},
        {'name': 'USD/JPY', 'value': '149.85', 'change': '+0.23', 'change_percent': '+0.15%'},
    ]
    
    # 人気タグ
    popular_tags = Tag.objects.annotate(
        usage_count=Count('taggit_taggeditem_items')
    ).order_by('-usage_count')[:8]
    
    context = {
        'stats': {
            'total_notebooks': total_notebooks,
            'active_notebooks': active_notebooks,
            'total_entries': total_entries,
            'monthly_entries': monthly_entries,
        },
        'recent_notebooks': recent_notebooks,
        'market_data': market_data,
        'popular_tags': popular_tags,
    }
    return render(request, 'notebooks/dashboard.html', context)

@login_required
def notebook_list_view(request):
    """ノート一覧"""
    notebooks = Notebook.objects.filter(user=request.user)
    
    # 検索機能
    search_query = request.GET.get('search', '')
    if search_query:
        notebooks = notebooks.filter(
            Q(title__icontains=search_query) |
            Q(company_name__icontains=search_query) |
            Q(stock_code__icontains=search_query) |
            Q(tags__name__icontains=search_query)
        ).distinct()
    
    # ページネーション
    paginator = Paginator(notebooks, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
    }
    return render(request, 'notebooks/list.html', context)

@login_required
def notebook_create_view(request):
    """ノート作成"""
    if request.method == 'POST':
        form = NotebookForm(request.POST)
        if form.is_valid():
            try:
                notebook = form.save(user=request.user)
                messages.success(request, f'ノート「{notebook.title}」を作成しました。')
                return redirect('notebook_detail', pk=notebook.pk)
            except Exception as e:
                messages.error(request, f'エラーが発生しました: {str(e)}')
        else:
            messages.error(request, 'フォームに不正な値があります。')
    else:
        form = NotebookForm()
    
    # おすすめタグ
    suggested_tags = [
        '高配当', '成長株', '長期投資', '自動車', 'IT', '金融', 
        '小売', '製造業', '決算分析', 'テクニカル'
    ]
    
    context = {
        'form': form,
        'suggested_tags': suggested_tags,
    }
    return render(request, 'notebooks/create.html', context)

@login_required
def notebook_detail_view(request, pk):
    """ノート詳細"""
    notebook = get_object_or_404(Notebook, pk=pk, user=request.user)
    entries = notebook.entries.all()
    
    # ページネーション
    paginator = Paginator(entries, 10)
    page_number = request.GET.get('page')
    entries_page = paginator.get_page(page_number)
    
    context = {
        'notebook': notebook,
        'entries_page': entries_page,
    }
    return render(request, 'notebooks/detail.html', context)

@login_required
def notebook_edit_view(request, pk):
    """ノート編集"""
    notebook = get_object_or_404(Notebook, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = NotebookForm(request.POST, instance=notebook)
        if form.is_valid():
            try:
                notebook = form.save()
                messages.success(request, f'ノート「{notebook.title}」を更新しました。')
                return redirect('notebook_detail', pk=notebook.pk)
            except Exception as e:
                messages.error(request, f'エラーが発生しました: {str(e)}')
    else:
        form = NotebookForm(instance=notebook)
    
    context = {
        'form': form,
        'notebook': notebook,
    }
    return render(request, 'notebooks/edit.html', context)

@login_required
def entry_create_view(request, notebook_pk):
    """エントリー作成"""
    notebook = get_object_or_404(Notebook, pk=notebook_pk, user=request.user)
    
    if request.method == 'POST':
        form = EntryForm(request.POST)
        if form.is_valid():
            try:
                entry = form.save(commit=False)
                entry.notebook = notebook
                entry.save()
                form.save_m2m()
                
                # ノートのエントリー数更新
                notebook.entry_count = notebook.entries.count()
                notebook.save()
                
                messages.success(request, 'エントリーを作成しました。')
                return redirect('notebook_detail', pk=notebook.pk)
            except Exception as e:
                messages.error(request, f'エラーが発生しました: {str(e)}')
    else:
        form = EntryForm()
    
    context = {
        'form': form,
        'notebook': notebook,
    }
    return render(request, 'notebooks/entry_create.html', context)

def search_api_view(request):
    """検索API（AJAX用）"""
    query = request.GET.get('q', '')
    if not query or len(query) < 2:
        return JsonResponse({'results': []})
    
    if request.user.is_authenticated:
        notebooks = Notebook.objects.filter(
            user=request.user
        ).filter(
            Q(title__icontains=query) |
            Q(company_name__icontains=query) |
            Q(stock_code__icontains=query) |
            Q(tags__name__icontains=query)
        ).distinct()[:5]
        
        results = [{
            'id': str(notebook.pk),
            'title': notebook.title,
            'subtitle': notebook.subtitle,
            'tags': [tag.name for tag in notebook.tags.all()],
            'updated': notebook.updated_at.strftime('%Y年%m月%d日'),
            'url': notebook.get_absolute_url(),
        } for notebook in notebooks]
    else:
        results = []
    
    return JsonResponse({'results': results})

@login_required
def calculator_view(request):
    """投資計算ツールページ"""
    context = {
        'page_title': '投資計算ツール',
    }
    return render(request, 'notebooks/calculator.html', context)

def register_view(request):
    """ユーザー登録"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                messages.success(request, f'アカウント「{user.username}」を作成しました。ログインしてください。')
                return redirect('login')
            except Exception as e:
                messages.error(request, f'登録エラー: {str(e)}')
        else:
            messages.error(request, 'フォームに不正な値があります。')
    else:
        form = UserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})

class CustomLoginView(auth_views.LoginView):
    """カスタムログインビュー"""
    template_name = 'registration/login.html'
    
    def get_success_url(self):
        return '/'
    
    def form_invalid(self, form):
        messages.error(self.request, 'ユーザー名またはパスワードが正しくありません。')
        return super().form_invalid(form)

class CustomLogoutView(auth_views.LogoutView):
    """カスタムログアウトビュー"""
    
    def dispatch(self, request, *args, **kwargs):
        messages.success(request, 'ログアウトしました。')
        return super().dispatch(request, *args, **kwargs)