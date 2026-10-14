from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    ROLE_CHOICES = (
        ("student", "Студент"),
        ("teacher", "Преподаватель"),
    )

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="student"
    )

    telegram_id = models.BigIntegerField(
        null=True,
        blank=True,
        unique=True
    )

    def __str__(self):
        return self.user.username



class Course(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name="Название курса"
    )

    description = models.TextField(
        verbose_name="Описание курса"
    )

    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="courses",
        verbose_name="Преподаватель"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )

    def __str__(self):
        return self.title



class Lesson(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="lessons",
        verbose_name="Курс"
    )

    title = models.CharField(
        max_length=200,
        verbose_name="Название урока"
    )

    content = models.TextField(
        verbose_name="Содержание урока"
    )

    order = models.PositiveIntegerField(
        default=1,
        verbose_name="Порядковый номер"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )

    def __str__(self):
        return self.title



class Test(models.Model):
    lesson = models.OneToOneField(
        Lesson,
        on_delete=models.CASCADE,
        related_name="test",
        verbose_name="Урок"
    )

    title = models.CharField(
        max_length=200,
        verbose_name="Название теста"
    )

    def __str__(self):
        return self.title


class Question(models.Model):
    test = models.ForeignKey(
        Test,
        on_delete=models.CASCADE,
        related_name="questions",
        verbose_name="Тест"
    )

    text = models.TextField(
        verbose_name="Текст вопроса"
    )

    def __str__(self):
        return self.text


class Answer(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="answers",
        verbose_name="Вопрос"
    )

    text = models.CharField(
        max_length=300,
        verbose_name="Текст ответа"
    )

    is_correct = models.BooleanField(
        default=False,
        verbose_name="Правильный ответ"
    )

    def __str__(self):
        return self.text


class Enrollment(models.Model):
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="enrollments",
        verbose_name="Студент"
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="enrollments",
        verbose_name="Курс"
    )

    enrolled_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата записи"
    )

    def __str__(self):
        return f"{self.student.username} — {self.course.title}"


class TestResult(models.Model):
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="test_results",
        verbose_name="Студент"
    )

    test = models.ForeignKey(
        Test,
        on_delete=models.CASCADE,
        related_name="results",
        verbose_name="Тест"
    )

    score = models.PositiveIntegerField(
        default=0,
        verbose_name="Количество правильных ответов"
    )

    total_questions = models.PositiveIntegerField(
        default=0,
        verbose_name="Всего вопросов"
    )

    completed_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата прохождения"
    )

    def __str__(self):
        return f"{self.student.username} — {self.test.title}: {self.score}/{self.total_questions}"