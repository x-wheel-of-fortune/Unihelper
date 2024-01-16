from django.contrib import admin
from .models import Subjects, ClassSessions, ClassSessionTypes, Assignments, AssignmentTypes, TaskStatuses, Events, \
    EventTypes, Exams, OnlineCourses
@admin.register(Subjects)
class SubjectsAdmin(admin.ModelAdmin):
    ordering = ["subject_name"]
    search_fields = ["subject_name"]


@admin.register(ClassSessions)
class ClassSessionsAdmin(admin.ModelAdmin):
    ordering = ["class_session_datetime"]
    search_fields = ["subject__subject_name"]

@admin.register(ClassSessionTypes)
class ClassSessionTypesAdmin(admin.ModelAdmin):
    ordering = ["name"]
    search_fields = ["name"]


@admin.register(Assignments)
class AssignmentsAdmin(admin.ModelAdmin):
    ordering = ["subject__subject_name"]
    search_fields = ["subject__subject_name"]
    list_filter = ["status__name"]

@admin.register(AssignmentTypes)
class AssignmentTypesAdmin(admin.ModelAdmin):
    ordering = ["name"]
    search_fields = ["name"]

@admin.register(Events)
class EventsAdmin(admin.ModelAdmin):
    ordering = ["name"]
    search_fields = ["name"]
    list_filter = ["status__name"]

@admin.register(TaskStatuses)
class TaskStatusesAdmin(admin.ModelAdmin):
    ordering = ["name"]
    search_fields = ["name"]

@admin.register(EventTypes)
class EventTypesAdmin(admin.ModelAdmin):
    ordering = ["name"]
    search_fields = ["name"]

@admin.register(Exams)
class ExamsAdmin(admin.ModelAdmin):
    ordering = ["subject__subject_name"]
    search_fields = ["subject__subject_name"]

@admin.register(OnlineCourses)
class OnlineCoursesAdmin(admin.ModelAdmin):
    ordering = ["name"]
    search_fields = ["name"]
    list_filter = ["status__name"]


