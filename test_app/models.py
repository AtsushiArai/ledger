from django.db import models

# Create your models here.
class TestModel(models.Model):
    text = models.CharField(max_length=20)


class Member(models.Model):
    name = models.CharField(max_length=100)
    age = models.IntegerField()

DEBIT_CREDIT_CHOICES = [("1", "借方"),("2", "貸方")] # ('DBに記録される値', '表示される値')

class TestJournalEntry(models.Model):
    t_je_no = models.IntegerField('仕訳番号', null=False)
    t_row_no = models.IntegerField('仕訳行番号', null=False)
    t_debit_credit = models.CharField('貸借区分', null=False, max_length=1, choices=DEBIT_CREDIT_CHOICES)
    t_account_code = models.IntegerField('科目コード', null=False)
    t_amount = models.IntegerField('金額（税抜）', null=False, default=0)

    class Meta:
        db_table = 'TestJournalEntry'
