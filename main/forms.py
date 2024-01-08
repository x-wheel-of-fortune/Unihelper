from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import *
from django.forms import DateInput


class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']


class LoginForm(forms.Form):
    username = forms.CharField(label='Имя пользователя')
    password = forms.CharField(widget=forms.PasswordInput, label='Пароль')


class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subjects
        fields = ['subject_name', 'teacher_name', 'semester', 'min_score_for_3', 'min_score_for_4', 'min_score_for_5']
        labels = {
            'subject_name': 'Название предмета',
            'teacher_name': 'Имя преподавателя',
            'semester': 'Семестр',
            'min_score_for_3': 'Минимальный балл для оценки 3',
            'min_score_for_4': 'Минимальный балл для оценки 4',
            'min_score_for_5': 'Минимальный балл для оценки 5',
        }


class AssignmentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(AssignmentForm, self).__init__(*args, **kwargs)

        # Filter the queryset of the subject field based on the user
        if user:
            self.fields['subject'].queryset = Subjects.objects.filter(user=user)

    class Meta:
        model = Assignments
        fields = ['subject', 'assignment_type', 'local_id', 'status', 'score', 'mark', 'due_date']
        widgets = {
            'due_date': DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'subject': 'Предмет',
            'assignment_type': 'Тип задания',
            'local_id': 'Номер задания',
            'status': 'Статус',
            'score': 'Баллы',
            'mark': 'Оценка',
            'due_date': 'Срок сдачи',
        }


class EventForm(forms.ModelForm):
    class Meta:
        model = Events
        fields = ['name', 'event_type', 'start', 'end', 'result', 'description', 'link', 'prize']
        widgets = {
            'start': DateInput(attrs={'type': 'date'}),
            'end': DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'name': 'Название',
            'event_type': 'Тип',
            'start': 'Дата начала',
            'end': 'Дата окончания',
            'result': 'Результат',
            'description': 'Описание',
            'link': 'Ссылка',
            'prize': 'Приз',
        }


class OnlineCourseForm(forms.ModelForm):
    class Meta:
        model = OnlineCourses
        fields = ['name', 'link', 'description']
        labels = {
            'name': 'Название',
            'description': 'Описание',
            'link': 'Ссылка',
        }
