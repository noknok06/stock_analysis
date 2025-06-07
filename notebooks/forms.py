# notebooks/forms.py（修正版）
from django import forms
from django.forms.widgets import TextInput
from taggit.forms import TagWidget
from .models import Notebook, Entry

class NotebookForm(forms.ModelForm):
    """ノートブック作成・編集フォーム"""
    
    # タグフィールドをCharFieldとして定義し、保存時に手動処理
    tags = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'tw-input',
            'placeholder': 'タグをカンマ区切りで入力（例: 高配当,自動車,長期投資）'
        }),
        help_text='タグをカンマ区切りで入力してください'
    )
    
    class Meta:
        model = Notebook
        fields = [
            'stock_code', 'company_name', 'subtitle', 'investment_goal',
            'current_price', 'target_price', 'risk_factors'
        ]
        widgets = {
            'stock_code': forms.TextInput(attrs={
                'class': 'tw-input',
                'placeholder': '例: 7203'
            }),
            'company_name': forms.TextInput(attrs={
                'class': 'tw-input',
                'placeholder': '例: トヨタ自動車'
            }),
            'subtitle': forms.TextInput(attrs={
                'class': 'tw-input',
                'placeholder': '例: 長期保有・配当重視'
            }),
            'investment_goal': forms.Textarea(attrs={
                'class': 'tw-textarea',
                'rows': 3,
                'placeholder': '例: 安定配当を重視した長期投資。自動車業界のリーダーとして持続的成長を期待。'
            }),
            'current_price': forms.NumberInput(attrs={
                'class': 'tw-input',
                'placeholder': '例: 2845',
                'step': '0.01'
            }),
            'target_price': forms.NumberInput(attrs={
                'class': 'tw-input',
                'placeholder': '例: 3200',
                'step': '0.01'
            }),
            'risk_factors': forms.Textarea(attrs={
                'class': 'tw-textarea',
                'rows': 2,
                'placeholder': '例: EV移行リスク、為替変動、半導体不足'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 既存のインスタンスがある場合、タグを文字列として表示
        if self.instance and self.instance.pk:
            self.fields['tags'].initial = ', '.join([tag.name for tag in self.instance.tags.all()])
    
    def save(self, commit=True, user=None):
        notebook = super().save(commit=False)
        if user:
            notebook.user = user
        if notebook.stock_code and notebook.company_name:
            notebook.title = f"{notebook.stock_code} {notebook.company_name}"
        
        if commit:
            notebook.save()
            # タグの処理
            tags_str = self.cleaned_data.get('tags', '')
            if tags_str:
                tag_names = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
                notebook.tags.set(tag_names)
            else:
                notebook.tags.clear()
        
        return notebook

class EntryForm(forms.ModelForm):
    """エントリー作成・編集フォーム"""
    
    # タグフィールドをCharFieldとして定義
    tags = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'tw-input',
            'placeholder': 'タグをカンマ区切りで入力'
        }),
        help_text='タグをカンマ区切りで入力してください'
    )
    
    class Meta:
        model = Entry
        fields = ['entry_type', 'title', 'content']
        widgets = {
            'entry_type': forms.Select(attrs={'class': 'tw-select'}),
            'title': forms.TextInput(attrs={
                'class': 'tw-input',
                'placeholder': '例: Q3決算分析'
            }),
            'content': forms.Textarea(attrs={
                'class': 'tw-textarea',
                'rows': 6,
                'placeholder': '例: 売上高は前年同期比12%増の8.9兆円。営業利益は15%増の2.1兆円と好調。北米市場での販売増が寄与。'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 既存のインスタンスがある場合、タグを文字列として表示
        if self.instance and self.instance.pk:
            self.fields['tags'].initial = ', '.join([tag.name for tag in self.instance.tags.all()])
    
    def save(self, commit=True):
        entry = super().save(commit=commit)
        
        if commit:
            # タグの処理
            tags_str = self.cleaned_data.get('tags', '')
            if tags_str:
                tag_names = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
                entry.tags.set(tag_names)
            else:
                entry.tags.clear()
        
        return entry