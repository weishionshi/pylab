from django.db import models


# Create your models here.
class Book(models.Model):
    bk_name = models.CharField(max_length=200)
    bk_author = models.CharField(max_length=200)
    bk_translator = models.ForeignKey(to='Writer', on_delete=models.CASCADE)
    bk_translator = models.ForeignKey(to='PublishHouse', on_delete=models.CASCADE)
    bk_page = models.IntegerField()
    bk_price = models.IntegerField()
    bk_pub_date = models.DateField('date published')
    bk_ISBN = models.CharField(max_length=16)


class Album(models.Model):
    ab_name = models.CharField(max_length=200)
    ab_singer = models.ForeignKey(to='Singer', on_delete=models.CASCADE)
    ab_release_date = models.DateField('date published')
    ab_genre = models.CharField(max_length=16, null=True)


class MotionPicture(models.Model):
    mp_name = models.CharField(max_length=200)
    director = models.CharField(max_length=200)
    writer = models.CharField(max_length=200)
    release_date = models.DateField('date published')
    runtime = models.IntegerField()


class Writer(models.Model):
    wt_name = models.CharField(max_length=128)
    wt_birthday = models.DateField()
    wt_deathday = models.DateField()
    wt_birthplace = models.CharField(max_length=128)
    wt_birthplace = models.CharField(max_length=128)
    wt_nationality = models.CharField(max_length=32)


class Singer(models.Model):
    sn_name = models.CharField(max_length=128)
    sn_birthday = models.DateField()
    sn_deathday = models.DateField()
    sn_birthplace = models.CharField(max_length=128)
    sn_birthday_birthplace = models.CharField(max_length=128)
    sn_nationality = models.CharField(max_length=32)


class PublishHouse(models.Model):
    ph_name = models.CharField(max_length=64)
    ph_founded_date = models.CharField(max_length=64)
    ph_founded_place = models.CharField(max_length=32)
    ph_founder = models.CharField(max_length=128)
    ph_headquarter = models.CharField(max_length=128)
