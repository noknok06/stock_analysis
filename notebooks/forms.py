# notebooks/forms.py
from django import forms
from django.forms.widgets import TextInput
from .models import Notebook, Entry

class NotebookForm(forms.ModelForm):
    """ノートブック作成・編集フォーム"""
    
    class Meta:
        model = Notebook
        fields = [
            'stock_code', 'company_name', 'subtitle', 'investment_goal',
            'current_price', 'target_price', 'risk_factors', 'tags'
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
        self.fields['tags'].widget.attrs.update({
            'class': 'tw-input',
            'placeholder': 'タグをカンマ区切りで入力（例: 高配当,自動車,長期投資）'
        })
    
    def save(self, commit=True, user=None):
        notebook = super().save(commit=False)
        if user:
            notebook.user = user
        if notebook.stock_code and notebook.company_name:
            notebook.title = f"{notebook.stock_code} {notebook.company_name}"
        if commit:
            notebook.save()
            self.save_m2m()
        return notebook

class EntryForm(forms.ModelForm):
    """エントリー作成・編集フォーム"""
    
    class Meta:
        model = Entry
        fields = ['entry_type', 'title', 'content', 'tags']
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
        self.fields['tags'].widget.attrs.update({
            'class': 'tw-input',
            'placeholder': 'タグをカンマ区切りで入力'
        })
