# Standard Libraries
from datetime import datetime, timedelta
import io
from operator import itemgetter

# Third-party Libraries
from django.apps import apps
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count, F, Sum
from django.db.models.functions import TruncDay
from django.http import FileResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

# Local Imports
from .forms import SignupForm, LoginForm, SubjectForm, AssignmentForm, EventForm, OnlineCourseForm
from .models import *

# Register the font (only need to do this once in your script)
pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))


def generate_report(request):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter, bottomup=0)
    text_object = c.beginText(165, 60)
    # text_object.setTextOrigin(inch, inch)
    text_object.setFont("DejaVuSans", 14)  # Use the registered font

    lines = []
    # lines.append(
    #     f"Количество сданных заданий: {Assignments.objects.filter(subject__user=request.user, status__name='Сдано').count()}/{Assignments.objects.filter(subject__user=request.user).count()}")

    closed_subjects_count = sum(1 for subject in Subjects.objects.filter(user=request.user) if
                                calculate_score(subject) >= (subject.min_score_for_5 or 0))
    total_subjects_count = Subjects.objects.filter(user=request.user).count()
    lines.append(f"Количество закрытых предметов: {closed_subjects_count}/{total_subjects_count}")

    closest_assignments = Assignments.objects.filter(subject__user=request.user, status__name='Не сдано').order_by(
        'due_date')
    subjects = Subjects.objects.filter(user=request.user)

    subjects_with_assignments = get_subjects_with_or_without_assignments(request.user)
    data = ([
                ['Итого:',
                 f'{Assignments.objects.filter(subject__user=request.user, status__name="Сдано").count()}/{Assignments.objects.filter(subject__user=request.user).count()}',
                 ]
            ]
            + [
                [
                    s['subject_name'],
                    s['assignments'] or '-',
                    s['score'] or '-',
                    s['assignment_name'] or '-',
                    s['deadline'] or '-'
                ] for s in subjects_with_assignments]
            + [['Предмет', 'Работы', 'Баллы', 'Ближайшая работа', 'Дней до дедлайна']])
    table = Table(data)

    # Add a TableStyle if desired
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, -1), (-1, -1), '#d3d3d3'),
        # ('TEXTCOLOR', (0, 0), (-1, 0), '#ffffff'),

        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Add this line
        ('FONTNAME', (0, 0), (-1, -1), 'DejaVuSans'),
        # ('FONTSIZE', (0, 0), (-1, 0), 14),

        ('BOTTOMPADDING', (0, 0), (-1, -1), 24),
        # ('BACKGROUND', (0, 1), (-1, -1), '#ffffff'),
        ('GRID', (0, 0), (-1, -1), 1, '#000000'),
    ]))

    # Add the Table to the canvas
    table.wrapOn(c, 200, 200)
    table.drawOn(c, 35, 100)

    for line in lines:
        text_object.textLine(line)

    c.drawText(text_object)
    c.showPage()
    c.save()
    buf.seek(0)

    return FileResponse(buf, as_attachment=True, filename='report.pdf')


def calculate_score(subject):
    return \
            Assignments.objects.filter(subject=subject, status__name='Сдано', score__isnull=False).aggregate(
                Sum('score'))[
                'score__sum'] or 0


def get_last_30_days_data(user):
    start_date = datetime.now() - timedelta(days=30)

    data = (Assignments.objects
            .filter(finish_date__gte=start_date, subject__user=user)
            .annotate(day=TruncDay('finish_date'))
            .values('day')
            .annotate(count=Count('id'))
            .values('day', 'count')
            )

    count_dict = {item['day'].strftime('%d.%m'): item['count'] for item in data}
    last_30_days = [(start_date + timedelta(days=i)).strftime('%d.%m') for i in range(31)]
    counts = [count_dict.get(day, 0) for day in last_30_days]

    return last_30_days, counts


# Create your views here.
@login_required(login_url='login')
def home(request):
    context = {'user': request.user}
    context['subjs'], context['float_scores'], subjects_with_assignments = get_subjects_and_scores(request.user)
    events = get_events(request.user)
    obj_list = subjects_with_assignments + events
    context['objects'] = sort_objects(obj_list)
    context['dates'], context['counts'] = get_last_30_days_data(request.user)
    return render(request, 'main/home.html', context)


