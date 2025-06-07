# notebooks/tests.py（AI機能完全テスト版）
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from decimal import Decimal
import json
from .models import Notebook, Entry
from .ai_analyzer import StockAnalysisAI
from .calculators import InvestmentCalculator
from .semantic_search import SemanticSearchEngine


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
    
    def test_ai_analysis_update(self):
        """AI分析結果更新テスト"""
        notebook = Notebook.objects.create(
            user=self.user,
            title='テストノート'
        )
        
        analysis_data = {
            'suggested_tags': ['高配当', '長期投資'],
            'sentiment': 'positive',
            'analysis_score': 85,
            'keywords': ['配当', '投資']
        }
        
        notebook.update_ai_analysis(analysis_data)
        
        self.assertEqual(notebook.ai_analysis_score, 85)
        self.assertEqual(notebook.ai_investment_strategy, 'dividend_income')
        self.assertIsNotNone(notebook.ai_last_analyzed)
        self.assertEqual(notebook.ai_analysis_cache, analysis_data)


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
    
    def test_ai_analysis_update(self):
        """エントリーAI分析更新テスト"""
        entry = Entry.objects.create(
            notebook=self.notebook,
            entry_type='analysis',
            title='決算分析',
            content='決算が好調で配当も増配'
        )
        
        analysis_data = {
            'suggested_tags': ['決算分析', '高配当'],
            'sentiment': 'positive',
            'analysis_score': 75
        }
        
        entry.update_ai_analysis(analysis_data)
        
        self.assertEqual(entry.ai_analysis_score, 75)
        self.assertEqual(entry.ai_sentiment, 'positive')
        self.assertEqual(entry.ai_content_type, 'earnings_analysis')


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
    
    def test_analysis_score_calculation(self):
        """分析スコア計算テスト"""
        detailed_content = """
        トヨタ自動車（7203）の2023年第3四半期決算分析。
        売上高は前年同期比15%増の8.9兆円、営業利益は18%増の2.1兆円。
        ROEは9.2%、PERは12.5倍と適正水準。
        配当利回りは2.8%で安定している。
        北米市場での販売が好調で、EVシフトも順調。
        """
        
        basic_content = "トヨタの株を買いました。"
        
        detailed_analysis = self.analyzer.analyze_content(detailed_content)
        basic_analysis = self.analyzer.analyze_content(basic_content)
        
        # 詳細分析の方がスコアが高いはず
        self.assertGreater(detailed_analysis['analysis_score'], basic_analysis['analysis_score'])
        self.assertGreater(detailed_analysis['analysis_score'], 50)


