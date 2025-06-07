from django.test import TestCase

# Create your tests here.
# notebooks/tests.py
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from decimal import Decimal
from .models import Notebook, Entry
from .ai_analyzer import StockAnalysisAI
from .calculators import InvestmentCalculator

class NotebookModelTest(TestCase):
    """ノートブックモデルのテスト"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
    def test_notebook_creation(self):
        """ノートブック作成テスト"""
        notebook = Notebook.objects.create(
            user=self.user,
            title='7203 トヨタ自動車',
            subtitle='長期保有・配当重視',
            stock_code='7203',
            company_name='トヨタ自動車',
            current_price=Decimal('2845.00'),
            target_price=Decimal('3200.00')
        )
        
        self.assertEqual(notebook.title, '7203 トヨタ自動車')
        self.assertEqual(notebook.user, self.user)
        self.assertEqual(notebook.price_change_percent, 12.47)
        
    def test_notebook_str(self):
        """文字列表現テスト"""
        notebook = Notebook.objects.create(
            user=self.user,
            title='テストノート'
        )
        self.assertEqual(str(notebook), 'テストノート')
        
    def test_notebook_absolute_url(self):
        """絶対URL取得テスト"""
        notebook = Notebook.objects.create(
            user=self.user,
            title='テストノート'
        )
        expected_url = f'/notebooks/{notebook.pk}/'
        self.assertEqual(notebook.get_absolute_url(), expected_url)

class EntryModelTest(TestCase):
    """エントリーモデルのテスト"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.notebook = Notebook.objects.create(
            user=self.user,
            title='テストノート'
        )
        
    def test_entry_creation(self):
        """エントリー作成テスト"""
        entry = Entry.objects.create(
            notebook=self.notebook,
            entry_type='analysis',
            title='Q3決算分析',
            content='売上高は前年同期比12%増'
        )
        
        self.assertEqual(entry.notebook, self.notebook)
        self.assertEqual(entry.entry_type, 'analysis')
        self.assertEqual(entry.get_entry_type_display(), '分析')

class ViewsTest(TestCase):
    """ビューのテスト"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
    def test_dashboard_view_anonymous(self):
        """匿名ユーザーダッシュボードアクセステスト"""
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '株式分析ダッシュボード')
        
    def test_dashboard_view_authenticated(self):
        """認証済みユーザーダッシュボードアクセステスト"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        
    def test_notebook_create_requires_login(self):
        """ノート作成にログインが必要"""
        response = self.client.get(reverse('notebook_create'))
        self.assertRedirects(response, '/accounts/login/?next=/notebooks/create/')
        
    def test_notebook_create_view(self):
        """ノート作成ビューテスト"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('notebook_create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '新規ノート作成')
        
    def test_notebook_create_post(self):
        """ノート作成POSTテスト"""
        self.client.login(username='testuser', password='testpass123')
        data = {
            'stock_code': '7203',
            'company_name': 'トヨタ自動車',
            'subtitle': 'テスト投資',
            'current_price': '2845.00',
            'target_price': '3200.00',
            'tags': '高配当,自動車'
        }
        response = self.client.post(reverse('notebook_create'), data)
        self.assertEqual(response.status_code, 302)  # リダイレクト
        
        notebook = Notebook.objects.filter(user=self.user).first()
        self.assertIsNotNone(notebook)
        self.assertEqual(notebook.stock_code, '7203')

class AIAnalyzerTest(TestCase):
    """AI分析機能のテスト"""
    
    def setUp(self):
        self.analyzer = StockAnalysisAI()
        
    def test_stock_detection(self):
        """銘柄検出テスト"""
        content = "トヨタ自動車の決算分析を行いました。"
        analysis = self.analyzer.analyze_content(content)
        
        self.assertIn('7203トヨタ', analysis['stock_mentions'])
        
    def test_tag_extraction(self):
        """タグ抽出テスト"""
        content = "配当利回りが高く、長期投資に適している。決算分析の結果も良好。"
        analysis = self.analyzer.analyze_content(content)
        
        self.assertIn('高配当', analysis['suggested_tags'])
        self.assertIn('長期投資', analysis['suggested_tags'])
        self.assertIn('決算分析', analysis['suggested_tags'])
        
    def test_sentiment_analysis(self):
        """センチメント分析テスト"""
        positive_content = "業績が好調で期待できる。株価上昇の可能性が高い。"
        negative_content = "業績が悪化している。リスクが高い。危険な投資。"
        neutral_content = "普通の決算内容でした。"
        
        positive_analysis = self.analyzer.analyze_content(positive_content)
        negative_analysis = self.analyzer.analyze_content(negative_content)
        neutral_analysis = self.analyzer.analyze_content(neutral_content)
        
        self.assertEqual(positive_analysis['sentiment'], 'positive')
        self.assertEqual(negative_analysis['sentiment'], 'negative')
        self.assertEqual(neutral_analysis['sentiment'], 'neutral')

class CalculatorTest(TestCase):
    """投資計算機能のテスト"""
    
    def setUp(self):
        self.calculator = InvestmentCalculator()
        
    def test_dividend_yield_calculation(self):
        """配当利回り計算テスト"""
        result = self.calculator.dividend_yield(
            Decimal('250'), Decimal('2845')
        )
        
        self.assertAlmostEqual(result['yield_rate'], 8.79, places=2)
        self.assertEqual(result['evaluation'], '高配当（5%以上）')
        
    def test_investment_amount_calculation(self):
        """投資金額計算テスト"""
        result = self.calculator.investment_amount(
            Decimal('2845'), 100
        )
        
        self.assertEqual(result['total_amount'], 284500.0)
        self.assertEqual(result['target_shares'], 100)
        
    def test_target_achievement_calculation(self):
        """目標達成率計算テスト"""
        result = self.calculator.target_achievement(
            Decimal('2845'), Decimal('3200')
        )
        
        self.assertAlmostEqual(result['change_rate'], 12.47, places=2)
        self.assertEqual(result['status'], 'profit')
        
    def test_compound_growth_calculation(self):
        """複利計算テスト"""
        result = self.calculator.compound_growth(
            Decimal('1000000'), Decimal('5'), 10
        )
        
        self.assertAlmostEqual(result['final_amount'], 1628895.0, places=0)
        self.assertEqual(result['years'], 10)

class APITest(TestCase):
    """API機能のテスト"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
    def test_search_api_requires_login(self):
        """検索APIにログインが必要"""
        response = self.client.get('/api/search/?q=test')
        self.assertEqual(response.status_code, 302)  # ログインページへリダイレクト
        
    def test_search_api_with_login(self):
        """認証済み検索APIテスト"""
        self.client.login(username='testuser', password='testpass123')
        
        # テストノート作成
        Notebook.objects.create(
            user=self.user,
            title='7203 トヨタ自動車',
            company_name='トヨタ自動車'
        )
        
        response = self.client.get('/api/search/?q=トヨタ')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(len(data['results']), 1)
        self.assertIn('トヨタ', data['results'][0]['title'])