@login_required(login_url='login')
def statistics(request):
    context = {'user': request.user}
    context['subjs'], context['float_scores'], subjects_with_assignments = get_subjects_and_scores(request.user)
    context['dates'], context['counts'] = get_last_30_days_data(request.user)
    return render(request, 'main/statistics.html', context)


def get_subjects_and_scores(user):
    subjs = []
    float_scores = []
    subjects_with_assignments = []
    subjects = Subjects.objects.filter(user=user)
    for subject in subjects:
        next_assignment = Assignments.objects.filter(subject=subject, status=1).order_by('due_date').first()
        if next_assignment:
            subject_with_assignment = create_subject_with_assignment(subject, next_assignment)
            subjects_with_assignments.append(subject_with_assignment)
        if subject.min_score_for_5:
            subjs.append(subject.subject_name)
            float_scores.append(calculate_score(subject) / subject.min_score_for_5)
    return subjs, float_scores, subjects_with_assignments


def create_subject_with_assignment(subject, next_assignment):
    return {
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


def get_events(user):
    events = []
    evs = Events.objects.filter(user=user)
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
    return events


def sort_objects(obj_list):
    def get_sort_key(item):
        # Replace None with a value that ensures correct sorting
        if 'deadline' in item:
            time = item['deadline']
        else:
            time = item['start']
        if time is None:
            time = float('inf')
        return time

    return sorted(obj_list, key=lambda x: get_sort_key(x))


@login_required(login_url='login')
def university(request):
    subjects_with_or_without_assignments = get_subjects_with_or_without_assignments(request.user)
    context = {'user': request.user, 'subjects_with_assignments': subjects_with_or_without_assignments}
    return render(request, 'main/university.html', context)


def get_subjects_with_or_without_assignments(user):
    subjects_with_assignments = []
    subjects = Subjects.objects.filter(user=user)
    for subject in subjects:
        next_assignment = Assignments.objects.filter(subject=subject, status=1).order_by(  # 1 is "Not Done"
            'due_date').first()

        if next_assignment:
            subject_with_assignment = {
                'subj_id': subject.id,
                'assignment_id': next_assignment.id,
                'assignment_status': next_assignment.status,
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
    return subjects_with_assignments


@login_required(login_url='login')
def events(request):
    context = {'user': request.user, 'events': get_events(request.user)}
    return render(request, 'main/events.html', context)


@login_required(login_url='login')
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


@login_required(login_url='login')
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


@login_required(login_url='login')
def add_assignment(request):
    if request.method == 'POST':
        form = AssignmentForm(request.POST, user=request.user)
        if form.is_valid():
            # Get the model instance without saving it to the database
            assignment = form.save(commit=False)

            # Check the status and set the finish_date if necessary
            if assignment.status.name == 'Сдано':
                assignment.finish_date = timezone.now()

            # Save the model instance to the database
            assignment.save()

            # Redirect to a success page
            return redirect('home')
    else:
        form = AssignmentForm(user=request.user)

    return render(request, 'main/add_assignment.html', {'form': form})


@login_required(login_url='login')
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


@login_required(login_url='login')
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


@login_required(login_url='login')
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


@login_required(login_url='login')
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


def get_model_object(app_label, model_name, obj_id):
    model_class = apps.get_model(app_label, model_name)
    obj = get_object_or_404(model_class, id=obj_id)
    return obj


@login_required(login_url='login')
def delete_object(request, model_name, obj_id):
    app_label = 'main'
    obj = get_model_object(app_label, model_name, obj_id)
    obj.delete()
    return redirect(request.GET.get('next'))


@login_required(login_url='login')
def fulfill_task(request, model_name, obj_id):
    app_label = 'main'
    obj = get_model_object(app_label, model_name, obj_id)
    obj.status = get_object_or_404(TaskStatuses, id=2)
    obj.finish_date = timezone.now()
    obj.save()
    return redirect(request.GET.get('next'))
