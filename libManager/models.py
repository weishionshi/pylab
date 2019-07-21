from django.db import models
import django.utils.timezone as timezone
import datetime


# Create your models here.
class Book(models.Model):
    bk_name = models.CharField(max_length=128, default='', verbose_name='书名')
    bk_subtitle = models.CharField(max_length=256, default='', verbose_name='副标题', null=True)
    # bk_author = models.ManyToManyField('Author', related_name='author', verbose_name='作者')
    # bk_translator = models.ManyToManyField('Author', related_name='translator', verbose_name='译者')
    bk_author2 = models.CharField(max_length=64, default='', verbose_name='作者')
    bk_translator2 = models.CharField(max_length=64, default='', verbose_name='译者', null=True)
    bk_press2 = models.CharField(max_length=64, default='', verbose_name='出版社', null=True)
    # bk_press = models.ForeignKey(to='PublishHouse', default="", on_delete=models.CASCADE)
    bk_page = models.IntegerField(default=0, verbose_name='页数', null=True)
    bk_price = models.IntegerField(default=0, verbose_name='价格', null=True)
    bk_pub_date = models.DateField('date published', null=True)
    bk_ISBN = models.CharField(max_length=16, default='', verbose_name='国际标准书号')
    bk_material = models.CharField(max_length=4, default='', verbose_name='纸质电子')
    bk_category = models.CharField(max_length=4, default='', verbose_name='图书类型', null=True)
    bk_buy_place = models.CharField(max_length=32, default='', verbose_name='购买地点', null=True)
    bk_buy_date = models.DateTimeField(verbose_name='购买日期', null=True)
    bk_series = models.CharField(max_length=32, default='', verbose_name='所属丛书', null=True)
    create_time_tc = models.DateTimeField(default=timezone.now, verbose_name='记录创建时间')
    modify_time_tc = models.DateTimeField(auto_now=True, verbose_name='最后一次修改时间')
    remark_tc = models.CharField(max_length=512, null=True, verbose_name="描述")


# 音乐专辑
# class Album(models.Model):
#     ab_name = models.CharField(max_length=200)
#     ab_singer = models.ForeignKey(to='Singer', on_delete=models.CASCADE)
#     ab_release_date = models.DateField('date published')
#     ab_genre = models.CharField(max_length=16, null=True)
#
# 电影电视剧
# class MotionPicture(models.Model):
#     mp_name = models.CharField(max_length=200, default='', verbose_name='片名')
#     director = models.CharField(max_length=200, default='', verbose_name='导演')
#     writer = models.CharField(max_length=200, default='', verbose_name='编剧')
#     release_date = models.DateField('date published')
#     runtime = models.IntegerField(default=0, verbose_name='时长')


class Author(models.Model):
    at_name = models.CharField(max_length=128)
    at_birthday = models.DateField()
    at_deathday = models.DateField()
    at_birthplace = models.CharField(max_length=128)
    at_birthplace = models.CharField(max_length=128)
    at_nationality = models.CharField(max_length=32)
    create_time_tc = models.DateTimeField(default=timezone.now, verbose_name='记录创建时间')
    modify_time_tc = models.DateTimeField(auto_now=True, verbose_name='最后一次修改时间')
    remark_tc = models.CharField(max_length=512, null=True, verbose_name="描述")


# class Singer(models.Model):
#     sn_name = models.CharField(max_length=128)
#     sn_birthday = models.DateField()
#     sn_deathday = models.DateField()
#     sn_birthplace = models.CharField(max_length=128)
#     sn_birthday_birthplace = models.CharField(max_length=128)
#     sn_nationality = models.CharField(max_length=32)


class PublishHouse(models.Model):
    ph_name = models.CharField(max_length=64, default='', verbose_name='出版社')
    ph_founded_date = models.CharField(max_length=64, null=True, verbose_name='成立时间')
    ph_founded_place = models.CharField(max_length=32, null=True, verbose_name='成立时间')
    ph_founder = models.CharField(max_length=128, null=True, verbose_name='创始人')
    ph_headquarter = models.CharField(max_length=128, null=True, verbose_name='总部所在地')
    create_time_tc = models.DateTimeField(default=timezone.now, verbose_name='记录创建时间')
    modify_time_tc = models.DateTimeField(auto_now=True, verbose_name='最后一次修改时间')
    remark_tc = models.CharField(max_length=512, null=True, verbose_name="描述")
