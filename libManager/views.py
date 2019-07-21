from django.shortcuts import render
from django.http import HttpResponse
import traceback
import json
import logging, logging.config
from iso.models import ChineseLibClassification
# import libManager.common.util.LoggerManager

from libManager.models import Book, PublishHouse

# logger = libManager.common.util.LoggerManager.get_logger()
logging.config.fileConfig('./config/logging.conf')
logger = logging.getLogger('simpleLogger')
logger.setLevel(logging.DEBUG)


# Create your views here.
def add_book(request):
    return render(request, "addBook.html")


# init the add book page
def init(request):
    clsf = []
    if request.method == 'GET':
        try:
            classifications = ChineseLibClassification.objects.using("iso").filter(status=1)
            for cls in classifications:
                cls_dict = {}
                cls_dict["code"] = cls.code
                cls_dict["name"] = cls.name
                cls_dict["superiorCode"] = cls.superior_code
                clsf.append(cls_dict)
                logger.debug("row dict:" + str(cls_dict))

        except Exception as err:
            logger.error(traceback.format_exc())
            result = {"status": "FAIL", "data": traceback.format_exc()}
            return HttpResponse(json.dumps(result, ensure_ascii=False),
                                content_type="application/json,charset=utf-8")

        else:
            result = {"status": "SUCCESS", "data": clsf}
            logger.debug("return:" + str(result))
            return HttpResponse(json.dumps(result, ensure_ascii=False),
                                content_type="application/json,charset=utf-8")

# save book
def save(request):
    if request.method == 'POST':
        try:
            name = request.POST.get("bookName")
            subtitle = request.POST.get("subtitle")
            logger.debug("book name:" + name)
            author = request.POST.get("author")
            translator = request.POST.get("translator")
            press = request.POST.get("press")
            publish_date = request.POST.get("publishDate")
            buy_place = request.POST.get("buyPlace")
            buy_date = request.POST.get("buyDate")
            isbn = request.POST.get("isbn")
            material = request.POST.get("material")
            logger.debug("material:" + material)

            book = Book(bk_name=name, bk_subtitle=subtitle, bk_author2=author, bk_translator2=translator,
                        bk_press2=press, bk_pub_date=publish_date, bk_buy_place=buy_place, bk_buy_date=buy_date,
                        bk_ISBN=isbn, bk_material=material)
            book.save()

        except Exception as err:
            logger.error(traceback.format_exc())
            result = {"status": "FAIL", "data": traceback.format_exc()}
            return HttpResponse(json.dumps(result, ensure_ascii=False),
                                content_type="application/json,charset=utf-8")

        else:
            result = {"status": "SUCCESS", "data": ""}
            return HttpResponse(json.dumps(result, ensure_ascii=False),
                                content_type="application/json,charset=utf-8")
