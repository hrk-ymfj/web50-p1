from django.shortcuts import render

from . import util

from markdown2 import Markdown

markdowner = Markdown()

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
    
