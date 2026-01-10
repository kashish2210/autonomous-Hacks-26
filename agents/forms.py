from django import forms

class ClaimsExtractorForm(forms.Form):
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            "rows": 10,
            "placeholder": "Enter a long text here..."
        }),
        label="Text Content"
    )
