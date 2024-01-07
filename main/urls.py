from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
urlpatterns = [
    path('', views.home, name='home'),
    path('university/', views.university, name='university'),
    path('events/', views.events, name='events'),
    path('courses/', views.courses, name='courses'),
    path('login/', views.user_login, name='login'),
    path('signup/', views.user_signup, name='signup'),
    path('logout/', views.user_logout, name='logout'),
    path('add_subject/', views.add_subject, name='add_subject'),
    path('add_assignment/', views.add_assignment, name='add_assignment'),
    path('add_event/', views.add_event, name='add_event'),
    path('add_course/', views.add_course, name='add_course'),
    path('subject/<int:subject_id>', views.display_subject, name='display_subject'),
    path('subject/<int:subject_id>/assignment/<int:assignment_id>', views.display_assignment, name='display_assignment'),
    path('delete/<str:model_name>/<int:obj_id>/', views.delete_object, name='delete_object'),
    path('fulfill/<str:model_name>/<int:obj_id>/', views.fulfill_task, name='fulfill_task'),
]