class SemanticSearchTest(TestCase):
    """セマンティック検索のテスト"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.search_engine = SemanticSearchEngine()
        
        # テストデータ作成
        self.notebook1 = Notebook.objects.create(
            user=self.user,
            title='7203 トヨタ自動車',
            subtitle='高配当・長期投資',
            investment_goal='安定配当を重視した長期投資戦略'
        )
        self.notebook1.tags.add('高配当', '自動車', '長期投資')
        
        self.notebook2 = Notebook.objects.create(
            user=self.user,
            title='6758 ソニー',
            subtitle='成長株投資',
            investment_goal='エンタメ事業の成長性に注目'
        )
        self.notebook2.tags.add('成長株', 'IT', 'エンタメ')
    
    def test_semantic_search(self):
        """セマンティック検索テスト"""
        results = self.search_engine.semantic_search(
            "配当が安定している銘柄", self.user.id, 5
        )
        
        # トヨタが上位に来るはず
        self.assertGreater(len(results), 0)
        top_result = results[0]
        self.assertIn('トヨタ', top_result['title'])
    
    def test_related_content_recommendation(self):
        """関連コンテンツ推奨テスト"""
        related = self.search_engine.find_related_content(
            str(self.notebook1.pk), self.user.id, 3
        )
        
        # 現在は1つしかノートがないので、関連なし
        self.assertEqual(len(related), 0)
        
        # 類似ノート追加
        similar_notebook = Notebook.objects.create(
            user=self.user,
            title='8766 東京海上HD',
            subtitle='配当重視投資',
            investment_goal='配当利回りの高い金融株'
        )
        similar_notebook.tags.add('高配当', '金融', '長期投資')
        
        related = self.search_engine.find_related_content(
            str(self.notebook1.pk), self.user.id, 3
        )
        
        self.assertGreater(len(related), 0)
    
    def test_auto_categorization(self):
        """自動分類テスト"""
        content = "配当利回り5%の高配当株を長期保有する戦略"
        categorization = self.search_engine.auto_categorize_content(content)
        
        self.assertEqual(categorization['investment_strategy'], 'dividend_income')
        self.assertIn('high', categorization['classification_confidence'])


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
    
    def test_error_handling(self):
        """エラーハンドリングテスト"""
        # ゼロ除算エラー
        result = self.calculator.dividend_yield(
            Decimal('250'), Decimal('0')
        )
        self.assertIn('error', result)
        
        # 負の値エラー
        result = self.calculator.investment_amount(
            Decimal('-100'), 10
        )
        self.assertIn('error', result)


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
    
    def test_ai_analyze_api(self):
        """AI分析APIテスト"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post(
            '/api/ai/analyze/',
            data=json.dumps({
                'content': 'トヨタ自動車の配当が増配され、長期投資に適している',
                'title': '分析メモ'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('suggested_tags', data['analysis'])
        self.assertIn('sentiment', data['analysis'])
    
    def test_semantic_search_api(self):
        """セマンティック検索APIテスト"""
        self.client.login(username='testuser', password='testpass123')
        
        # テストデータ作成
        notebook = Notebook.objects.create(
            user=self.user,
            title='高配当株投資',
            investment_goal='配当利回りの高い株式への投資'
        )
        notebook.tags.add('高配当', '長期投資')
        
        response = self.client.get('/api/search/semantic/?q=配当が安定した投資')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('results', data)
    
    def test_auto_categorize_api(self):
        """自動分類APIテスト"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post(
            '/api/ai/categorize/',
            data=json.dumps({
                'content': '決算発表で売上高が前年比20%増。成長が期待できる。',
                'title': '決算分析'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('categorization', data)
        self.assertIn('investment_strategy', data['categorization'])
    
    def test_calculation_api(self):
        """計算APIテスト"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post(
            '/api/calculate/',
            data=json.dumps({
                'type': 'dividend_yield',
                'annual_dividend': 250,
                'stock_price': 2845
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('result', data)
        self.assertIn('yield_rate', data['result'])


class IntegrationTest(TestCase):
    """統合テスト"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
    def test_full_workflow(self):
        """完全なワークフローテスト"""
        self.client.login(username='testuser', password='testpass123')
        
        # 1. ノート作成
        notebook_data = {
            'stock_code': '7203',
            'company_name': 'トヨタ自動車',
            'subtitle': '高配当・長期投資',
            'investment_goal': '安定配当を重視した長期投資',
            'current_price': '2845.00',
            'target_price': '3200.00',
            'tags': '高配当,自動車,長期投資'
        }
        
        response = self.client.post(reverse('notebook_create'), notebook_data)
        self.assertEqual(response.status_code, 302)
        
        notebook = Notebook.objects.filter(user=self.user).first()
        self.assertIsNotNone(notebook)
        
        # 2. エントリー作成
        entry_data = {
            'entry_type': 'analysis',
            'title': 'Q3決算分析',
            'content': '売上高は前年同期比12%増の8.9兆円。営業利益も順調に成長。配当も安定している。',
            'tags': '決算分析,業績好調'
        }
        
        response = self.client.post(
            reverse('entry_create', args=[notebook.pk]), 
            entry_data
        )
        self.assertEqual(response.status_code, 302)
        
        entry = Entry.objects.filter(notebook=notebook).first()
        self.assertIsNotNone(entry)
        
        # 3. AI分析の確認
        response = self.client.get(f'/api/insights/{notebook.pk}/')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('ai_analysis', data)
        
        # 4. セマンティック検索
        response = self.client.get('/api/search/semantic/?q=配当が安定している銘柄')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertTrue(data['success'])
        
        # 5. 計算ツール使用
        response = self.client.post(
            '/api/calculate/',
            data=json.dumps({
                'type': 'dividend_yield',
                'annual_dividend': 250,
                'stock_price': 2845
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])


class PerformanceTest(TestCase):
    """パフォーマンステスト"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # 大量のテストデータ作成
        for i in range(50):
            notebook = Notebook.objects.create(
                user=self.user,
                title=f'テストノート{i}',
                subtitle=f'テスト投資戦略{i}',
                investment_goal=f'投資目標{i}の説明文'
            )
            notebook.tags.add(f'タグ{i}', f'カテゴリ{i % 5}')
            
            # エントリー作成
            for j in range(5):
                Entry.objects.create(
                    notebook=notebook,
                    title=f'エントリー{j}',
                    content=f'テスト内容{j} ' * 20  # ある程度の長さ
                )
    
    def test_search_performance(self):
        """検索パフォーマンステスト"""
        import time
        
        search_engine = SemanticSearchEngine()
        
        start_time = time.time()
        results = search_engine.semantic_search('テスト', self.user.id, 10)
        end_time = time.time()
        
        # 1秒以内に完了することを確認
        self.assertLess(end_time - start_time, 1.0)
        self.assertGreater(len(results), 0)
    
    def test_ai_analysis_performance(self):
        """AI分析パフォーマンステスト"""
        import time
        
        analyzer = StockAnalysisAI()
        content = "テスト内容 " * 100  # 長いコンテンツ
        
        start_time = time.time()
        analysis = analyzer.analyze_content(content)
        end_time = time.time()
        
        # 2秒以内に完了することを確認
        self.assertLess(end_time - start_time, 2.0)
        self.assertIn('suggested_tags', analysis)


# テストデータファクトリー
class NotebookFactory:
    """テストデータ作成ファクトリー"""
    
    @staticmethod
    def create_sample_notebook(user, stock_code='7203', company_name='トヨタ自動車'):
        """サンプルノートブック作成"""
        notebook = Notebook.objects.create(
            user=user,
            title=f'{stock_code} {company_name}',
            subtitle='テスト投資戦略',
            stock_code=stock_code,
            company_name=company_name,
            investment_goal='テスト用の投資目標',
            current_price=Decimal('2845.00'),
            target_price=Decimal('3200.00')
        )
        notebook.tags.add('テスト', '高配当', '長期投資')
        return notebook
    
    @staticmethod
    def create_sample_entry(notebook, entry_type='analysis'):
        """サンプルエントリー作成"""
        entry = Entry.objects.create(
            notebook=notebook,
            entry_type=entry_type,
            title='テストエントリー',
            content='テスト用の分析内容。売上が増加し、配当も安定している。'
        )
        entry.tags.add('テスト', '決算分析')
        return entry


# カスタムテストケース基底クラス
class AITestCase(TestCase):
    """AI機能テスト用基底クラス"""
    
    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.analyzer = StockAnalysisAI()
        self.search_engine = SemanticSearchEngine()
        self.calculator = InvestmentCalculator()
    
    def assertAIAnalysisValid(self, analysis):
        """AI分析結果の妥当性チェック"""
        required_keys = [
            'suggested_tags', 'sentiment', 'confidence', 
            'keywords', 'analysis_score'
        ]
        for key in required_keys:
            self.assertIn(key, analysis, f'{key} がAI分析結果に含まれていません')
        
        self.assertIn(analysis['sentiment'], ['positive', 'negative', 'neutral'])
        self.assertGreaterEqual(analysis['confidence'], 0)
        self.assertLessEqual(analysis['confidence'], 1)
        self.assertGreaterEqual(analysis['analysis_score'], 0)
        self.assertLessEqual(analysis['analysis_score'], 100)
    
    def assertSemanticSearchValid(self, results):
        """セマンティック検索結果の妥当性チェック"""
        self.assertIsInstance(results, list)
        for result in results:
            required_keys = [
                'notebook_id', 'title', 'relevance_score', 
                'content_preview', 'tags'
            ]
            for key in required_keys:
                self.assertIn(key, result, f'{key} が検索結果に含まれていません')
            
            self.assertGreaterEqual(result['relevance_score'], 0)
            self.assertLessEqual(result['relevance_score'], 1)