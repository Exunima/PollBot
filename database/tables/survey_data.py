# database/tables/survey_data.py

from tortoise import fields, models
from enum import Enum
import uuid
from datetime import datetime, timedelta


# Типы опросов
class SurveyType(str, Enum):
    ANONYMOUS = "anonymous"
    REGISTERED = "registered"


class Survey(models.Model):
    """
    Таблица для хранения опросов (polls).
    """
    id = fields.IntField(pk=True)

    # Ссылка на пользователя (кто создал)
    creator = fields.ForeignKeyField(
        "models.User",
        related_name="surveys",
        null=True,
        on_delete=fields.SET_NULL
    )

    survey_title = fields.CharField(max_length=255, null=False)      # Название опроса
    survey_type = fields.CharEnumField(SurveyType, null=False)       # Тип: анонимный / зарегистрированный
    is_anonymous = fields.BooleanField(default=False)                # Флаг анонимности
    access_key = fields.UUIDField(default=uuid.uuid4, unique=True)   # Уникальный ключ для доступа
    attempts = fields.IntField(null=True, default=1)                 # Количество попыток прохождения

    # Сколько дней опрос доступен пользователям
    duration_days = fields.IntField(null=True, default=0)

    # Дата создания (пригодится для автозакрытия)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "surveys"

    def get_expiration_date(self) -> datetime:
        """
        Пример: базовый срок жизни 7 дней,
        если у пользователя есть 'duration_days', то +7.
        """
        base_lifetime = 7
        user_days = self.duration_days if self.duration_days else 0
        total_days = base_lifetime + user_days  # Можно скорректировать логику
        return self.created_at + timedelta(days=total_days)


# Типы вопросов
class QuestionType(str, Enum):
    POLL = "poll"
    # Если нужно, можно добавить другие варианты,
    # но важно, чтобы не путать с TEST (это другая таблица)


class SurveyQuestion(models.Model):
    """
    Таблица вопросов для опроса.
    """
    id = fields.IntField(pk=True)
    survey = fields.ForeignKeyField(
        "models.Survey",
        related_name="questions",
        on_delete=fields.CASCADE
    )
    question_text = fields.TextField(null=False)
    question_type = fields.CharEnumField(QuestionType, null=False)

    class Meta:
        table = "survey_questions"


class SurveyAnswerOption(models.Model):
    """
    Возможные варианты ответа для конкретного вопроса в опросе.
    """
    id = fields.IntField(pk=True)
    question = fields.ForeignKeyField(
        "models.SurveyQuestion",
        related_name="answer_options",
        on_delete=fields.CASCADE
    )
    option_text = fields.CharField(max_length=255, null=False)

    class Meta:
        table = "survey_answer_options"


class SurveyResponse(models.Model):
    """
    Ответы пользователей на опрос.
    """
    id = fields.IntField(pk=True)
    question = fields.ForeignKeyField(
        "models.SurveyQuestion",
        related_name="responses",
        on_delete=fields.CASCADE
    )

    # Можно хранить user_id (anon / registered), или ForeignKey на User
    user_id = fields.BigIntField(null=True)

    # Вариант ответа, который выбрал пользователь
    selected_option = fields.ForeignKeyField(
        "models.SurveyAnswerOption",
        related_name="responses",
        null=True,
        on_delete=fields.CASCADE
    )

    # Сколько раз этот вариант ответа выбирали
    response_count = fields.IntField(default=0)

    class Meta:
        table = "survey_responses"
