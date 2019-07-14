from django.shortcuts import render
from django.http import HttpResponse
import traceback
import json

# Create your views here.
def add_book(request):
    return render(request, "addBook.html")


# save book
def save(request):
    if request.method == 'POST':
        try:
            name = request.form.get("bookName")
            # author = request.POST.get("")
            # subtitle = request.POST.get("")
            # press = request.POST.get("")
            # publish_date = request.POST.get("")
            # buy_place = request.POST.get("")
            # buy_date = request.POST.get("")
            # isbn = request.POST.get("")
            # material = request.POST.get("")
            print("book name:" + name)

        except Exception as err:
            print(traceback.format_exc())
            return HttpResponse(traceback.format_exc())

        else:
            result = {"status": "SUCCESS", "data": ""}
            return HttpResponse(json.dumps(result, ensure_ascii=False),
                                content_type="application/json,charset=utf-8")
