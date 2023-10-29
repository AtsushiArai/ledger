from django.shortcuts import render

from free_app.views.util import make_trial_balance

# 試算表を表示させるページ
# https://note.com/nssystems/n/nbc0f9d215fa0
def trial_balance(request):

    df_tb = make_trial_balance()

    # htmlに渡す用。
    form = df_tb

    return render(request, "free_app/trial_balance.html", {'form':form})
