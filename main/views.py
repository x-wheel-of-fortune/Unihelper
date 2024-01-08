from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from .forms import *
from django.contrib.auth.decorators import login_required
from .models import Subjects, Assignments, Events, OnlineCourses
from django.utils import timezone
from operator import itemgetter
from django.apps import apps
from datetime import datetime, timedelta
from django.db.models import F, Count
import json
from django.db.models.functions import TruncMonth, TruncDay

from django.http import FileResponse
import io
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter


from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Register the font (only need to do this once in your script)
pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))

def generate_report(request):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter, bottomup=0)
    text_object = c.beginText()
    text_object.setTextOrigin(inch, inch)
    text_object.setFont("DejaVuSans", 14)  # Use the registered font

    lines = [
        f"Количетсво сданных заданий: {Assignments.objects.filter(subject__user=request.user, status__name='Сдано').count()}/{Assignments.objects.filter(subject__user=request.user).count()}",
    ]

    for line in lines:
        text_object.textLine(line)

    c.drawText(text_object)
    c.showPage()
    c.save()
    buf.seek(0)

    return FileResponse(buf, as_attachment=True, filename='report.pdf')

def calculate_score(subject):
    assignments = Assignments.objects.filter(subject=subject)
    total_score = 0
    for assignment in assignments:
        if assignment.status.name == 'Сдано' and assignment.score:
            total_score += assignment.score if assignment.score else 0
    return total_score


def get_last_30_days_data():
    # Calculate the start date (30 days ago from now)
    start_date = datetime.now() - timedelta(days=30)

    # Get the count of fulfilled assignments for each day in the last 30 days
    data = (Assignments.objects
            .filter(finish_date__gte=start_date)
            .annotate(day=TruncDay('finish_date'))
            .values('day')
            .annotate(count=Count('id'))
            .values('day', 'count')
            )

    # Create a dictionary to store counts for each day
    count_dict = {item['day'].strftime('%d.%m'): item['count'] for item in data}
    print(f"count_dict: {count_dict}")
    # Create a list of the last 30 days with counts (filling missing days with count 0)
    last_30_days = [(start_date + timedelta(days=i)).strftime('%d.%m') for i in range(31)]
    counts = [count_dict.get(day, 0) for day in last_30_days]

    return last_30_days, counts

# Create your views here.
@login_required(login_url='login')
def home(request):
    context = {'user': request.user}
    subjs = []
    float_scores = []
    subjects_with_assignments = []
    subjects = Subjects.objects.filter(user=request.user)
    for subject in subjects:
        next_assignment = Assignments.objects.filter(subject=subject, status=1).order_by(  # 1 is "Not Done"
            'due_date').first()
        if next_assignment:
            subject_with_assignment = {
                'id': subject.id,
                'assignment_id': next_assignment.id,
                'obj_type': 'Subjects',
                'subject_name': subject.subject_name,
                'assignment_name': f"{next_assignment.assignment_type} {next_assignment.local_id if next_assignment.local_id else ''}",
                'deadline': (
                        next_assignment.due_date.date() - timezone.now().date()).days if next_assignment.due_date else None,
                'teacher_name': subject.teacher_name,
                'assignments': f"{Assignments.objects.filter(subject=subject, status=2).count()}/{Assignments.objects.filter(subject=subject).count()}",
                'score': f"{calculate_score(subject)}/{subject.min_score_for_5}" if subject.min_score_for_5 else None,
                'float_score': calculate_score(subject) / subject.min_score_for_5 if subject.min_score_for_5 else 1,

                'subject_link': f"/subject/{subject.id}",
                'assignment_link': f"/subject/{subject.id}/assignment/{next_assignment.id}",

            }
            subjects_with_assignments.append(subject_with_assignment)
        if subject.min_score_for_5:
            subjs.append(subject.subject_name)
            float_scores.append(calculate_score(subject) / subject.min_score_for_5)
    context['subjs'] = subjs
    context['float_scores'] = float_scores
    events = []
    evs = Events.objects.filter(user=request.user)
    for event in evs:
        d = {
            'id': event.id,
            'obj_type': 'Events',
            'name': event.name,
            'type': event.event_type.name,
            'start': (event.start.date() - timezone.now().date()).days if event.start else None,
            'end': (event.end.date() - timezone.now().date()).days if event.end else None,
            'description': event.description,
            'link': event.link,
            'prize': event.prize,
        }
        events.append(d)
    obj_list = subjects_with_assignments + events

    def get_sort_key(item):
        # Replace None with a value that ensures correct sorting
        if 'deadline' in item:
            time = item['deadline']
        else:
            time = item['start']
        if time is None:
            time = float('inf')
        return time

    sorted_obj_list = sorted(obj_list, key=lambda x: get_sort_key(x))
    context['objects'] = sorted_obj_list

    # Get the date 30 days ago
    start_date = datetime.now() - timedelta(days=30)

    # Get the count of fulfilled assignments for each day
    data = Assignments.objects.filter(finish_date__gte=start_date).annotate(date=F('finish_date')).values(
        'date').annotate(count=Count('id')).order_by('date')

    # Separate the dates and counts into two lists
    dates, counts = get_last_30_days_data()
    print(dates, counts)
    context['dates'] = dates
    context['counts'] = counts

    return render(request, 'main/home.html', context)


