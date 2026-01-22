from django.urls import path
from . import views

urlpatterns = [
    path('shift-definitions/', views.shift_definitions_list, name='shift-definitions-list'),
    path('shift-definitions/<int:pk>/', views.shift_definition_detail, name='shift-definition-detail'),

    path('group-configs/', views.group_configs_list, name='group-configs-list'),
    path('group-configs/<int:pk>/', views.group_config_detail, name='group-config-detail'),

    path('persons/', views.persons_list, name='persons-list'),
    path('persons/<int:pk>/', views.person_detail, name='person-detail'),

    path('absences/', views.absences_list, name='absences-list'),
    path('absences/<int:pk>/', views.absence_detail, name='absence-detail'),

    path('calendar-overrides/', views.calendar_overrides_list, name='calendar-overrides-list'),
    path('calendar-overrides/<int:pk>/', views.calendar_override_detail, name='calendar-override-detail'),

    path('week-schedules/', views.week_schedule_config, name='week-schedule-config'),

    path('generate-schedule/', views.generate_schedule_view, name='generate-schedule'),
]
