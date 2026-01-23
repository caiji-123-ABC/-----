from django.db import models


class ShiftDefinition(models.Model):
    name = models.CharField(max_length=100, verbose_name="班次名称")
    start_time = models.TimeField(verbose_name="开始时间")
    end_time = models.TimeField(verbose_name="结束时间")
    enabled = models.BooleanField(default=True, verbose_name="是否启用")
    remark = models.TextField(blank=True, null=True, verbose_name="备注")
    big_week = models.JSONField(default=list, help_text="大周工作日列表，0-6代表周一到周日")
    small_week = models.JSONField(default=list, help_text="小周工作日列表，0-6代表周一到周日")

    class Meta:
        db_table = 'shift_definition'

    def __str__(self):
        return self.name


class GroupConfig(models.Model):
    """组配置"""
    name = models.CharField(max_length=50, unique=True)
    remark = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'group_config'

class ShiftRotationGroup(models.Model):
    """班次轮换组合"""
    name = models.CharField(max_length=100, unique=True)
    odd_shift = models.ForeignKey(
        ShiftDefinition,
        on_delete=models.CASCADE,
        related_name='rotation_group_odd',
        verbose_name='奇数月班次'
    )
    even_shift = models.ForeignKey(
        ShiftDefinition,
        on_delete=models.CASCADE,
        related_name='rotation_group_even',
        verbose_name='偶数月班次'
    )
    remark = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'shift_rotation_group'

    def __str__(self):
        return self.name

class Person(models.Model):
    """人员信息"""
    name = models.CharField(max_length=50)
    group = models.CharField(max_length=50)
    shift_type = models.ForeignKey(ShiftDefinition, on_delete=models.SET_NULL, null=True, blank=True)
    rotation_group = models.ForeignKey(ShiftRotationGroup, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = 'person'


class Absence(models.Model):
    """请假信息"""
    ABSENCE_TYPE_CHOICES = (
        ('请假', '请假'),
        ('病假', '病假'),
        ('出差', '出差'),
        ('培训', '培训'),
    )
    person = models.ForeignKey(Person, on_delete=models.CASCADE, verbose_name='姓名')
    start_date = models.DateField(verbose_name='开始日期')
    end_date = models.DateField(verbose_name='结束日期')
    type = models.CharField(max_length=20, choices=ABSENCE_TYPE_CHOICES, verbose_name='类型')
    count_as_rest = models.BooleanField(default=False, verbose_name='是否算休息')
    reason = models.TextField(blank=True, null=True, verbose_name='原因')

    def __str__(self):
        return f"{self.person.name} - {self.type}"

    class Meta:
        verbose_name = '请假/不可用'
        verbose_name_plural = '请假/不可用'


class CalendarOverride(models.Model):
    """日历覆盖"""
    OVERRIDE_TYPE_CHOICES = [
        ('上班', '上班'),
        ('休息', '休息'),
    ]
    SCOPE_CHOICES = [
        ('全员', '全员'),
        ('指定组', '指定组'),
        ('指定人员', '指定人员'),
    ]

    date = models.DateField(verbose_name='开始日期')
    end_date = models.DateField(null=True, blank=True, verbose_name='结束日期')
    override_type = models.CharField(max_length=20, choices=OVERRIDE_TYPE_CHOICES, verbose_name='覆盖类型')
    scope = models.CharField(max_length=20, choices=SCOPE_CHOICES, default='全员', verbose_name='作用范围')
    target = models.CharField(max_length=200, blank=True, null=True, verbose_name='目标(组名或人员)')
    reason = models.CharField(max_length=200, blank=True, null=True, verbose_name='原因')
    priority = models.IntegerField(default=0, verbose_name='优先级')

    class Meta:
        db_table = 'calendar_override'
        verbose_name = '日历覆盖'
        verbose_name_plural = '日历覆盖'


# class GlobalRules(models.Model):
#     """全局规则"""
#     min_consecutive_work_days = models.IntegerField(default=5)
#     max_consecutive_work_days = models.IntegerField(default=6)
#     forbidden_rest_days = models.JSONField(default=list)
#     allowed_rest_days = models.JSONField(default=list)
#     small_week_must_consecutive = models.BooleanField(default=True)
#     week_rotation_mode = models.CharField(max_length=20, default='全员同步')
#     override_week_rules = models.BooleanField(default=False)
#
#     class Meta:
#         db_table = 'global_rules'
