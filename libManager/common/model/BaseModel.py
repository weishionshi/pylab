from django.db import models
import datetime

# the base model,all models extend this class

# class BaseModel(models.Model):
#     create_time_tc = models.DateTimeField(default=timezone.now, verbose_name='记录创建时间')
#     modify_time_tc = models.DateTimeField(auto_now=True, verbose_name='最后一次修改时间')
#     remark_tc = models.CharField(max_length=512, null=True, verbose_name="描述")
