# notebooks/models.py
from django.db import models
from django.contrib.auth.models import User
from taggit.managers import TaggableManager
import uuid

class Notebook(models.Model):
    """ノートブック（銘柄分析ノート）"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, verbose_name="タイトル")
    subtitle = models.CharField(max_length=300, blank=True, verbose_name="サブタイトル")
    stock_code = models.CharField(max_length=10, blank=True, verbose_name="銘柄コード")
    company_name = models.CharField(max_length=100, blank=True, verbose_name="企業名")
    
    # 投資目標
    investment_goal = models.TextField(blank=True, verbose_name="投資理由・戦略")
    current_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="現在価格")
    target_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="目標価格")
    risk_factors = models.TextField(blank=True, verbose_name="リスク要因")
    
    # メタデータ
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    entry_count = models.IntegerField(default=0, verbose_name="エントリー数")
    is_public = models.BooleanField(default=False, verbose_name="公開")
    
    # タグ
    tags = TaggableManager(verbose_name="タグ")
    
    class Meta:
        ordering = ['-updated_at']
        verbose_name = "ノートブック"
        verbose_name_plural = "ノートブック"
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('notebook_detail', kwargs={'pk': self.pk})
    
    @property
    def price_change_percent(self):
        """目標価格との差分パーセント"""
        if self.current_price and self.target_price:
            return ((self.target_price - self.current_price) / self.current_price) * 100
        return 0

class Entry(models.Model):
    """記録エントリー"""
    ENTRY_TYPES = [
        ('analysis', '分析'),
        ('earnings', '決算情報'),
        ('news', 'ニュース'),
        ('calculation', '計算結果'),
        ('memo', 'メモ'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    notebook = models.ForeignKey(Notebook, on_delete=models.CASCADE, related_name='entries')
    entry_type = models.CharField(max_length=20, choices=ENTRY_TYPES, default='memo', verbose_name="エントリータイプ")
    title = models.CharField(max_length=200, blank=True, verbose_name="タイトル")
    content = models.TextField(verbose_name="内容")
    metadata = models.JSONField(default=dict, blank=True, verbose_name="メタデータ")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # タグ
    tags = TaggableManager(verbose_name="タグ")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "エントリー"
        verbose_name_plural = "エントリー"
    
    def __str__(self):
        return f"{self.notebook.title} - {self.title or 'エントリー'}"

