# notebooks/semantic_search.py
"""
セマンティック検索・関連コンテンツ推奨機能
"""
import re
import json
from typing import Dict, List, Any, Optional
from collections import Counter
from django.db.models import Q
from .models import Notebook, Entry
from .ai_analyzer import StockAnalysisAI


class SemanticSearchEngine:
    """セマンティック検索エンジン"""
    
    def __init__(self):
        self.analyzer = StockAnalysisAI()
        
        # セマンティックキーワードマッピング
        self.semantic_mappings = {
            '高配当': ['配当', '利回り', 'dividend', '分配金', 'インカムゲイン'],
            '成長株': ['成長', 'グロース', '拡大', '売上増', '利益増', 'growth'],
            '割安株': ['バリュー', '割安', 'PER', 'PBR', '割り負け', 'value'],
            '長期投資': ['長期', 'ホールド', '保有', '継続', 'long term'],
            '短期取引': ['短期', 'トレード', 'デイトレ', 'スイング', 'short term'],
            '決算分析': ['決算', '業績', 'earnings', '売上', '利益', '四半期'],
            'テクニカル': ['チャート', 'technical', 'ローソク足', '移動平均', 'RSI'],
            'ファンダメンタル': ['fundamental', 'ROE', 'ROA', '財務', 'バランスシート'],
            'リスク管理': ['リスク', 'risk', '危険', '注意', '懸念', 'リスクヘッジ'],
        }
        
        # 業界関連キーワード
        self.industry_keywords = {
            '自動車': ['車', 'automotive', 'EV', '電気自動車', 'トヨタ', 'ホンダ'],
            'IT': ['テクノロジー', 'tech', 'ソフトウェア', 'AI', 'クラウド', 'DX'],
            '金融': ['銀行', 'bank', '証券', '保険', 'フィンテック', '投資'],
            '不動産': ['REIT', '不動産', 'real estate', 'マンション', 'オフィス'],
            '製造業': ['製造', 'manufacturing', '工場', '生産', '素材', '部品'],
            '小売': ['retail', '小売', '販売', '店舗', 'EC', 'eコマース'],
            'エネルギー': ['energy', 'エネルギー', '電力', 'ガス', '再生可能'],
            'ヘルスケア': ['healthcare', '医療', '製薬', 'バイオ', '病院'],
        }
    
    def semantic_search(self, query: str, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """セマンティック検索実行"""
        # クエリの正規化
        normalized_query = self._normalize_query(query)
        
        # 拡張キーワード生成
        expanded_keywords = self._expand_query_keywords(normalized_query)
        
        # 基本検索
        basic_results = self._basic_search(expanded_keywords, user_id)
        
        # セマンティックスコア計算
        scored_results = self._calculate_semantic_scores(
            basic_results, normalized_query, expanded_keywords
        )
        
        # 結果の並び替えと制限
        return sorted(scored_results, key=lambda x: x['relevance_score'], reverse=True)[:limit]
    
    def find_related_content(self, notebook_id: str, user_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        """関連コンテンツ推奨"""
        try:
            target_notebook = Notebook.objects.get(pk=notebook_id, user_id=user_id)
        except Notebook.DoesNotExist:
            return []
        
        # ターゲットノートの特徴抽出
        target_features = self._extract_notebook_features(target_notebook)
        
        # 他のノートとの類似度計算
        candidate_notebooks = Notebook.objects.filter(
            user_id=user_id
        ).exclude(pk=notebook_id)
        
        similarity_scores = []
        for notebook in candidate_notebooks:
            candidate_features = self._extract_notebook_features(notebook)
            similarity = self._calculate_similarity(target_features, candidate_features)
            
            if similarity > 0.1:  # 最小類似度閾値
                similarity_scores.append({
                    'notebook': notebook,
                    'similarity_score': similarity,
                    'matching_aspects': self._identify_matching_aspects(
                        target_features, candidate_features
                    )
                })
        
        # 類似度順でソート
        similarity_scores.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        # 結果フォーマット
        return [{
            'notebook_id': str(item['notebook'].pk),
            'title': item['notebook'].title,
            'subtitle': item['notebook'].subtitle,
            'similarity_score': item['similarity_score'],
            'matching_aspects': item['matching_aspects'],
            'tags': [tag.name for tag in item['notebook'].tags.all()],
            'updated_at': item['notebook'].updated_at.isoformat(),
            'url': item['notebook'].get_absolute_url(),
        } for item in similarity_scores[:limit]]
    
    def auto_categorize_content(self, content: str, title: str = "") -> Dict[str, Any]:
        """コンテンツ自動分類"""
        # AI分析実行
        analysis = self.analyzer.analyze_content(content, title)
        
        # 投資戦略分類
        investment_strategy = self._classify_investment_strategy(content, analysis)
        
        # 分析深度評価
        analysis_depth = self._evaluate_analysis_depth(content, analysis)
        
        # コンテンツタイプ分類
        content_type = self._classify_content_type(content, title)
        
        # 推奨アクション
        recommended_actions = self._generate_recommended_actions(
            content, analysis, investment_strategy
        )
        
        return {
            'investment_strategy': investment_strategy,
            'analysis_depth': analysis_depth,
            'content_type': content_type,
            'recommended_actions': recommended_actions,
            'classification_confidence': self._calculate_classification_confidence(
                investment_strategy, analysis_depth, content_type
            )
        }
    
    def _normalize_query(self, query: str) -> str:
        """クエリ正規化"""
        # 記号除去、小文字変換
        normalized = re.sub(r'[^\w\s]', ' ', query.lower())
        return ' '.join(normalized.split())
    
    def _expand_query_keywords(self, query: str) -> List[str]:
        """クエリキーワード拡張"""
        keywords = set(query.split())
        
        # セマンティックマッピングによる拡張
        for main_keyword, synonyms in self.semantic_mappings.items():
            if any(keyword in query for keyword in synonyms):
                keywords.add(main_keyword)
                keywords.update(synonyms)
        
        # 業界キーワード拡張
        for industry, industry_keywords in self.industry_keywords.items():
            if any(keyword in query for keyword in industry_keywords):
                keywords.add(industry)
                keywords.update(industry_keywords)
        
        return list(keywords)
    
    def _basic_search(self, keywords: List[str], user_id: int) -> List[Notebook]:
        """基本検索実行"""
        query_filter = Q()
        
        for keyword in keywords:
            query_filter |= (
                Q(title__icontains=keyword) |
                Q(subtitle__icontains=keyword) |
                Q(company_name__icontains=keyword) |
                Q(stock_code__icontains=keyword) |
                Q(investment_goal__icontains=keyword) |
                Q(risk_factors__icontains=keyword) |
                Q(tags__name__icontains=keyword) |
                Q(entries__title__icontains=keyword) |
                Q(entries__content__icontains=keyword) |
                Q(entries__tags__name__icontains=keyword)
            )
        
        return Notebook.objects.filter(
            user_id=user_id
        ).filter(query_filter).distinct()
    
    def _calculate_semantic_scores(self, notebooks: List[Notebook], 
                                 original_query: str, expanded_keywords: List[str]) -> List[Dict[str, Any]]:
        """セマンティックスコア計算"""
        scored_results = []
        
        for notebook in notebooks:
            # ノート全体のテキスト結合
            full_text = self._extract_full_text(notebook)
            
            # 関連度スコア計算
            relevance_score = self._calculate_relevance_score(
                full_text, original_query, expanded_keywords
            )
            
            # 新しさスコア
            freshness_score = self._calculate_freshness_score(notebook)
            
            # 総合スコア
            final_score = (relevance_score * 0.7) + (freshness_score * 0.3)
            
            scored_results.append({
                'notebook_id': str(notebook.pk),
                'title': notebook.title,
                'subtitle': notebook.subtitle,
                'relevance_score': final_score,
                'content_preview': self._generate_content_preview(full_text, original_query),
                'tags': [tag.name for tag in notebook.tags.all()],
                'updated_at': notebook.updated_at.isoformat(),
                'url': notebook.get_absolute_url(),
                'entry_count': notebook.entry_count,
            })
        
        return scored_results
    
    def _extract_notebook_features(self, notebook: Notebook) -> Dict[str, Any]:
        """ノート特徴抽出"""
        # タグ特徴
        tags = [tag.name for tag in notebook.tags.all()]
        
        # テキスト特徴
        full_text = self._extract_full_text(notebook)
        analysis = self.analyzer.analyze_content(full_text, notebook.title)
        
        # 業界・セクター特徴
        industry_features = self._extract_industry_features(full_text, tags)
        
        # 投資スタイル特徴
        investment_style = self._extract_investment_style(full_text, tags)
        
        return {
            'tags': tags,
            'sentiment': analysis['sentiment'],
            'suggested_tags': analysis['suggested_tags'],
            'keywords': analysis['keywords'],
            'industry_features': industry_features,
            'investment_style': investment_style,
            'stock_mentions': analysis['stock_mentions'],
            'entry_count': notebook.entry_count,
        }
    
    def _calculate_similarity(self, features1: Dict[str, Any], features2: Dict[str, Any]) -> float:
        """特徴ベース類似度計算"""
        scores = []
        
        # タグ類似度
        tags1, tags2 = set(features1['tags']), set(features2['tags'])
        if tags1 or tags2:
            tag_similarity = len(tags1 & tags2) / len(tags1 | tags2)
            scores.append(tag_similarity * 0.3)
        
        # キーワード類似度
        keywords1 = set(features1['keywords'][:5])
        keywords2 = set(features2['keywords'][:5])
        if keywords1 or keywords2:
            keyword_similarity = len(keywords1 & keywords2) / max(len(keywords1 | keywords2), 1)
            scores.append(keyword_similarity * 0.2)
        
        # 投資スタイル類似度
        style1, style2 = features1['investment_style'], features2['investment_style']
        style_similarity = len(set(style1) & set(style2)) / max(len(set(style1) | set(style2)), 1)
        scores.append(style_similarity * 0.3)
        
        # 業界類似度
        industry1, industry2 = features1['industry_features'], features2['industry_features']
        industry_similarity = len(set(industry1) & set(industry2)) / max(len(set(industry1) | set(industry2)), 1)
        scores.append(industry_similarity * 0.2)
        
        return sum(scores) if scores else 0.0
    
    def _classify_investment_strategy(self, content: str, analysis: Dict[str, Any]) -> str:
        """投資戦略分類"""
        content_lower = content.lower()
        tags = analysis.get('suggested_tags', [])
        
        # 戦略パターンマッチング
        if any(tag in ['高配当', '配当', 'dividend'] for tag in tags) or '配当' in content_lower:
            return 'dividend_income'
        elif any(tag in ['成長株', 'グロース', 'growth'] for tag in tags) or '成長' in content_lower:
            return 'growth_investing'
        elif any(tag in ['バリュー投資', '割安', 'value'] for tag in tags) or '割安' in content_lower:
            return 'value_investing'
        elif any(tag in ['短期取引', 'デイトレ', 'トレード'] for tag in tags) or 'トレード' in content_lower:
            return 'short_term_trading'
        elif any(tag in ['長期投資', 'ホールド'] for tag in tags) or '長期' in content_lower:
            return 'long_term_holding'
        else:
            return 'diversified'
    
    def _evaluate_analysis_depth(self, content: str, analysis: Dict[str, Any]) -> str:
        """分析深度評価"""
        depth_score = 0
        
        # 文字数による評価
        if len(content) > 500:
            depth_score += 2
        elif len(content) > 200:
            depth_score += 1
        
        # 数値データの有無
        if re.search(r'\d+[%円ドル万億]', content):
            depth_score += 2
        
        # 分析用語の使用
        analysis_terms = r'per|pbr|roe|eps|売上|利益|配当|成長率|時価総額'
        if re.search(analysis_terms, content, re.IGNORECASE):
            depth_score += 2
        
        # 比較分析
        if re.search(r'前年|同期|比較|対比|vs', content):
            depth_score += 1
        
        # AI分析スコア
        ai_score = analysis.get('analysis_score', 0)
        if ai_score > 80:
            depth_score += 2
        elif ai_score > 50:
            depth_score += 1
        
        # 深度判定
        if depth_score >= 7:
            return 'detailed'
        elif depth_score >= 4:
            return 'moderate'
        else:
            return 'basic'
    
    def _classify_content_type(self, content: str, title: str) -> str:
        """コンテンツタイプ分類"""
        content_lower = content.lower()
        title_lower = title.lower()
        
        if '決算' in content_lower or '業績' in content_lower or 'earnings' in content_lower:
            return 'earnings_analysis'
        elif 'ニュース' in title_lower or '発表' in content_lower or '報道' in content_lower:
            return 'news_analysis'
        elif 'チャート' in content_lower or 'テクニカル' in content_lower or '移動平均' in content_lower:
            return 'technical_analysis'
        elif 'ファンダメンタル' in content_lower or 'per' in content_lower or 'pbr' in content_lower:
            return 'fundamental_analysis'
        elif '計算' in content_lower or '利回り' in content_lower or '投資金額' in content_lower:
            return 'calculation'
        elif 'リスク' in content_lower or '危険' in content_lower or '注意' in content_lower:
            return 'risk_analysis'
        else:
            return 'general_memo'
    
    def _generate_recommended_actions(self, content: str, analysis: Dict[str, Any], 
                                   investment_strategy: str) -> List[str]:
        """推奨アクション生成"""
        actions = []
        
        # 戦略別推奨
        if investment_strategy == 'dividend_income':
            actions.extend([
                "配当利回り計算ツールで現在の利回りを確認",
                "配当性向の安定性を分析",
                "他の高配当銘柄との比較検討"
            ])
        elif investment_strategy == 'growth_investing':
            actions.extend([
                "売上成長率の推移を追跡",
                "競合他社との成長率比較",
                "将来性のある事業領域の分析"
            ])
        elif investment_strategy == 'value_investing':
            actions.extend([
                "PER・PBR等の割安指標確認",
                "同業他社との指標比較",
                "企業の本質的価値分析"
            ])
        
        # 分析深度による推奨
        analysis_score = analysis.get('analysis_score', 0)
        if analysis_score < 50:
            actions.append("より詳細な分析データの追加を検討")
        
        # センチメントによる推奨
        sentiment = analysis.get('sentiment', 'neutral')
        if sentiment == 'negative':
            actions.append("リスク要因の詳細分析を実施")
        elif sentiment == 'positive':
            actions.append("投資タイミングの検討")
        
        return actions[:5]  # 最大5件
    
    def _calculate_classification_confidence(self, investment_strategy: str, 
                                          analysis_depth: str, content_type: str) -> float:
        """分類信頼度計算"""
        confidence_scores = []
        
        # 各分類の確実性評価
        strategy_confidence = 0.8 if investment_strategy != 'diversified' else 0.5
        depth_confidence = {'detailed': 0.9, 'moderate': 0.7, 'basic': 0.5}[analysis_depth]
        type_confidence = 0.8 if content_type != 'general_memo' else 0.4
        
        confidence_scores.extend([strategy_confidence, depth_confidence, type_confidence])
        
        return sum(confidence_scores) / len(confidence_scores)
    
    def _extract_full_text(self, notebook: Notebook) -> str:
        """ノート全文抽出"""
        text_parts = [
            notebook.title or '',
            notebook.subtitle or '',
            notebook.company_name or '',
            notebook.investment_goal or '',
            notebook.risk_factors or '',
        ]
        
        # エントリーのテキスト追加
        for entry in notebook.entries.all()[:10]:  # 最新10件
            text_parts.extend([
                entry.title or '',
                entry.content or '',
            ])
        
        return ' '.join(filter(None, text_parts))
    
    def _calculate_relevance_score(self, text: str, query: str, keywords: List[str]) -> float:
        """関連度スコア計算"""
        text_lower = text.lower()
        query_lower = query.lower()
        
        # 完全一致スコア
        exact_match_score = text_lower.count(query_lower) * 2
        
        # キーワードマッチスコア
        keyword_score = sum(text_lower.count(keyword.lower()) for keyword in keywords)
        
        # 文字数による正規化
        text_length = len(text)
        if text_length > 0:
            normalized_score = (exact_match_score + keyword_score) / (text_length / 1000)
        else:
            normalized_score = 0
        
        return min(normalized_score, 1.0)
    
    def _calculate_freshness_score(self, notebook: Notebook) -> float:
        """新しさスコア計算"""
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        days_ago = (now - notebook.updated_at).days
        
        if days_ago <= 7:
            return 1.0
        elif days_ago <= 30:
            return 0.8
        elif days_ago <= 90:
            return 0.5
        else:
            return 0.2
    
    def _generate_content_preview(self, text: str, query: str) -> str:
        """コンテンツプレビュー生成"""
        # クエリキーワード周辺のテキスト抽出
        text_lower = text.lower()
        query_lower = query.lower()
        
        match_index = text_lower.find(query_lower)
        if match_index != -1:
            start = max(0, match_index - 50)
            end = min(len(text), match_index + len(query) + 50)
            preview = text[start:end].strip()
            return f"...{preview}..." if start > 0 or end < len(text) else preview
        
        # マッチしない場合は先頭から
        return text[:100] + "..." if len(text) > 100 else text
    
    def _extract_industry_features(self, text: str, tags: List[str]) -> List[str]:
        """業界特徴抽出"""
        industries = []
        text_lower = text.lower()
        
        for industry, keywords in self.industry_keywords.items():
            if (industry.lower() in text_lower or 
                any(keyword.lower() in text_lower for keyword in keywords) or
                any(industry.lower() in tag.lower() for tag in tags)):
                industries.append(industry)
        
        return industries
    
    def _extract_investment_style(self, text: str, tags: List[str]) -> List[str]:
        """投資スタイル特徴抽出"""
        styles = []
        text_lower = text.lower()
        
        style_patterns = {
            '高配当投資': ['配当', '利回り', 'dividend'],
            '成長投資': ['成長', 'グロース', 'growth'],
            'バリュー投資': ['バリュー', '割安', 'value'],
            '長期投資': ['長期', 'ホールド', 'long'],
            '短期投資': ['短期', 'トレード', 'short'],
        }
        
        for style, patterns in style_patterns.items():
            if (any(pattern in text_lower for pattern in patterns) or
                any(style.lower() in tag.lower() for tag in tags)):
                styles.append(style)
        
        return styles
    
    def _identify_matching_aspects(self, features1: Dict[str, Any], features2: Dict[str, Any]) -> List[str]:
        """マッチング要素特定"""
        matching_aspects = []
        
        # 共通タグ
        common_tags = set(features1['tags']) & set(features2['tags'])
        if common_tags:
            matching_aspects.append(f"共通タグ: {', '.join(list(common_tags)[:3])}")
        
        # 共通業界
        common_industries = set(features1['industry_features']) & set(features2['industry_features'])
        if common_industries:
            matching_aspects.append(f"同業界: {', '.join(common_industries)}")
        
        # 共通投資スタイル
        common_styles = set(features1['investment_style']) & set(features2['investment_style'])
        if common_styles:
            matching_aspects.append(f"投資スタイル: {', '.join(common_styles)}")
        
        # 類似センチメント
        if features1['sentiment'] == features2['sentiment'] and features1['sentiment'] != 'neutral':
            matching_aspects.append(f"センチメント: {features1['sentiment']}")
        
        return matching_aspects