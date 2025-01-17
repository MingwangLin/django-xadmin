from django.db.models import Func


class Convert(Func):
    """
    用法示例: .order_by(Convert(*args).asc())
    """
    def __init__(self, expression, transcoding_name, **extra):
         super(Convert, self).__init__(
             expression, transcoding_name=transcoding_name, **extra)

    def as_mysql(self, compiler, connection):
        self.function = 'CONVERT'
        self.template = '%(function)s(%(expressions)s USING %(transcoding_name)s)'
        return super(Convert, self).as_sql(compiler, connection)