from django.urls import path
from .views import (
    course_list,
    enroll_course,
    home,
    lesson_list,
    my_results,
    register,
    student_login,
    student_logout,
    take_test,
)


urlpatterns = [
    path("register/", register, name="register"),
    path("login/", student_login, name="student_login"),
    path("home/", home, name="home"),
    path("courses/", course_list, name="course_list"),
    path(
        "courses/<int:course_id>/enroll/",
        enroll_course,
        name="enroll_course"
    ),
    path(
    "courses/<int:course_id>/lessons/",
    lesson_list,
    name="lesson_list"
),
    path(
    "tests/<int:test_id>/",
    take_test,
    name="take_test"
),
    path("my-results/", my_results, name="my_results"),
    path("logout/", student_logout, name="student_logout"),
]
