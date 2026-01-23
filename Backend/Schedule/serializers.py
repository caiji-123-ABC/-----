from rest_framework import serializers
from .models import *


class ShiftDefinitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShiftDefinition
        fields = '__all__'


class GroupConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupConfig
        fields = '__all__'

class ShiftRotationGroupSerializer(serializers.ModelSerializer):
    oddShiftName = serializers.CharField(source='odd_shift.name', read_only=True)
    evenShiftName = serializers.CharField(source='even_shift.name', read_only=True)

    class Meta:
        model = ShiftRotationGroup
        fields = '__all__'


class PersonSerializer(serializers.ModelSerializer):
    shiftType = serializers.CharField(source='shift_type.name', read_only=True)
    rotationGroupName = serializers.CharField(source='rotation_group.name', read_only=True)
    groupName = serializers.CharField(source='group.name', read_only=True)

    class Meta:
        model = Person
        fields = '__all__'


class AbsenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Absence
        fields = '__all__'


class CalendarOverrideSerializer(serializers.ModelSerializer):
    class Meta:
        model = CalendarOverride
        fields = '__all__'
