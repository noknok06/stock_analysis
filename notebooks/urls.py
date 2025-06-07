# notebooks/urls.py（修正版）
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views, api_views

urlpatterns = [
    # メインページ
    path('', views.dashboard_view, name='dashboard'),
    
    # ノートブック関連（intに変更）
    path('notebooks/', views.notebook_list_view, name='notebook_list'),
    path('notebooks/create/', views.notebook_create_view, name='notebook_create'),
    path('notebooks/<int:pk>/', views.notebook_detail_view, name='notebook_detail'),
    path('notebooks/<int:pk>/edit/', views.notebook_edit_view, name='notebook_edit'),
    
    # エントリー関連（引数名をnotebook_pkに統一）
    path('notebooks/<int:notebook_pk>/entries/create/', views.entry_create_view, name='entry_create'),
    
    # ツール
    path('calculator/', views.calculator_view, name='calculator'),
    
    # API エンドポイント（intに変更）
    path('api/search/', api_views.search_notebooks_api, name='search_api'),
    path('api/search/semantic/', api_views.semantic_search_api, name='semantic_search_api'),
    path('api/ai/analyze/', api_views.ai_analyze_content_api, name='ai_analyze_api'),
    path('api/ai/categorize/', api_views.auto_categorize_api, name='auto_categorize_api'),
    path('api/related/<int:notebook_id>/', api_views.related_content_api, name='related_content_api'),
    path('api/insights/<int:notebook_id>/', api_views.ai_insights_api, name='ai_insights_api'),
    path('api/calculate/', api_views.calculate_investment_api, name='calculate_api'),
    path('api/stats/', api_views.dashboard_stats_api, name='stats_api'),
    
    # 認証
    path('accounts/register/', views.register_view, name='register'),
    path('accounts/login/', views.CustomLoginView.as_view(), name='login'),
    path('accounts/logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('accounts/password_change/', auth_views.PasswordChangeView.as_view(
        template_name='registration/password_change.html',
        success_url='/'
    ), name='password_change'),
    path('accounts/password_reset/', auth_views.PasswordResetView.as_view(
        template_name='registration/password_reset.html'
    ), name='password_reset'),
]