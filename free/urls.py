"""free URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
# from django.conf.urls import url

from free_app.views.balance_sheet import balance_sheet
from free_app.views.journal_entry import journal_entry
from free_app.views.trial_balanece import trial_balance
from free_app.views.profit_loss import profit_loss_statement
# from free_app.views import journalentry, trial_balance, balancesheet, profit_loss_statement
from test_app.views import IndexView, TestJournalEntryListView

urlpatterns = [
    path('', journal_entry, name='index'),
    path('trial_balance', trial_balance, name='trial_balance'),
    path('balance_sheet', balance_sheet, name='balance_sheet'),
    path('profit_loss', profit_loss_statement, name='profit_loss'),
    # path('',IndexView.as_view(), name='index' ),
    # path('list/', TestJournalEntryListView.as_view(), name='list'),
    path('admin/', admin.site.urls),
]
