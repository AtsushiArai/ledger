from django.contrib import admin

from import_export import resources
from import_export.admin import ImportExportModelAdmin
from import_export.fields import Field
from import_export.widgets import ForeignKeyWidget

from free_app.models import JournalEntry, AccountingCode, DebitCredit, Description

# Register your models here.

# -------------- 摘要 ----------------------
@admin.register(Description)
class Description(admin.ModelAdmin):
    list_display = ('je_no', 'description')

# -------------- 仕訳明細（一括インポート、エクスポート機能を追加） ----------------------
# https://note.com/nssystems/n/n7cb1339f2a2c
class JournalEntryResource(resources.ModelResource):

    class Meta:
        model = JournalEntry

@admin.register(JournalEntry)
class JournalEntryAdmin(ImportExportModelAdmin):
    resource_class = JournalEntryResource
    ordering = ['je_no']
    list_display = ('je_no', 'row_no', 'debit_credit', 'account_code', 'amount')


# -------------- 科目コード（一括インポート、エクスポート機能を追加） ----------------------
class AccountingCodeResource(resources.ModelResource):
    class Meta:
        model = AccountingCode
        skip_unchanged = True
        use_bulk = True

@admin.register(AccountingCode)
class AccountingCodeAdmin(ImportExportModelAdmin):
    resource_class = AccountingCodeResource
    ordering = ['account_code_id']
    list_display = ('account_code_id', 'account_name', 'opening_balance')


# -------------- 貸借区分 ----------------------
@admin.register(DebitCredit)
class DebitCredit(admin.ModelAdmin):
    list_display = ("debit_credit_id", 'debit_credit_name')

