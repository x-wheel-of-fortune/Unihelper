# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.contrib.auth.models import User

class TaskStatuses(models.Model):
    name = models.CharField(blank=False)

    class Meta:
        managed = False
        db_table = 'task_statuses'

    def __str__(self):
        return self.name


class AssignmentTypes(models.Model):
    name = models.CharField(blank=False)

    def __str__(self):
        return self.name

    class Meta:
        managed = False
        db_table = 'assignment_types'


class Assignments(models.Model):
    subject = models.ForeignKey('Subjects', models.CASCADE, blank=False)
    status = models.ForeignKey(TaskStatuses, models.CASCADE, blank=False)
    assignment_type = models.ForeignKey(AssignmentTypes, models.CASCADE, blank=False)
    content = models.BinaryField(blank=True, null=True)
    score = models.IntegerField(blank=True, null=True)
    mark = models.IntegerField(blank=True, null=True)
    due_date = models.DateTimeField(blank=True, null=True)
    finish_date = models.DateTimeField(blank=True, null=True)
    local_id = models.IntegerField(blank=False)
    class Meta:
        managed = False
        db_table = 'assignments'

    def __str__(self):
        return f"{self.subject.subject_name} {self.assignment_type.name} {str(self.local_id) if self.local_id else ''}"


class ClassSessionTypes(models.Model):
    name = models.CharField(blank=False)

    class Meta:
        managed = False
        db_table = 'class_session_types'


class ClassSessions(models.Model):
    subject = models.ForeignKey('Subjects', models.CASCADE, blank=False)
    class_session_type = models.ForeignKey(ClassSessionTypes, models.CASCADE, blank=False)
    class_session_datetime = models.DateTimeField(blank=False)
    score = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'class_sessions'


class EventTypes(models.Model):
    name = models.CharField(blank=False)

    def __str__(self):
        return self.name

    class Meta:
        managed = False
        db_table = 'event_types'


class Events(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    event_type = models.ForeignKey(EventTypes, models.CASCADE, blank=False)
    start = models.DateTimeField(blank=True, null=True)
    end = models.DateTimeField(blank=True, null=True)
    result = models.CharField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    link = models.CharField(blank=True, null=True)
    content = models.BinaryField(blank=True, null=True)
    prize = models.CharField(blank=True, null=True)
    name = models.CharField(blank=False)
    status = models.ForeignKey(TaskStatuses, models.CASCADE, blank=False)
    finish_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.name if self.name else self.event_type.name+' '+(str(self.start) if self.start else '')
    class Meta:
        managed = False
        db_table = 'events'


class Exams(models.Model):
    subject = models.ForeignKey('Subjects', models.CASCADE, blank=False)
    class_session = models.ForeignKey(ClassSessions, models.CASCADE, blank=True, null=True)
    mark = models.IntegerField(blank=True, null=True)
    status = models.CharField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'exams'


class OnlineCourses(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    name = models.CharField(blank=False)
    link = models.CharField(blank=False)
    description = models.TextField(blank=True, null=True)
    status = models.ForeignKey(TaskStatuses, models.CASCADE, blank=True, null=True)
    finish_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'online_courses'




class Subjects(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    subject_name = models.CharField(blank=False)
    teacher_name = models.CharField(blank=True, null=True)
    semester = models.IntegerField(blank=False)
    min_score_for_3 = models.IntegerField(blank=True, null=True)
    min_score_for_4 = models.IntegerField(blank=True, null=True)
    min_score_for_5 = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.subject_name#+"_user_"+str(self.user)

    class Meta:
        managed = False
        db_table = 'subjects'
