from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect

from .forms import LoginForm, RegistrationForm
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


def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.save()

            Profile.objects.create(
                user=user,
                role="student"
            )

            login(request, user)

            return redirect("home")

    else:
        form = RegistrationForm()

    return render(request, "users/register.html", {"form": form})


def home(request):
    return render(request, "users/home.html")


def course_list(request):
    courses = Course.objects.all()

    enrolled_course_ids = []

    if request.user.is_authenticated:
        enrolled_course_ids = Enrollment.objects.filter(
            student=request.user
        ).values_list("course_id", flat=True)

    return render(
        request,
        "users/course_list.html",
        {
            "courses": courses,
            "enrolled_course_ids": enrolled_course_ids,
        }
    )


def enroll_course(request, course_id):
    if not request.user.is_authenticated:
        return redirect("register")

    course = Course.objects.get(id=course_id)

    Enrollment.objects.get_or_create(
        student=request.user,
        course=course
    )

    return redirect("course_list")



def student_login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            user = authenticate(
                request,
                username=username,
                password=password
            )

            if user is not None:
                login(request, user)
                return redirect("course_list")

            form.add_error(
                None,
                "Неверное имя пользователя или пароль."
            )
    else:
        form = LoginForm()

    return render(
        request,
        "users/login.html",
        {"form": form}
    )

def lesson_list(request, course_id):
    course = Course.objects.get(id=course_id)

    lessons = Lesson.objects.filter(
        course=course
    ).order_by("order")

    return render(
        request,
        "users/lesson_list.html",
        {
            "course": course,
            "lessons": lessons,
        }
    )


def take_test(request, test_id):
    test = Test.objects.get(id=test_id)

    questions = Question.objects.filter(
        test=test
    ).prefetch_related("answers")

    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect("student_login")

        score = 0
        total_questions = questions.count()

        for question in questions:
            answer_id = request.POST.get(
                f"question_{question.id}"
            )

            if answer_id:
                is_correct = Answer.objects.filter(
                    id=answer_id,
                    question=question,
                    is_correct=True
                ).exists()

                if is_correct:
                    score += 1

        TestResult.objects.create(
            student=request.user,
            test=test,
            score=score,
            total_questions=total_questions
        )

        return render(
            request,
            "users/test_result.html",
            {
                "test": test,
                "score": score,
                "total_questions": total_questions,
            }
        )

    return render(
        request,
        "users/take_test.html",
        {
            "test": test,
            "questions": questions,
        }
    )

def my_results(request):
    if not request.user.is_authenticated:
        return redirect("student_login")

    results = TestResult.objects.filter(
        student=request.user
    ).select_related("test").order_by("-completed_at")

    return render(
        request,
        "users/my_results.html",
        {
            "results": results,
        }
    )


def student_logout(request):
    if request.method == "POST":
        logout(request)
        return redirect("student_login")

    return redirect("course_list")