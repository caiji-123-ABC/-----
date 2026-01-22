from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_date
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .models import ShiftDefinition, GroupConfig, Person, Absence, PersonOverride, CalendarOverride, SpecialDateRule, WeekRotationConfig
from .serializers import ShiftDefinitionSerializer, GroupConfigSerializer, PersonSerializer, AbsenceSerializer, PersonOverrideSerializer, CalendarOverrideSerializer, SpecialDateRuleSerializer, WeekRotationConfigSerializer
from .schedule_generator import generate_schedule
import json
from datetime import datetime


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def week_schedule_config(request):
    """
    获取或更新大小周配置（现在存储在ShiftDefinition中）
    """
    if request.method == 'GET':
        # 获取所有班次及其大小周配置
        shifts = ShiftDefinition.objects.all()
        configs = []
        for shift in shifts:
            # 为每个班次创建配置对象
            config = {
                'id': shift.id,
                'shiftType': shift.id,
                'name': shift.name,
                'big_week': shift.big_week,
                'small_week': shift.small_week
            }
            configs.append(config)
        
        return Response(configs)
    
    elif request.method == 'POST':
        # 更新班次的大小周配置
        data = request.data
        
        for config_data in data:
            shift_type_id = config_data.get('shift_type') or config_data.get('shiftType')
            
            if shift_type_id:
                try:
                    # 获取对应的班次
                    shift_definition = ShiftDefinition.objects.get(id=shift_type_id)
                    
                    # 更新班次的大小周配置
                    shift_definition.big_week = config_data.get('big_week', config_data.get('bigWeek', []))
                    shift_definition.small_week = config_data.get('small_week', config_data.get('smallWeek', []))
                    shift_definition.save()
                    
                except ShiftDefinition.DoesNotExist:
                    return Response({'error': f'班次ID {shift_type_id} 不存在'}, status=400)
        
        return Response({'message': '大小周配置已更新'}, status=201)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def week_rotation_config(request):
    """
    获取或更新月份大小周配置
    """
    if request.method == 'GET':
        # 获取所有的月份大小周配置
        configs = WeekRotationConfig.objects.all()
        serializer = WeekRotationConfigSerializer(configs, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        # 更新或创建月份大小周配置
        data = request.data
        
        # 删除现有的配置
        WeekRotationConfig.objects.all().delete()
        
        # 创建新的配置
        for config_data in data:
            serializer = WeekRotationConfigSerializer(data=config_data)
            if serializer.is_valid():
                serializer.save()
            else:
                return Response(serializer.errors, status=400)
        
        return Response({'message': '月份大小周配置已更新'}, status=201)


@api_view(['GET', 'POST'])
def shift_definitions_list(request):
    """
    获取或创建班次定义
    """
    if request.method == 'GET':
        shift_definitions = ShiftDefinition.objects.all()
        serializer = ShiftDefinitionSerializer(shift_definitions, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = ShiftDefinitionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def shift_definition_detail(request, pk):
    """
    获取、更新或删除特定班次定义
    """
    try:
        shift_definition = ShiftDefinition.objects.get(pk=pk)
    except ShiftDefinition.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ShiftDefinitionSerializer(shift_definition)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = ShiftDefinitionSerializer(shift_definition, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        shift_definition.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
def group_configs_list(request):
    """
    获取或创建组配置
    """
    if request.method == 'GET':
        group_configs = GroupConfig.objects.all()
        serializer = GroupConfigSerializer(group_configs, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = GroupConfigSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def group_config_detail(request, pk):
    """
    获取、更新或删除特定组配置
    """
    try:
        group_config = GroupConfig.objects.get(pk=pk)
    except GroupConfig.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = GroupConfigSerializer(group_config)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = GroupConfigSerializer(group_config, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        group_config.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
def persons_list(request):
    """
    获取或创建人员信息
    """
    if request.method == 'GET':
        persons = Person.objects.select_related('shift_type').all()
        serializer = PersonSerializer(persons, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = PersonSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def person_detail(request, pk):
    """
    获取、更新或删除特定人员信息
    """
    try:
        person = Person.objects.select_related('shift_type').get(pk=pk)
    except Person.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = PersonSerializer(person)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = PersonSerializer(person, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        person.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
def absences_list(request):
    """
    获取或创建请假信息
    """
    if request.method == 'GET':
        absences = Absence.objects.all()
        serializer = AbsenceSerializer(absences, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = AbsenceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def absence_detail(request, pk):
    """
    获取、更新或删除特定请假信息
    """
    try:
        absence = Absence.objects.get(pk=pk)
    except Absence.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = AbsenceSerializer(absence)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = AbsenceSerializer(absence, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        absence.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
def person_overrides_list(request):
    """
    获取或创建人员锁定规则
    """
    if request.method == 'GET':
        person_overrides = PersonOverride.objects.all()
        serializer = PersonOverrideSerializer(person_overrides, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = PersonOverrideSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def person_override_detail(request, pk):
    """
    获取、更新或删除特定人员锁定规则
    """
    try:
        person_override = PersonOverride.objects.get(pk=pk)
    except PersonOverride.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = PersonOverrideSerializer(person_override)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = PersonOverrideSerializer(person_override, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        person_override.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
def calendar_overrides_list(request):
    """
    获取或创建日历覆盖规则
    """
    if request.method == 'GET':
        calendar_overrides = CalendarOverride.objects.all()
        serializer = CalendarOverrideSerializer(calendar_overrides, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = CalendarOverrideSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def calendar_override_detail(request, pk):
    """
    获取、更新或删除特定日历覆盖规则
    """
    try:
        calendar_override = CalendarOverride.objects.get(pk=pk)
    except CalendarOverride.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = CalendarOverrideSerializer(calendar_override)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = CalendarOverrideSerializer(calendar_override, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        calendar_override.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
def special_date_rules_list(request):
    """
    获取或创建特殊日期规则
    """
    if request.method == 'GET':
        special_date_rules = SpecialDateRule.objects.all()
        serializer = SpecialDateRuleSerializer(special_date_rules, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = SpecialDateRuleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def special_date_rule_detail(request, pk):
    """
    获取、更新或删除特定特殊日期规则
    """
    try:
        special_date_rule = SpecialDateRule.objects.get(pk=pk)
    except SpecialDateRule.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = SpecialDateRuleSerializer(special_date_rule)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = SpecialDateRuleSerializer(special_date_rule, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        special_date_rule.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
def week_rotation_configs_list(request):
    """
    获取或创建大小周配置
    """
    if request.method == 'GET':
        week_rotation_configs = WeekRotationConfig.objects.all()
        serializer = WeekRotationConfigSerializer(week_rotation_configs, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = WeekRotationConfigSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def week_rotation_config_detail(request, pk):
    """
    获取、更新或删除特定大小周配置
    """
    try:
        week_rotation_config = WeekRotationConfig.objects.get(pk=pk)
    except WeekRotationConfig.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = WeekRotationConfigSerializer(week_rotation_config)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = WeekRotationConfigSerializer(week_rotation_config, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        week_rotation_config.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



@api_view(['POST'])
@permission_classes([AllowAny])
def generate_schedule_view(request):
    """
    生成排班表
    
    请求参数:
    {
        "year_month": "YYYY-MM"
    }
    
    返回:
    {
        "schedule": [
            {
                "person_id": int,
                "person_name": str,
                "group": str,
                "date": "YYYY-MM-DD",
                "shift": str,
                "status": str,
                "is_violation": bool,
                "violation_reason": str
            },
            ...
        ],
        "violations": []
    }
    """
    try:
        year_month = request.data.get('year_month')
        if not year_month:
            return Response(
                {'error': '缺少year_month参数'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        result = generate_schedule(year_month)
        return Response(result, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )