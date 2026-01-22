from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_date
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .models import ShiftDefinition, GroupConfig, Person, Absence, CalendarOverride
from .serializers import (
    ShiftDefinitionSerializer,
    GroupConfigSerializer,
    PersonSerializer,
    AbsenceSerializer,
    CalendarOverrideSerializer,
)
from .schedule_generator import generate_schedule
import json
from datetime import datetime


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def week_schedule_config(request):
    """
    获取或更新大小周配置（存储在 ShiftDefinition 中）
    """
    if request.method == 'GET':
        shifts = ShiftDefinition.objects.all()
        configs = []
        for shift in shifts:
            configs.append({
                'id': shift.id,
                'shiftType': shift.id,
                'name': shift.name,
                'big_week': shift.big_week,
                'small_week': shift.small_week
            })
        return Response(configs)

    if request.method == 'POST':
        data = request.data
        for config_data in data:
            shift_type_id = config_data.get('shift_type') or config_data.get('shiftType')
            if shift_type_id:
                try:
                    shift_definition = ShiftDefinition.objects.get(id=shift_type_id)
                    shift_definition.big_week = config_data.get('big_week', config_data.get('bigWeek', []))
                    shift_definition.small_week = config_data.get('small_week', config_data.get('smallWeek', []))
                    shift_definition.save()
                except ShiftDefinition.DoesNotExist:
                    return Response({'error': f'班次ID {shift_type_id} 不存在'}, status=400)

        return Response({'message': '大小周配置已更新'}, status=201)



@api_view(['GET', 'POST'])
def shift_definitions_list(request):
    """
    获取或创建班次定义
    """
    if request.method == 'GET':
        shift_definitions = ShiftDefinition.objects.all()
        serializer = ShiftDefinitionSerializer(shift_definitions, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
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

    if request.method == 'PUT':
        serializer = ShiftDefinitionSerializer(shift_definition, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
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

    if request.method == 'POST':
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

    if request.method == 'PUT':
        serializer = GroupConfigSerializer(group_config, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
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

    if request.method == 'POST':
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

    if request.method == 'PUT':
        serializer = PersonSerializer(person, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
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

    if request.method == 'POST':
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

    if request.method == 'PUT':
        serializer = AbsenceSerializer(absence, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        absence.delete()
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

    if request.method == 'POST':
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

    if request.method == 'PUT':
        serializer = CalendarOverrideSerializer(calendar_override, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        calendar_override.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)






@api_view(['POST'])
@permission_classes([AllowAny])
def generate_schedule_view(request):
    """
    生成排班

    请求参数:
    {
        "year_month": "YYYY-MM"
    }
    """
    try:
        year_month = request.data.get('year_month')
        if not year_month:
            return Response(
                {'error': '缺少 year_month 参数'},
                status=status.HTTP_400_BAD_REQUEST
            )

        result = generate_schedule(year_month)
        return Response(result, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
