from tortoise import fields, models
import uuid
from datetime import datetime, timedelta


class Test(models.Model):
    """
    Таблица для хранения данных о тесте.
    """
    id = fields.IntField(pk=True)

    # Ссылка на пользователя (кто создал тест)
    creator = fields.ForeignKeyField(
        "models.User",
        related_name="tests",
        null=True,
        on_delete=fields.SET_NULL
    )

    title = fields.CharField(max_length=255, null=False)

    # Время (в минутах) которое даётся пользователю после старта
    duration_minutes = fields.IntField(null=True, default=0)

    attempts = fields.IntField(null=True, default=1)

    # Дата создания (чтобы потом удалять устаревшие)
    created_at = fields.DatetimeField(auto_now_add=True)

    access_key = fields.UUIDField(default=uuid.uuid4, unique=True)

    class Meta:
        table = "tests"

    def get_expiration_date(self) -> datetime:
        """
        Пример упрощённой схемы: храним тест ровно 7 дней в БД, затем удаляем.
        Или меняйте логику как нужно.
        """
        return self.created_at + timedelta(days=7)


class TestQuestion(models.Model):
    id = fields.IntField(pk=True)
    test = fields.ForeignKeyField(
        "models.Test",
        related_name="questions",
        on_delete=fields.CASCADE
    )
    question_text = fields.TextField(null=False)

    # Теперь связь многие-ко-многим (M2M)
    correct_answers = fields.ManyToManyField(
        "models.TestAnswerOption",
        related_name="correct_for_questions"
    )

    class Meta:
        table = "test_questions"


class TestAnswerOption(models.Model):
    id = fields.IntField(pk=True)
    question = fields.ForeignKeyField(
        "models.TestQuestion",
        related_name="answer_options",
        on_delete=fields.CASCADE
    )
    option_text = fields.CharField(max_length=255, null=False)

    class Meta:
        table = "test_answer_options"


class TestResponse(models.Model):
    """
    Ответы конкретного пользователя на конкретный тест.
    """
    id = fields.IntField(pk=True)
    question = fields.ForeignKeyField(
        "models.TestQuestion",
        related_name="responses",
        on_delete=fields.CASCADE
    )
    user_id = fields.BigIntField(null=True)
    selected_option = fields.ForeignKeyField(
        "models.TestAnswerOption",
        related_name="responses",
        null=True,
        on_delete=fields.CASCADE
    )

    # Флаг, правильно ли ответил
    is_correct = fields.BooleanField(default=False)

    class Meta:
        table = "test_responses"


class TestResult(models.Model):
    id = fields.IntField(pk=True)
    test = fields.ForeignKeyField(
        "models.Test",
        related_name="results",
        on_delete=fields.CASCADE
    )
    user_id = fields.BigIntField()
    best_score = fields.IntField(default=0)

    class Meta:
        table = "test_results"
