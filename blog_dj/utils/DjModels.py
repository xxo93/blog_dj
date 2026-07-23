# -*- coding: utf-8 -*-
from django.db import models


class BaseModel(models.Model):
    update_time = models.DateTimeField(auto_now=True, blank=True, null=True, help_text='记录更新时间')
    create_time = models.DateTimeField(auto_now_add=True, blank=True, null=True, help_text='记录创建时间')

    class Meta:
        abstract = True
