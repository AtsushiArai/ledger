from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from django import forms
from django.http import HttpResponse
from django.db import models

from django_pandas.io import read_frame

import pandas as pd

from free_app.models import JournalEntry, Description, AccountingCode
from free_app.forms import JournalEntryForm, DescriptionForm

# Create your views here.

# FORM_NUM = 1
# FORM_VALUES = {}

# https://en-junior.com/formset_add/
# 仕訳行を追加したときに行番号がインクリメントされる機能をつけたかったけど、うまくいかなかったので一旦コメントアウト。
# class IndexView(FormView):
#     template_name = 'free_app/journal.html'
#     success_url = reverse_lazy('index')
#     JournalEntryFormSet = forms.formset_factory(
#         form = JournalEntryForm,
#         extra = 1,
#         max_num = 10,
#     )
#     form_class = JournalEntryFormSet

#     def get_form_kwargs(self):
#         # デフォルトのget_form_kwargsメソッドを呼び出す
#         kwargs = super().get_form_kwargs()
#         # FORM_VALUESがからでない場合（入力中のフォームがある場合）、dataキーにFORM_VALUESを設定
#         if FORM_VALUES and 'btn_add' in FORM_VALUES:
#             kwargs['data'] = FORM_VALUES
#         return kwargs
    
#     def post(self, request, *args, **kwargs):
#         global FORM_NUM
#         global FORM_VALUES
#         # 追加ボタンが押された時の挙動
#         if 'btn_add' in request.POST:
#             FORM_NUM += 1 # フォーム数をインクリメント
#             FORM_VALUES = request.POST.copy() # リクエストの内容をコピー
#             FORM_VALUES['form-TOTAL_FORMS'] = FORM_NUM # フォーム数を上書き

#         return super().post(request, args, kwargs)


def journalentry(request):

    if request.method == 'POST':
        # POSTの場合には入力されている仕訳がDBにセーブされる。
        # 値は request.POST.getlist('xxx')で抽出する。getlistは抽出対象を指定しないとエラーになる。
        # https://office54.net/python/django/views-request-post
        form_je = JournalEntryForm(request.POST)
        form_de = DescriptionForm(request.POST)

        if form_je.is_valid() and form_de.is_valid():
            posted_je_no = request.POST.getlist('je_no')
            posted_row_no = request.POST.getlist('row_no')
            posted_debit_credit = request.POST.getlist('debit_credit')
            posted_account_code = request.POST.getlist('account_code')
            if posted_debit_credit == 1:
                posted_amount = request.POST.getlist('amount')
            else:
                posted_amount = request.POST.getlist('amount')

            for i in range(0, len(posted_account_code)):

                journal = JournalEntry(je_no = int(posted_je_no[0]),
                                       row_no = posted_row_no[i],
                                       debit_credit = posted_debit_credit[i],
                                       account_code = posted_account_code[i],
                                       amount = posted_amount[i],
                                       )
                journal.created_by = request.user
                journal.save()

            description = form_de.save(commit=False)
            description.je_no = posted_je_no[0]
            description.created_by = request.user
            description.save()

            return redirect("/")
        
        je_data = JournalEntry.objects.values_list('je_no', flat=True)
        try:
            pre_je_no = max(je_data)
        except:
            pre_je_no = 0
        je_no = pre_je_no + 1
        initial_values = {'je_no':je_no}

        je_form = JournalEntryForm(initial_values)
        description_form = DescriptionForm()

    else:
        # GETの場合には仕訳入力フォームを表示する。仕訳番号はDBから最新の値を取得する。
        # 1.フォーム名をキー、初期値を値とした辞書型のオブジェクトを作成
        # 2.フォームクラスの引数に作成したオブジェクトを渡す
        # 3.コンテキストでフォームクラスをHTMLテンプレートへ渡す
        je_data = JournalEntry.objects.values_list('je_no', flat=True)
        try:
            pre_je_no = max(je_data)
        except:
            pre_je_no = 0
        je_no = pre_je_no + 1
        initial_values_1 = {'je_no':je_no, 'row_no':1}
        initial_values_2 = {'je_no':je_no, 'row_no':2}


        # 仕訳番号のデフォルト値を反映させてformを作成する。
        je_form_1 = JournalEntryForm(initial_values_1)
        je_form_2 = JournalEntryForm(initial_values_2)
        description_form = DescriptionForm()




    return render(request, "free_app/journal.html", {'je_form_1':je_form_1,
                                                     'je_form_2':je_form_2,
                                                      'description_form':description_form})

    # 仕訳行追加ボタンが押された時に、仕訳行を1行追加するコードを書く。