def university(request):
    subjects_with_assignments = []
    subjects = Subjects.objects.filter(user=request.user)

    for subject in subjects:
        next_assignment = Assignments.objects.filter(subject=subject, status=1).order_by(  # 1 is "Not Done"
            'due_date').first()

        if next_assignment:
            subject_with_assignment = {
                'subj_id': subject.id,
                'assignment_id': next_assignment.id,
                'assignment_status' : next_assignment.status,
                'subject_name': subject.subject_name,
                'assignment_name': f"{next_assignment.assignment_type} {next_assignment.local_id if next_assignment.local_id else ''}",
                'deadline': (
                        next_assignment.due_date.date() - timezone.now().date()).days if next_assignment.due_date else None,
                'teacher_name': subject.teacher_name,
                'assignments': f"{Assignments.objects.filter(subject=subject, status=2).count()}/{Assignments.objects.filter(subject=subject).count()}",
                'score': f"{calculate_score(subject)}/{subject.min_score_for_5}" if subject.min_score_for_5 else None,
                'float_score': calculate_score(subject) / subject.min_score_for_5 if subject.min_score_for_5 else 1,
                'subject_link': f"/subject/{subject.id}",
                'assignment_link': f"/subject/{subject.id}/assignment/{next_assignment.id}",
            }
        else:
            subject_with_assignment = {
                'subj_id': subject.id,
                'subject_name': subject.subject_name,
                'assignment_name': None,
                'deadline': None,
                'teacher_name': subject.teacher_name,
                'assignments': f"{Assignments.objects.filter(subject=subject, status=2).count()}/{Assignments.objects.filter(subject=subject).count()}",
                'score': f"{calculate_score(subject)}/{subject.min_score_for_5}" if subject.min_score_for_5 else None,
                'float_score': calculate_score(subject) / subject.min_score_for_5 if subject.min_score_for_5 else 1,
                'subject_link': f"/subject/{subject.id}",
            }
        subjects_with_assignments.append(subject_with_assignment)

    context = {'user': request.user, 'subjects_with_assignments': subjects_with_assignments}
    return render(request, 'main/university.html', context)


def events(request):
    events = []
    evs = Events.objects.filter(user=request.user)

    for event in evs:
        d = {
            'ev_id': event.id,
            'name': event.name,
            'type': event.event_type.name,
            'start': (event.start.date() - timezone.now().date()).days if event.start else None,
            'end': (event.end.date() - timezone.now().date()).days if event.end else None,
            'description': event.description,
            'link': event.link,
            'prize': event.prize,
        }
        events.append(d)
    context = {'user': request.user, 'events': events}
    return render(request, 'main/events.html', context)


