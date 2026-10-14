from django.contrib import admin
from .models import (
    Answer,
    Course,
    Enrollment,
    Lesson,
    Profile,
    Question,
    Test,
    TestResult,
)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "telegram_id")
    list_filter = ("role",)
    search_fields = ("user__username", "user__email", "telegram_id")


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "teacher", "created_at")
    list_filter = ("created_at",)
    search_fields = ("title", "description", "teacher__username")


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "order", "created_at")
    list_filter = ("course",)
    search_fields = ("title", "content")
    ordering = ("course", "order")    


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ("title", "lesson")
    search_fields = ("title",)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("text", "test")
    search_fields = ("text",)


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ("text", "question", "is_correct")
    list_filter = ("is_correct",)
    search_fields = ("text",)

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("student", "course", "enrolled_at")
    list_filter = ("course", "enrolled_at")
    search_fields = ("student__username", "course__title")


@admin.register(TestResult)
class TestResultAdmin(admin.ModelAdmin):
    list_display = (
        "student",
        "test",
        "score",
        "total_questions",
        "completed_at",
    )

    list_filter = ("test", "completed_at")
    search_fields = ("student__username", "test__title")