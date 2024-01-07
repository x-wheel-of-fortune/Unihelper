from django.contrib import admin
from .models import Subjects, ClassSessions, ClassSessionTypes, Assignments, AssignmentTypes, TaskStatuses, Events, EventTypes, Exams, OnlineCourses
# Register your models here.
admin.site.register(Subjects)
admin.site.register(ClassSessions)
admin.site.register(ClassSessionTypes)
admin.site.register(Assignments)
admin.site.register(AssignmentTypes)
admin.site.register(TaskStatuses)
admin.site.register(Events)
admin.site.register(EventTypes)
admin.site.register(Exams)
admin.site.register(OnlineCourses)


