from django import forms
from .models import Member, TestJournalEntry

class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = '__all__'
        labels = {'name': '名前', 'age': '年齢'}

class TestJournalEntryForm(forms.ModelForm):
    class Meta:
        model = TestJournalEntry
        fields = ('t_je_no', 't_row_no', 't_debit_credit', 't_account_code', 't_amount')
        labels = {'t_je_no':'仕訳番号', 't_row_no':'行番号', 't_debit_credit':'貸借区分', 't_account_code':'勘定コード', 't_amount':'金額'}
        
