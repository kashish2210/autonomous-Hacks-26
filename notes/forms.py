# notes/forms.py
from django import forms
from .models import Claim, NewsReport


class ClaimForm(forms.ModelForm):
    """Form for creating/editing claims"""
    
    class Meta:
        model = Claim
        fields = [
            'title',
            'content',
            'source_url',
            'source_type',
            'status',
            'verification_notes',
            'language',
            'tags'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter claim title'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Enter full claim content'
            }),
            'source_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://example.com/article'
            }),
            'source_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'verification_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Add verification notes, sources, or context'
            }),
            'language': forms.Select(attrs={
                'class': 'form-select'
            }),
            'tags': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'politics, economy, health (comma-separated)'
            })
        }


class NewsReportForm(forms.ModelForm):
    """Form for generating news reports"""
    
    claim_ids = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        required=True
    )
    
    class Meta:
        model = NewsReport
        fields = ['title', 'format_type', 'language']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter report title'
            }),
            'format_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'language': forms.Select(attrs={
                'class': 'form-select'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate claim choices from database
        self.fields['claim_ids'].choices = [
            (claim.id, claim.title) 
            for claim in Claim.objects.filter(is_archived=False)
        ]