# def test(request):
#     TestModelFormSet = forms.modelformset_factory(
#             model=JournalEntry,
#             fields=('je_no', 'row_no', 'debit_credit', 'account_code', 'amount'),
#             extra=1,
#     )
#     if request.method == 'POST':
#         formset = TestModelFormSet(request.POST,queryset=JournalEntry.objects.none()) 
#         if formset.is_valid():
#             formset.save()  # データベースに保存します。
#             # チェック用にデータベース上の全データを表示してみます。
#             data = [x.text for x in JournalEntry.objects.all()]
#             return HttpResponse(repr(data))
#     else:
#         formset = TestModelFormSet(queryset=JournalEntry.objects.none())

#     description_form = DescriptionForm()

#     return render(request, 'free_app/journal_test.html', {'formset': formset, 'description_form':description_form})

def make_trial_balance():
    # DBから必要な情報を取得する
    acc = AccountingCode.objects.all()
    journal_debit = JournalEntry.objects.filter(debit_credit=1).values('account_code', 'amount')
    journal_credit = JournalEntry.objects.filter(debit_credit=2).values('account_code', 'amount')

    # テーブルにまとめる
    df_acc_table = read_frame(acc)
    df_journal_debit_table = read_frame(journal_debit)
    df_journal_credit_table = read_frame(journal_credit)

    # 仕訳の借方・貸方をそれぞれ科目ごとに集計する。
    df_journal_debit_table = df_journal_debit_table.groupby('account_code').sum()
    df_journal_credit_table = df_journal_credit_table.groupby('account_code').sum()

    # TBのDataframeの作成
    df_tb = pd.DataFrame(columns=['科目コード','科目名','区分CD', '区分名', '決算書表示区分CD', '決算書表示区分名', '期首残高', '借方', '貸方', '期末残高'])
    df_tb = df_tb.astype({'科目コード': str})
    df_tb = df_tb.astype({'科目名': str})
    df_tb = df_tb.astype({'区分CD': str})
    df_tb = df_tb.astype({'区分名': str})
    df_tb = df_tb.astype({'決算書表示区分CD': str})
    df_tb = df_tb.astype({'決算書表示区分名': str})
    df_tb = df_tb.astype({'期首残高': int})
    df_tb = df_tb.astype({'借方': int})
    df_tb = df_tb.astype({'貸方': int})
    df_tb = df_tb.astype({'期末残高': int})

    # 科目名、科目コードをTBに移す。
    df_tb['科目コード'] = df_acc_table['account_code']
    df_tb['科目名'] = df_acc_table['account_name']
    df_tb['区分CD'] = df_acc_table['classification_code']
    df_tb['区分名'] = df_acc_table['classification_name']
    df_tb['決算書表示区分CD'] = df_acc_table['fs_display_classification_code']
    df_tb['決算書表示区分名'] = df_acc_table['fs_display_classification_name']
    df_tb['期首残高'] = df_acc_table['opening_balance']
    df_tb['借方'] = 0
    df_tb['貸方'] = 0
    df_tb['期末残高'] = 0


    # 仕訳の借方、貸方をTBに埋め込む。
    col = df_tb['科目コード'].tolist()

    for c in col:
        if c in df_journal_debit_table.index.to_list():
            v = df_journal_debit_table.at[c, 'amount']
            loc = list(df_tb['科目コード']).index(c)
            df_tb.at[loc, '借方'] = v

        if c in df_journal_credit_table.index.to_list():
            v = df_journal_credit_table.at[c, 'amount']
            if v > 0:
                v = v * -1
            loc = list(df_tb['科目コード']).index(c)
            df_tb.at[loc, '貸方'] = v

    # TBの期末残高を計算し、期末残高列に値を入れる。
    for index, row in df_tb.iterrows():
        df_tb.at[index, '期末残高'] += row['期首残高'] + row['借方'] + row['貸方']

    return df_tb

