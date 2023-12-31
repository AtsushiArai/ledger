from django.shortcuts import render, redirect


from free_app.models import JournalEntry
from free_app.forms import JournalEntryForm, DescriptionForm

def journal_entry(request):

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
            posted_amount = request.POST.getlist('amount')

            for i in range(0, len(posted_row_no)):
                if posted_amount[i] == '0':
                    pass
                else:
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

        initial_values_1 = {'je_no':je_no, 'row_no':1, 'amount':0}
        initial_values_2 = {'je_no':je_no, 'row_no':2, 'amount':0}
        initial_values_3 = {'je_no':je_no, 'row_no':3, 'amount':0}
        initial_values_4 = {'je_no':je_no, 'row_no':4, 'amount':0}
        initial_values_5 = {'je_no':je_no, 'row_no':5, 'amount':0}
        initial_values_6 = {'je_no':je_no, 'row_no':6, 'amount':0}
        initial_values_7 = {'je_no':je_no, 'row_no':7, 'amount':0}
        initial_values_8 = {'je_no':je_no, 'row_no':8, 'amount':0}
        initial_values_9 = {'je_no':je_no, 'row_no':9, 'amount':0}
        initial_values_10 = {'je_no':je_no, 'row_no':10, 'amount':0}

        je_form_1 = JournalEntryForm(initial_values_1)
        je_form_2 = JournalEntryForm(initial_values_2)
        je_form_3 = JournalEntryForm(initial_values_3)
        je_form_4 = JournalEntryForm(initial_values_4)
        je_form_5 = JournalEntryForm(initial_values_5)
        je_form_6 = JournalEntryForm(initial_values_6)
        je_form_7 = JournalEntryForm(initial_values_7)
        je_form_8 = JournalEntryForm(initial_values_8)
        je_form_9 = JournalEntryForm(initial_values_9)
        je_form_10 = JournalEntryForm(initial_values_10)
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
        initial_values_1 = {'je_no':je_no, 'row_no':1, 'amount':0}
        initial_values_2 = {'je_no':je_no, 'row_no':2, 'amount':0}
        initial_values_3 = {'je_no':je_no, 'row_no':3, 'amount':0}
        initial_values_4 = {'je_no':je_no, 'row_no':4, 'amount':0}
        initial_values_5 = {'je_no':je_no, 'row_no':5, 'amount':0}
        initial_values_6 = {'je_no':je_no, 'row_no':6, 'amount':0}
        initial_values_7 = {'je_no':je_no, 'row_no':7, 'amount':0}
        initial_values_8 = {'je_no':je_no, 'row_no':8, 'amount':0}
        initial_values_9 = {'je_no':je_no, 'row_no':9, 'amount':0}
        initial_values_10 = {'je_no':je_no, 'row_no':10, 'amount':0}

        # 仕訳番号のデフォルト値を反映させてformを作成する。
        je_form_1 = JournalEntryForm(initial_values_1)
        je_form_2 = JournalEntryForm(initial_values_2)
        je_form_3 = JournalEntryForm(initial_values_3)
        je_form_4 = JournalEntryForm(initial_values_4)
        je_form_5 = JournalEntryForm(initial_values_5)
        je_form_6 = JournalEntryForm(initial_values_6)
        je_form_7 = JournalEntryForm(initial_values_7)
        je_form_8 = JournalEntryForm(initial_values_8)
        je_form_9 = JournalEntryForm(initial_values_9)
        je_form_10 = JournalEntryForm(initial_values_10)
        description_form = DescriptionForm()

    return render(request, "free_app/journal.html", {'je_form_1':je_form_1,
                                                     'je_form_2':je_form_2,
                                                     'je_form_3':je_form_3,
                                                     'je_form_4':je_form_4,
                                                     'je_form_5':je_form_5,
                                                     'je_form_6':je_form_6,
                                                     'je_form_7':je_form_7,
                                                     'je_form_8':je_form_8,
                                                     'je_form_9':je_form_9,
                                                     'je_form_10':je_form_10,
                                                      'description_form':description_form})

