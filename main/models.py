# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.contrib.auth.models import User

class AssignmentStatuses(models.Model):
    name = models.CharField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'assignment_statuses'


class AssignmentTypes(models.Model):
    name = models.CharField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'assignment_types'


class Assignments(models.Model):
    subject = models.ForeignKey('Subjects', models.DO_NOTHING, blank=True, null=True)
    assignment_status = models.ForeignKey(AssignmentStatuses, models.DO_NOTHING, blank=True, null=True)
    assignment_type = models.ForeignKey(AssignmentTypes, models.DO_NOTHING, blank=True, null=True)
    content = models.BinaryField(blank=True, null=True)
    score = models.IntegerField(blank=True, null=True)
    mark = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'assignments'


class ClassSessionTypes(models.Model):
    name = models.CharField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'class_session_types'


class ClassSessions(models.Model):
    subject = models.ForeignKey('Subjects', models.DO_NOTHING, blank=True, null=True)
    class_session_type = models.ForeignKey(ClassSessionTypes, models.DO_NOTHING, blank=True, null=True)
    class_session_datetime = models.DateTimeField(blank=True, null=True)
    score = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'class_sessions'


class EventTypes(models.Model):
    name = models.CharField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'event_types'


class Events(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    event_type = models.ForeignKey(EventTypes, models.DO_NOTHING, blank=True, null=True)
    start = models.DateTimeField(blank=True, null=True)
    end = models.DateTimeField(blank=True, null=True)
    result = models.CharField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    link = models.CharField(blank=True, null=True)
    content = models.BinaryField(blank=True, null=True)
    prize = models.CharField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'events'


class Exams(models.Model):
    subject = models.ForeignKey('Subjects', models.DO_NOTHING, blank=True, null=True)
    class_session = models.ForeignKey(ClassSessions, models.DO_NOTHING, blank=True, null=True)
    mark = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'exams'


class OnlineCourses(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    name = models.CharField(blank=True, null=True)
    link = models.CharField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'online_courses'


class RatingPlan(models.Model):
    subject = models.ForeignKey('Subjects', models.DO_NOTHING, blank=True, null=True)
    min_score_for_3 = models.IntegerField(blank=True, null=True)
    min_score_for_4 = models.IntegerField(blank=True, null=True)
    min_score_for_5 = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'rating_plan'


class Subjects(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    subject_name = models.CharField(blank=True, null=True)
    teacher_name = models.CharField(blank=True, null=True)
    semester = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.subject_name+"_user_"+str(self.user)

    class Meta:
        managed = False
        db_table = 'subjects'