def make_balance_sheet():
    # 試算表の作成
    df_tb = make_trial_balance()

    # 当期純利益の算定
    profit_loss = 0
    for index, row in df_tb.iterrows():
        if str(row['区分CD'])[0:2] in ['B2']:
            profit_loss += row['期末残高']
    
    # TBの利益剰余金に当期純利益額を反映させる
    for index, row in df_tb.iterrows():
        if str(row['科目コード']) == "A1808":
            df_tb.at[index, '期末残高'] += profit_loss

    # 資産
    df_bs_asset = pd.DataFrame(columns=['科目名', '期末残高'])
    df_bs_asset = df_bs_asset.astype({'科目名': str})
    df_bs_asset = df_bs_asset.astype({'期末残高': int})

    # 負債
    df_bs_liability = pd.DataFrame(columns=['科目名', '期末残高'])
    df_bs_liability = df_bs_liability.astype({'科目名': str})
    df_bs_liability = df_bs_liability.astype({'期末残高': int})

    # 純資産
    df_bs_netasset = pd.DataFrame(columns=['科目名', '期末残高'])
    df_bs_netasset = df_bs_netasset.astype({'科目名': str})
    df_bs_netasset = df_bs_netasset.astype({'期末残高': int})

    total_asset = 0
    total_liability = 0
    total_netasset = 0

    for index, row in df_tb.iterrows():
        if str(row["科目コード"])[0:3] in ['A11', 'A12', 'A13','A14', 'A15']:
            df_bs_asset.at[index, "科目名"] = row["科目名"]
            df_bs_asset.at[index, "期末残高"] = row["期末残高"]
            total_asset += row['期末残高']

        if str(row["科目コード"])[0:3] in ['A16', 'A17']:
            df_bs_liability.at[index, "科目名"] = row["科目名"]
            df_bs_liability.at[index, "期末残高"] = row["期末残高"] * -1
            total_liability += row['期末残高'] * -1

        if str(row["科目コード"])[0:3] in ['A18', 'A19']:
            df_bs_netasset.at[index, "科目名"] = row["科目名"]
            df_bs_netasset.at[index, "期末残高"] = row["期末残高"] * -1
            total_netasset += row['期末残高'] * -1

    asset_index = max(list(df_bs_asset.index)) + 1
    liability_index = max(list(df_bs_liability.index)) + 1
    netasset_index = max(list(df_bs_netasset.index)) + 1

    df_bs_asset.loc[asset_index] = ["資産合計", total_asset]
    df_bs_liability.loc[liability_index] = ["負債合計", total_liability]
    df_bs_netasset.loc[netasset_index] = ["純資産合計", total_netasset]
    df_bs_netasset.loc[netasset_index + 1] = ["負債・純資産合計", total_liability + total_netasset]

    asset = df_bs_asset[df_bs_asset["期末残高"] != 0]
    liability = df_bs_liability[df_bs_liability["期末残高"] != 0]
    netasset = df_bs_netasset[df_bs_netasset["期末残高"] != 0]

    asset['期末残高'] = asset['期末残高'].astype('int')
    liability['期末残高'] = liability['期末残高'].astype('int')
    netasset['期末残高'] = netasset['期末残高'].astype('int')

    return asset, liability, netasset

