from django.shortcuts import render, redirect

from . import util

from markdown2 import Markdown

from django import forms

import secrets

from django.http import HttpResponseRedirect

from django.urls import reverse


markdowner = Markdown()

class NewEntryForm(forms.Form):
    title = forms.CharField(label="タイトル")
    content = forms.CharField(widget=forms.Textarea(attrs={'rows': 10, 'cols': 40}), label="コンテンツ")

class EditForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea)

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request, title):
    # titleのリストをentriesに代入
    entries = util.list_entries()
    print("Entries:", entries)  # entriesリストをコンソールに出力
    # 引数のtitleがentriesに存在する場合の処理
    if title in entries:
        # titleのエントリーをpageに代入
        page = util.get_entry(title)
        # markdownerでpageを変換し、変数に格納する
        converted_page = markdowner.convert(page)

        # dataオブジェクトにtitleとpageを格納する
        context = {
            "title": title,
            "page": converted_page
        }

        # entry.htmlにcontextをrenderする
        return render(request, "encyclopedia/entry.html", context)

    else:
        # 「このページは作成されていません」のエラーメッセージを渡して、error.htmlをrenderする
        return render(request, "encyclopedia/error.html", {"message": "このページは作成されていません"})
    
def search(request):
    query = request.GET.get('q', '').lower()  # クエリ文字列を取得し、小文字に変換
    entries = util.list_entries()

    # 完全一致のページがある場合、該当ページに遷移
    for entry in entries:
        if query == entry.lower():
            return redirect('entry', title=entry)

    # 完全一致のページがない場合、候補一覧を表示
    matching_entries = [entry for entry in entries if query in entry.lower()]
    return render(request, "encyclopedia/index.html", {
        "entries": matching_entries
    })

def create(request):
    if request.method == "POST":
        form = NewEntryForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]

            # 指定したタイトルのエントリが既に存在するかをチェック
            if title in util.list_entries():
                return render(request, "encyclopedia/error.html", {"message": "このタイトルのエントリは既に存在します"})

            # エントリを保存
            util.save_entry(title, content)
            return redirect("entry", title=title)
    else:
        form = NewEntryForm()

    return render(request, "encyclopedia/newEntry.html", {"form": form})

def edit(request, title):
    # 既存のエントリーを取得し、フォームの初期データとして設定
    entry = util.get_entry(title)
    if entry is None:
        return render(request, "encyclopedia/error.html", {"message": "Page not found"})

    if request.method == "POST":
        form = EditForm(request.POST)
        if form.is_valid():
            content = form.cleaned_data["content"]
            util.save_entry(title, content)
            return redirect("entry", title=title)
    else:
        form = EditForm(initial={"content": entry})

    return render(request, "encyclopedia/newEntry.html", {
        "form": form,
        "editing": True,
        "entry_title": title,
        "entry_content": entry
    })

def random(request):
    entries = util.list_entries()
    if entries:
        randomEntry = secrets.choice(entries)
        redirect_url = reverse("entry", kwargs={'title': randomEntry})
        return HttpResponseRedirect(redirect_url)
    else:
        return render(request, "encyclopedia/error.html", {"message": "エントリーが存在しません"})
