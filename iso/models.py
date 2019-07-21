from django.db import models


# Create your models here.
class ChineseLibClassification(models.Model):
    code = models.CharField(max_length=8, default='', verbose_name='编码')
    name = models.CharField(max_length=64, default='', verbose_name='副标题')
    superior_code = models.CharField(max_length=8, default='', verbose_name='上级编码')
    status = models.CharField(max_length=1, default='1', verbose_name='状态')
