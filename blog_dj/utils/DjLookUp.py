# -*- coding: utf-8 -*-
"""
@desc: django自定义查询器
"""
from django.db.models import Lookup


class StartWithSearch(Lookup):
    """ 以某字符开头
    使用示例：TableModel.objects.filter(code__startwith="TQ")  # 过滤code以"TQ"开头的queryset
    转换成的sql为：WHERE code like 'TQ%'
    """
    lookup_name = 'startwith'

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        rhs_params[0] += '%'
        params = lhs_params + rhs_params
        return '%s like %s' % (lhs, rhs), params


class NotEqualSearch(Lookup):
    """ 不等于
    使用示例：TableModel.objects.filter(id__neq=1)  # 过滤id不等于1的queryset
    转换成的sql为：WHERE id <> 1
    """
    lookup_name = 'neq'

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = lhs_params + rhs_params
        return '%s <> %s' % (lhs, rhs), params
