# notebooks/middleware.py
"""
カスタムミドルウェア
"""
from django.utils.deprecation import MiddlewareMixin
from django.contrib import messages
import logging

logger = logging.getLogger(__name__)

class ErrorHandlingMiddleware(MiddlewareMixin):
    """エラーハンドリングミドルウェア"""
    
    def process_exception(self, request, exception):
        """例外処理"""
        if request.user.is_authenticated:
            logger.error(f"User {request.user.username} encountered error: {exception}")
        else:
            logger.error(f"Anonymous user encountered error: {exception}")
        
        # 本番環境では詳細なエラーを表示しない
        if not request.user.is_staff:
            messages.error(request, 'システムエラーが発生しました。しばらく後でもう一度お試しください。')
        
        return None
