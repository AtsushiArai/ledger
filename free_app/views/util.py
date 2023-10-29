from django_pandas.io import read_frame

import pandas as pd

from free_app.models import JournalEntry, AccountingCode

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
    df_tb['科目コード'] = df_acc_table['account_code_id']
    df_tb['科目名'] = df_acc_table['account_name']
    df_tb['区分CD'] = df_acc_table['classification_code_id']
    df_tb['区分名'] = df_acc_table['classification_name']
    df_tb['決算書表示区分CD'] = df_acc_table['fs_display_classification_code_id']
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
    df_fs_all['区分CD'] = df_acc_table['classification_code_id']
    df_fs_all['区分名'] = df_acc_table['classification_name']
    df_fs_all['決算書表示区分CD'] = df_acc_table['fs_display_classification_code_id']
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
