from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from django import forms
from .forms import MemberForm, TestJournalEntryForm

from django.views.generic.list import ListView
from .models import Member, TestJournalEntry


FORM_NUM = 1      # フォーム数
FORM_VALUES = {}  # 前回のPSOT値

# https://en-junior.com/formset_add/

class IndexView(FormView):
    
    '''
        初期値設定をするとエラーが出るの、なぜ？
    '''

    # # 初期値のためのデータ抽出（仕訳番号最大値を取得し、１を足したものを初期値にする）
    # je_data = TestJournalEntry.objects.values_list('t_je_no', flat=True)
    # print(je_data)
    # try:
    #     pre_je_no = max(je_data)
    # except:
    #     pre_je_no = 0
    # je_no = pre_je_no + 1
    # print(je_no)

    # # 初期値
    # initial = {'t_je_no':je_no,}

    # テンプレート
    template_name = 'test_app/test.html'

    # POST成功時の遷移先
    success_url = reverse_lazy('index')
    TestJournalEntryFormSet = forms.formset_factory(
        form=TestJournalEntryForm,
        extra=1,
        max_num=10,
    )

    # フォームとして表示するFormSetを指定
    form_class = TestJournalEntryFormSet

    def get_form_kwargs(self):
        # デフォルトのget_form_kwargsメソッドを呼び出す
        kwargs = super().get_form_kwargs()
        # FORM_VALUESが空でない場合（入力中のフォームがある場合）、dataキーにFORM_VALUESを設定
        if FORM_VALUES and 'btn_add' in FORM_VALUES:
            kwargs['data'] = FORM_VALUES
        return kwargs
    
    def post(self, request, *args, **kwargs):
        global FORM_NUM
        global FORM_VALUES
        # 追加ボタンが押された時の挙動
        if 'btn_add' in request.POST:
            FORM_NUM += 1    # フォーム数をインクリメント
            FORM_VALUES = request.POST.copy()  # リクエストの内容をコピー
            FORM_VALUES['form-TOTAL_FORMS'] = FORM_NUM   # フォーム数を上書き
        elif 'btn_submit' in request.POST:
            self.success_url = reverse_lazy('list')
            FORM_VALUES = {}
        
        return super().post(request, args, kwargs)
    
    def form_valid(self, form):
        # 送信ボタンが押されたとき
        if 'btn_submit' in self.request.POST:
            # バリデーション済みのデータを取得
            data = form.cleaned_data

            # フォームが複数あるので、一つずつループする
            for test_je_parameter in data:
                # フォームが空の可能性があるので、空ではないデータ飲み登録
                if test_je_parameter:
                    # フォームのデータでMemberモデルのオブジェクトを作成
                    test_je = TestJournalEntry(**test_je_parameter)
                    # データを登録
                    test_je.save()
        return super().form_valid(form)
    

class TestJournalEntryListView(ListView):
    model = TestJournalEntry