from django.urls import path
from . import views

urlpatterns = [
    # 班次定义相关路由
    path('shift-definitions/', views.shift_definitions_list, name='shift-definitions-list'),
    path('shift-definitions/<int:pk>/', views.shift_definition_detail, name='shift-definition-detail'),
    
    # 组配置相关路由
    path('group-configs/', views.group_configs_list, name='group-configs-list'),
    path('group-configs/<int:pk>/', views.group_config_detail, name='group-config-detail'),
    
    # 人员管理相关路由
    path('persons/', views.persons_list, name='persons-list'),
    path('persons/<int:pk>/', views.person_detail, name='person-detail'),
    
    # 请假管理相关路由
    path('absences/', views.absences_list, name='absences-list'),
    path('absences/<int:pk>/', views.absence_detail, name='absence-detail'),
    
    # 人员锁定相关路由
    path('person-overrides/', views.person_overrides_list, name='person-overrides-list'),
    path('person-overrides/<int:pk>/', views.person_override_detail, name='person-override-detail'),
    
    # 日历覆盖相关路由
    path('calendar-overrides/', views.calendar_overrides_list, name='calendar-overrides-list'),
    path('calendar-overrides/<int:pk>/', views.calendar_override_detail, name='calendar-override-detail'),
    
    # 特殊日期规则相关路由
    path('special-date-rules/', views.special_date_rules_list, name='special-date-rules-list'),
    path('special-date-rules/<int:pk>/', views.special_date_rule_detail, name='special-date-rule-detail'),
    
    # 大小周配置相关路由
    path('week-rotation-configs/', views.week_rotation_configs_list, name='week-rotation-configs-list'),
    path('week-rotation-configs/<int:pk>/', views.week_rotation_config_detail, name='week-rotation-config-detail'),
    
    # 新增：大小周工作日安排配置
    path('week-schedules/', views.week_schedule_config, name='week-schedule-config'),
    
    # 新增：月份大小周配置
    path('week-rotation-configs-full/', views.week_rotation_config, name='week-rotation-config-full'),
    
    # 排班生成相关路由
    path('generate-schedule/', views.generate_schedule_view, name='generate-schedule'),
]