from tortoise import fields, models


class User(models.Model):
    """
    Таблица пользователей в боте.
    Содержит основные данные, которые общие для тестов и опросов.
    """
    id = fields.IntField(pk=True)
    telegram_id = fields.BigIntField(unique=True)
    full_name = fields.CharField(max_length=200, null=True, default=None)

    class Meta:
        table = "users"
