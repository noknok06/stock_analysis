# notebooks/calculators.py
"""
投資計算ツール集
"""
from decimal import Decimal, getcontext, ROUND_HALF_UP
from typing import Dict, Any, Optional

# 精度設定
getcontext().prec = 10

class InvestmentCalculator:
    """投資計算ツール"""
    
    @staticmethod
    def dividend_yield(annual_dividend: Decimal, stock_price: Decimal) -> Dict[str, Any]:
        """配当利回り計算"""
        if stock_price <= 0:
            return {'error': '株価は0より大きい値を入力してください'}
        
        yield_rate = (annual_dividend / stock_price * 100).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )
        
        return {
            'yield_rate': float(yield_rate),
            'annual_dividend': float(annual_dividend),
            'stock_price': float(stock_price),
            'monthly_dividend': float(annual_dividend / 12),
            'evaluation': InvestmentCalculator._evaluate_dividend_yield(yield_rate)
        }
    
    @staticmethod
    def investment_amount(stock_price: Decimal, target_shares: int) -> Dict[str, Any]:
        """投資金額計算"""
        if stock_price <= 0:
            return {'error': '株価は0より大きい値を入力してください'}
        if target_shares <= 0:
            return {'error': '株数は0より大きい値を入力してください'}
        
        total_amount = (stock_price * target_shares).quantize(
            Decimal('1'), rounding=ROUND_HALF_UP
        )
        
        # 手数料計算（仮定: 0.1%、最低100円）
        commission = max(total_amount * Decimal('0.001'), Decimal('100'))
        total_cost = total_amount + commission
        
        return {
            'stock_price': float(stock_price),
            'target_shares': target_shares,
            'total_amount': float(total_amount),
            'commission': float(commission),
            'total_cost': float(total_cost),
            'per_share_cost': float(total_cost / target_shares)
        }
    
    @staticmethod
    def target_achievement(current_price: Decimal, target_price: Decimal) -> Dict[str, Any]:
        """目標達成率計算"""
        if current_price <= 0:
            return {'error': '現在価格は0より大きい値を入力してください'}
        if target_price <= 0:
            return {'error': '目標価格は0より大きい値を入力してください'}
        
        change_amount = target_price - current_price
        change_rate = (change_amount / current_price * 100).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )
        
        return {
            'current_price': float(current_price),
            'target_price': float(target_price),
            'change_amount': float(change_amount),
            'change_rate': float(change_rate),
            'status': 'profit' if change_rate > 0 else 'loss' if change_rate < 0 else 'break_even',
            'evaluation': InvestmentCalculator._evaluate_target_achievement(change_rate)
        }
    
    @staticmethod
    def portfolio_weight(investment_amount: Decimal, total_portfolio: Decimal) -> Dict[str, Any]:
        """ポートフォリオ構成比計算"""
        if total_portfolio <= 0:
            return {'error': 'ポートフォリオ総額は0より大きい値を入力してください'}
        if investment_amount < 0:
            return {'error': '投資金額は0以上の値を入力してください'}
        
        weight = (investment_amount / total_portfolio * 100).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )
        
        return {
            'investment_amount': float(investment_amount),
            'total_portfolio': float(total_portfolio),
            'weight': float(weight),
            'remaining_amount': float(total_portfolio - investment_amount),
            'evaluation': InvestmentCalculator._evaluate_portfolio_weight(weight)
        }
    
    @staticmethod
    def compound_growth(principal: Decimal, annual_rate: Decimal, years: int) -> Dict[str, Any]:
        """複利計算"""
        if principal <= 0:
            return {'error': '元本は0より大きい値を入力してください'}
        if years <= 0:
            return {'error': '期間は0より大きい値を入力してください'}
        
        rate_decimal = annual_rate / 100
        final_amount = principal * (1 + rate_decimal) ** years
        total_gain = final_amount - principal
        
        # 年次詳細
        yearly_breakdown = []
        current_amount = principal
        for year in range(1, min(years + 1, 11)):  # 最大10年まで表示
            current_amount = current_amount * (1 + rate_decimal)
            yearly_breakdown.append({
                'year': year,
                'amount': float(current_amount.quantize(Decimal('1'), rounding=ROUND_HALF_UP))
            })
        
        return {
            'principal': float(principal),
            'annual_rate': float(annual_rate),
            'years': years,
            'final_amount': float(final_amount.quantize(Decimal('1'), rounding=ROUND_HALF_UP)),
            'total_gain': float(total_gain.quantize(Decimal('1'), rounding=ROUND_HALF_UP)),
            'gain_rate': float((total_gain / principal * 100).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            'yearly_breakdown': yearly_breakdown
        }
    
    @staticmethod
    def _evaluate_dividend_yield(yield_rate: Decimal) -> str:
        """配当利回り評価"""
        if yield_rate >= 5:
            return "高配当（5%以上）"
        elif yield_rate >= 3:
            return "中配当（3-5%）"
        elif yield_rate >= 1:
            return "低配当（1-3%）"
        else:
            return "無配当級（1%未満）"
    
    @staticmethod
    def _evaluate_target_achievement(change_rate: Decimal) -> str:
        """目標達成評価"""
        if change_rate >= 50:
            return "大幅上昇期待"
        elif change_rate >= 20:
            return "上昇期待"
        elif change_rate >= 5:
            return "小幅上昇期待"
        elif change_rate >= -5:
            return "ほぼ適正価格"
        elif change_rate >= -20:
            return "小幅下落リスク"
        else:
            return "大幅下落リスク"
    
    @staticmethod
    def _evaluate_portfolio_weight(weight: Decimal) -> str:
        """ポートフォリオ構成比評価"""
        if weight >= 30:
            return "集中投資（30%以上）"
        elif weight >= 20:
            return "主力投資（20-30%）"
        elif weight >= 10:
            return "中核投資（10-20%）"
        elif weight >= 5:
            return "分散投資（5-10%）"
        else:
            return "少額投資（5%未満）"