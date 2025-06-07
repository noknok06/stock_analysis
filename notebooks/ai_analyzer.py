# notebooks/ai_analyzer.py
"""
AI分析機能 - 簡易版（外部依存関係最小化）
タグ推奨、セマンティック分析、投資判断支援
"""
import re
import json
from typing import Dict, List, Any
from collections import Counter
from decimal import Decimal

class StockAnalysisAI:
    """株式分析AI - タグ推奨と内容分析（簡易版）"""
    
    def __init__(self):
        # 銘柄パターン（日本の主要銘柄）
        self.stock_patterns = [
            {'pattern': r'7203|トヨタ自動車|toyota', 'stock': '7203トヨタ', 'confidence': 0.95},
            {'pattern': r'6758|ソニー|sony', 'stock': '6758ソニー', 'confidence': 0.95},
            {'pattern': r'9984|ソフトバンク|softbank', 'stock': '9984ソフトバンク', 'confidence': 0.95},
            {'pattern': r'8306|三菱ufj|mufg', 'stock': '8306三菱UFJ', 'confidence': 0.9},
            {'pattern': r'4519|中外製薬', 'stock': '4519中外製薬', 'confidence': 0.9},
            {'pattern': r'2914|JT|日本たばこ', 'stock': '2914JT', 'confidence': 0.9},
            {'pattern': r'9432|NTT', 'stock': '9432NTT', 'confidence': 0.9},
            {'pattern': r'9433|KDDI', 'stock': '9433KDDI', 'confidence': 0.9},
            {'pattern': r'4063|信越化学', 'stock': '4063信越化学', 'confidence': 0.9},
            {'pattern': r'6861|キーエンス', 'stock': '6861キーエンス', 'confidence': 0.9},
        ]
        
        # タグパターン
        self.tag_patterns = [
            {'pattern': r'配当|利回り|dividend', 'tag': '高配当', 'weight': 0.8},
            {'pattern': r'成長|グロース|growth', 'tag': '成長株', 'weight': 0.8},
            {'pattern': r'ev|電気自動車|electric', 'tag': 'EV', 'weight': 0.9},
            {'pattern': r'決算|業績|earnings', 'tag': '決算分析', 'weight': 0.8},
            {'pattern': r'リスク|危険|risk', 'tag': 'リスク管理', 'weight': 0.7},
            {'pattern': r'長期|ホールド|long.term', 'tag': '長期投資', 'weight': 0.7},
            {'pattern': r'短期|デイトレ|short.term', 'tag': '短期取引', 'weight': 0.7},
            {'pattern': r'テクニカル|チャート|technical', 'tag': 'テクニカル', 'weight': 0.8},
            {'pattern': r'ファンダメンタル|fundamental', 'tag': 'ファンダメンタル', 'weight': 0.8},
            {'pattern': r'reit|不動産', 'tag': 'REIT', 'weight': 0.9},
            {'pattern': r'米国|アメリカ|us|usa', 'tag': '米国株', 'weight': 0.8},
            {'pattern': r'競合|比較|competitor', 'tag': '競合分析', 'weight': 0.7},
            {'pattern': r'バリュー|割安|value', 'tag': 'バリュー投資', 'weight': 0.8},
            {'pattern': r'新規上場|ipo', 'tag': 'IPO', 'weight': 0.9},
            {'pattern': r'優待|株主優待', 'tag': '株主優待', 'weight': 0.9},
        ]
        
        # センチメント分析パターン
        self.positive_patterns = r'良い|上昇|成長|利益|好調|期待|強い|優秀|安定|買い|ポジティブ|有望|改善|増加|拡大'
        self.negative_patterns = r'悪い|下落|減少|損失|不調|心配|弱い|危険|不安定|売り|ネガティブ|懸念|悪化|減退'
    
    def analyze_content(self, content: str, title: str = "") -> Dict[str, Any]:
        """
        コンテンツの総合分析
        """
        try:
            text = f"{title} {content}".lower()
            
            # 株式検出
            stock_analysis = self._analyze_stock_mentions(text)
            
            # タグ抽出
            tag_analysis = self._extract_tags(text)
            
            # センチメント分析
            sentiment_analysis = self._analyze_sentiment(text)
            
            # リスク評価
            risk_analysis = self._assess_risk(text)
            
            # キーワード抽出
            keywords = self._extract_keywords(text)
            
            # 投資判断支援
            investment_insights = self._generate_investment_insights(
                text, stock_analysis, tag_analysis, sentiment_analysis
            )
            
            return {
                'suggested_tags': tag_analysis['tags'],
                'stock_mentions': stock_analysis['stocks'],
                'sentiment': sentiment_analysis['sentiment'],
                'confidence': sentiment_analysis['confidence'],
                'risk_level': risk_analysis['level'],
                'keywords': keywords,
                'investment_insights': investment_insights,
                'analysis_score': self._calculate_analysis_score(text)
            }
        except Exception as e:
            # エラー時のフォールバック
            return {
                'suggested_tags': [],
                'stock_mentions': [],
                'sentiment': 'neutral',
                'confidence': 0.0,
                'risk_level': 'unknown',
                'keywords': [],
                'investment_insights': ['分析処理中にエラーが発生しました'],
                'analysis_score': 0
            }
    
    def _analyze_stock_mentions(self, text: str) -> Dict[str, Any]:
        """株式メンション分析"""
        detected_stocks = []
        
        for pattern_data in self.stock_patterns:
            try:
                matches = re.findall(pattern_data['pattern'], text, re.IGNORECASE)
                if matches:
                    detected_stocks.append({
                        'stock': pattern_data['stock'],
                        'confidence': pattern_data['confidence'],
                        'mentions': len(matches)
                    })
            except Exception:
                continue
        
        return {
            'stocks': [s['stock'] for s in detected_stocks],
            'details': detected_stocks
        }
    
    def _extract_tags(self, text: str) -> Dict[str, Any]:
        """タグ抽出"""
        detected_tags = []
        
        for pattern_data in self.tag_patterns:
            try:
                matches = re.findall(pattern_data['pattern'], text, re.IGNORECASE)
                if matches:
                    detected_tags.append({
                        'tag': pattern_data['tag'],
                        'weight': pattern_data['weight'],
                        'mentions': len(matches)
                    })
            except Exception:
                continue
        
        # 重要度順でソート
        detected_tags.sort(key=lambda x: x['weight'] * x['mentions'], reverse=True)
        
        return {
            'tags': [t['tag'] for t in detected_tags[:6]],  # 最大6個
            'details': detected_tags
        }
    
    def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """センチメント分析"""
        try:
            positive_matches = len(re.findall(self.positive_patterns, text, re.IGNORECASE))
            negative_matches = len(re.findall(self.negative_patterns, text, re.IGNORECASE))
            
            if positive_matches > negative_matches + 1:
                sentiment = "positive"
            elif negative_matches > positive_matches + 1:
                sentiment = "negative"
            else:
                sentiment = "neutral"
            
            confidence = min((abs(positive_matches - negative_matches) + 1) / 5, 1.0)
            
            return {
                'sentiment': sentiment,
                'confidence': confidence,
                'scores': {'positive': positive_matches, 'negative': negative_matches}
            }
        except Exception:
            return {
                'sentiment': 'neutral',
                'confidence': 0.0,
                'scores': {'positive': 0, 'negative': 0}
            }
    
    def _assess_risk(self, text: str) -> Dict[str, Any]:
        """リスク評価"""
        try:
            risk_indicators = r'リスク|危険|不安定|暴落|損失|破綻|倒産|規制|競合激化'
            risk_matches = len(re.findall(risk_indicators, text, re.IGNORECASE))
            
            if risk_matches > 2:
                level = "high"
            elif risk_matches > 0:
                level = "medium"
            else:
                level = "low"
            
            return {'level': level, 'mentions': risk_matches}
        except Exception:
            return {'level': 'unknown', 'mentions': 0}
    
    def _extract_keywords(self, text: str) -> List[str]:
        """キーワード抽出（簡易版）"""
        try:
            # 一般的な単語を除外
            common_words = {
                'の', 'は', 'が', 'を', 'に', 'で', 'と', 'から', 'まで', 'より',
                'について', 'として', 'という', 'する', 'した', 'している',
                'です', 'である', 'だと', '思う', '考える', 'ある', 'いる',
                'この', 'その', 'どの', 'これ', 'それ', 'あれ'
            }
            
            # 単語分割（簡易版）
            words = re.findall(r'[ぁ-んァ-ヶー一-龠a-zA-Z0-9]+', text)
            words = [w for w in words if len(w) > 1 and w not in common_words]
            
            # 頻度順でソート
            word_count = Counter(words)
            return [word for word, count in word_count.most_common(8)]
        except Exception:
            return []
    
    def _generate_investment_insights(self, text: str, stock_analysis: Dict, 
                                    tag_analysis: Dict, sentiment_analysis: Dict) -> List[str]:
        """投資判断支援インサイト生成"""
        insights = []
        
        try:
            if len(stock_analysis['stocks']) > 1:
                insights.append("複数銘柄の比較分析が含まれています")
            
            if sentiment_analysis['sentiment'] == 'positive' and sentiment_analysis['confidence'] > 0.7:
                insights.append("ポジティブな投資判断の傾向が見られます")
            elif sentiment_analysis['sentiment'] == 'negative' and sentiment_analysis['confidence'] > 0.7:
                insights.append("リスクに注意した慎重な分析が行われています")
            
            if '決算分析' in tag_analysis['tags']:
                insights.append("決算数値に基づく分析が行われています")
            
            if '長期投資' in tag_analysis['tags'] and '高配当' in tag_analysis['tags']:
                insights.append("長期配当投資戦略の特徴が見られます")
            
            if len(text) > 500:
                insights.append("詳細な分析内容が記録されています")
                
            if not insights:
                insights.append("投資分析の記録として適切な内容です")
        except Exception:
            insights = ["分析処理中にエラーが発生しました"]
        
        return insights
    
    def _calculate_analysis_score(self, text: str) -> int:
        """分析スコア計算（0-100）"""
        try:
            score = 0
            
            # 文字数による加点
            if len(text) > 100:
                score += 20
            if len(text) > 300:
                score += 20
            
            # 数値データの存在
            if re.search(r'\d+[%円ドル]', text):
                score += 15
            
            # 具体的な分析用語
            analysis_terms = r'per|pbr|roe|eps|売上|利益|配当|成長率'
            if re.search(analysis_terms, text, re.IGNORECASE):
                score += 25
            
            # 比較表現
            comparison_terms = r'前年|同期|比較|対比|vs'
            if re.search(comparison_terms, text, re.IGNORECASE):
                score += 20
            
            return min(score, 100)
        except Exception:
            return 0