def courses(request):
    return render(request, 'main/courses.html',
                  {'user': request.user, 'courses': OnlineCourses.objects.filter(user=request.user)})


# signup page
def user_signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = SignupForm()
    return render(request, 'main/signup.html', {'form': form})


# login page
def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return redirect('/')
    else:
        form = LoginForm()
    return render(request, 'main/login.html', {'form': form})


# logout page
def user_logout(request):
    logout(request)
    return redirect('login')


def add_subject(request):
    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            subject = form.save(commit=False)
            subject.user = request.user  # Assuming you have user authentication
            subject.save()
            return redirect('university')  # Redirect to a page showing all subjects
    else:
        form = SubjectForm()

    return render(request, 'main/add_subject.html', {'form': form})


def add_assignment(request):
    if request.method == 'POST':
        form = AssignmentForm(request.POST, user=request.user)
        if form.is_valid():
            # Save the form
            form.save()
            # Redirect to a success page
            return redirect('home')
    else:
        form = AssignmentForm(user=request.user)

    return render(request, 'main/add_assignment.html', {'form': form})


def display_subject(request, subject_id):
    subject = Subjects.objects.get(id=subject_id)
    if request.method == 'POST':
        form = SubjectForm(request.POST, instance=subject)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = SubjectForm(instance=subject)

    assignments = Assignments.objects.filter(subject=subject)
    links = [f"/subject/{subject.id}/assignment/{assignment.id}" for assignment in assignments]
    course = (subject.semester - 1) // 2 + 1
    semester = (subject.semester - 1) % 2 + 1
    context = {
        'subject': subject,
        'assignments': zip(assignments, links),
        'form': form, 'course': course,
        'semester': semester,
        'assignments_score': f"{Assignments.objects.filter(subject=subject, status=2).count()}/{Assignments.objects.filter(subject=subject).count()}",
        'score': f"{calculate_score(subject)}/{subject.min_score_for_5}" if subject.min_score_for_5 else None,
    }
    return render(request, 'main/display_subject.html', context)


def display_assignment(request, subject_id, assignment_id):
    subject = Subjects.objects.get(id=subject_id)
    assignment = Assignments.objects.get(id=assignment_id)
    if request.method == 'POST':
        form = AssignmentForm(request.POST, instance=assignment)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = AssignmentForm(instance=assignment)

    context = {
        'subject': subject,
        'assignment': assignment,
        'form': form,
        'name': subject.subject_name + " " + assignment.assignment_type.name + " " + (
            str(assignment.local_id) if assignment.local_id else ""),

    }
    return render(request, 'main/display_assignment.html', context)


def add_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.user = request.user  # Assuming you have user authentication
            event.save()
            return redirect('events')  # Redirect to a page showing all events
    else:
        form = EventForm()

    return render(request, 'main/add_event.html', {'form': form})


def add_course(request):
    if request.method == 'POST':
        form = OnlineCourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.user = request.user  # Assuming you have user authentication
            course.save()
            return redirect('courses')  # Redirect to a page showing all courses
    else:
        form = OnlineCourseForm()

    return render(request, 'main/add_course.html', {'form': form})


def delete_object(request, model_name, obj_id):
    # Assuming your models are in an app named 'yourapp'
    app_label = 'main'

    # Construct the model class from the app label and model name
    model_class = apps.get_model(app_label, model_name)

    obj = get_object_or_404(model_class, id=obj_id)
    obj.delete()

    # Redirect to the URL specified in the 'next' query parameter
    return redirect(request.GET.get('next'))


def fulfill_task(request, model_name, obj_id):
    app_label = 'main'

    # Construct the model class from the app label and model name
    model_class = apps.get_model(app_label, model_name)

    obj = get_object_or_404(model_class, id=obj_id)
    obj.status = get_object_or_404(TaskStatuses, id=2)
    obj.finish_date = timezone.now()
    obj.save()

    # Redirect to the URL specified in the 'next' query parameter
    return redirect(request.GET.get('next'))

