from django.shortcuts import render

from free_app.views.util import make_profit_loss_statement

# 損益計算書を表示させるページ
def profit_loss_statement(request):
    df_pl = make_profit_loss_statement()
    return render(request, "free_app/profit_loss.html", {'form':df_pl})
