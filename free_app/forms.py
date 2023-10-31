from django import forms

from free_app.models import JournalEntry, Description, AccountingCode, DebitCredit

class JournalEntryForm(forms.ModelForm):
    # https://note.com/ym202110/n/n6b376222f037

    debit_credit = forms.ModelChoiceField(
        queryset=DebitCredit.objects.all(),
        widget=forms.widgets.Select,
        empty_label=None,
    )
    
    # account_code = forms.ModelChoiceField(
    #     queryset=AccountingCode.objects.all(),
    #     widget=forms.widgets.Select,
    #     empty_label=None,
    # )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # https://dot-blog.jp/news/django-readonly-disabled-field/
        self.fields['je_no'].widget.attrs['readonly'] = 'readonly'
        self.fields['row_no'].widget.attrs['readonly'] = 'readonly'
    
    class Meta:
        model = JournalEntry
        fields = ('je_no', 'row_no', 'debit_credit', 'account_code', 'amount')
        labels = {'je_no':'仕訳番号', 'row_no':'行番号', 'debit_credit':'貸借区分', 'account_code':'勘定コード', 'amount':'金額'}

class DescriptionForm(forms.ModelForm):
    class Meta:
        model = Description
        fields = {'description'}