def make_profit_loss_statement():
    # 試算表の作成
    df_tb = make_trial_balance()
    
    # 勘定科目一覧の取得
    acc = AccountingCode.objects.all()
    df_acc_table = read_frame(acc)

    # まとめ用のDataFrameを作成する。
    df_fs_all = pd.DataFrame(columns=['区分CD', '区分名', '決算書表示区分CD','決算書表示区分名', '期末残高'])
    df_fs_all = df_fs_all.astype({'区分CD': str})
    df_fs_all = df_fs_all.astype({'区分名': str})
    df_fs_all = df_fs_all.astype({'決算書表示区分CD': str})
    df_fs_all = df_fs_all.astype({'決算書表示区分名': str})
    df_fs_all = df_fs_all.astype({'期末残高': int})

    # 科目名、科目コードをfsに移す。
    df_fs_all['区分CD'] = df_acc_table['classification_code']
    df_fs_all['区分名'] = df_acc_table['classification_name']
    df_fs_all['決算書表示区分CD'] = df_acc_table['fs_display_classification_code']
    df_fs_all['決算書表示区分名'] = df_acc_table['fs_display_classification_name']
    df_fs_all['期末残高'] = 0

    # 試算表の「決算書表示区分CD」をもとに、値を集計する。
    df_tb_dropped = df_tb.drop(["科目コード","科目名","区分CD","区分名", "決算書表示区分名", "期首残高", "借方", "貸方"], axis=1)
    df_fs_sum = df_tb_dropped.groupby('決算書表示区分CD').sum()

    # 集計したデータを df_fs に反映させる
    for index, row in df_fs_all.iterrows():
        for i, r in df_fs_sum.iterrows():
            if str(row['決算書表示区分CD']) == i:
                df_fs_all.at[index, '期末残高'] = r['期末残高']

    # 区分CDで集約
    _aggregated_by_category = df_fs_all.drop(['区分名','決算書表示区分CD', '決算書表示区分名'], axis=1)
    aggregated_by_category = _aggregated_by_category.groupby('区分CD').sum().reset_index()

    # 売上総利益の算定
    df_total_sale = aggregated_by_category[aggregated_by_category['区分CD'] == 'B2100']
    total_sale = int(df_total_sale["期末残高"].values) * -1
    
    df_total_cogs = aggregated_by_category[aggregated_by_category['区分CD'] == 'B2200']
    total_cogs = int(df_total_cogs["期末残高"].values)

    gross_profit = total_sale - total_cogs

    # 販売費及び一般管理費合計額の算定
    df_total_sga = aggregated_by_category[aggregated_by_category['区分CD'] == 'B2300']
    total_sga = int(df_total_sga["期末残高"].values)
    

    # 営業利益の算定
    operating_income = gross_profit - total_sga
    
    # 営業外収益合計額の算定
    df_total_non_operating_profit = aggregated_by_category[aggregated_by_category['区分CD'] == 'B2400']
    total_non_operating_profit = int(df_total_non_operating_profit["期末残高"].values) * -1

    
    # 営業外費用合計額の算定
    df_total_non_operating_expenses = aggregated_by_category[aggregated_by_category['区分CD'] == 'B2500']
    total_non_operating_expenses = int(df_total_non_operating_expenses["期末残高"].values)
    
    # 経常利益の算定
    ordinaly_profit = operating_income + total_non_operating_profit - total_non_operating_expenses
    
    # 特別利益合計額の算定
    df_total_extraordinary_profit = aggregated_by_category[aggregated_by_category['区分CD'] == 'B2600']
    total_extraordinary_profit = int(df_total_extraordinary_profit["期末残高"].values) * -1
    
    # 特別損失合計額の算定
    df_total_extraordinary_loss = aggregated_by_category[aggregated_by_category['区分CD'] == 'B2700']
    total_extraordinary_loss = int(df_total_extraordinary_loss["期末残高"].values)
    
    # 税引前利益の算定
    profit_before_tax = ordinaly_profit + total_extraordinary_profit - total_extraordinary_loss

    # 税金費用合計額の算定
    df_total_tax = aggregated_by_category[aggregated_by_category['区分CD'] == 'B2800']
    total_tax = int(df_total_tax["期末残高"].values)

    # 当期純利益の算定
    profit_after_tax = profit_before_tax - total_tax

    # 表示させるように整形する。
    df_pl = pd.DataFrame(columns=['項目', '金額'])
    koumoku = ['売上高', '売上原価', '売上総利益', '販売費及び一般管理費', ' 営業利益', '営業外収益', '営業外費用', '経常利益', '特別利益', '特別損失', '税引前利益', '税金費用（仮）', '税引後利益']
    kingaku = [total_sale, total_cogs, gross_profit, total_sga, operating_income, total_non_operating_profit, total_non_operating_expenses, ordinaly_profit, total_extraordinary_profit, total_extraordinary_loss, profit_before_tax, total_tax, profit_after_tax]
    df_pl['項目'] = koumoku
    df_pl['金額'] = kingaku

    return df_pl

# 試算表を表示させるページ
# https://note.com/nssystems/n/nbc0f9d215fa0
def trial_balance(request):

    df_tb = make_trial_balance()

    # htmlに渡す用。
    form = df_tb

    return render(request, "free_app/trial_balance.html", {'form':form})

# 貸借対照表を表示させるページ
def balancesheet(request):
    asset, liability, netasset = make_balance_sheet()
    return render(request, "free_app/balance_sheet.html", {'asset': asset, 'liability': liability, 'netasset':netasset})

# 損益計算書を表示させるページ
def profit_loss_statement(request):
    df_pl = make_profit_loss_statement()
    return render(request, "free_app/profit_loss.html", {'form':df_pl})
