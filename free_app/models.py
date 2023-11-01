from django.db import models
from django import forms

# Create your models here.

DEBIT_CREDIT_CHOICES = [("1", "借方"),("2", "貸方")] # ('DBに記録される値', '表示される値')

class DebitCredit(models.Model):
    debit_credit_id = models.IntegerField('貸借区分CD', null=False, primary_key=True)
    debit_credit_name = models.CharField('貸借区分名', null=False, max_length=2)

    class Meta:
        db_table = 'DebitCredit'

    def __str__(self):
        return self.debit_credit_name
    
class AccountingCode(models.Model):
    account_code_id = models.CharField('勘定科目CD', null=False, max_length=5)
    account_name = models.CharField('勘定科目名', null=False, max_length=25)
    classification_code_id = models.CharField('区分CD', null=False, max_length=5)
    classification_name = models.CharField('区分名', null=False, max_length=25)
    fs_display_classification_code_id = models.CharField('決算書表示区分CD', null=False, max_length=5)
    fs_display_classification_name = models.CharField('決算書表示区分名', null=False, max_length=25)
    opening_balance = models.IntegerField('期首残高', null=False)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['account_code_id', 'fs_display_classification_code_id'], name='unique_account_id')]
        db_table = 'AccountingCode'

    def __str__(self):
        return self.account_code_id + ":" + self.account_name

class JournalEntry(models.Model):
    je_no = models.IntegerField('仕訳番号', null=False)
    row_no = models.IntegerField('仕訳行番号', null=False)
    debit_credit = models.CharField('貸借区分', null=False, max_length=2)
    account_code = models.CharField('勘定科目CD', null=False, max_length=30)
    amount = models.IntegerField('金額（税抜）', null=False)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['je_no', 'row_no'], name='unique_je_id')]
        db_table = 'JournalEntry'


class Description(models.Model):
    je_no = models.IntegerField('仕訳番号', null=False, primary_key=True)
    description = models.CharField('摘要', max_length=100)

    class Meta:
        db_table = 'Description'
