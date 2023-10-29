from django.shortcuts import render, redirect

from free_app.views.util import make_balance_sheet

# 貸借対照表を表示させるページ
def balance_sheet(request):
    asset, liability, netasset = make_balance_sheet()
    return render(request, "free_app/balance_sheet.html", {'asset': asset, 'liability': liability, 'netasset':netasset})
