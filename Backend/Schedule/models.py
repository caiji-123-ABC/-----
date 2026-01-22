from django.db import models


class ShiftDefinition(models.Model):
    name = models.CharField(max_length=100, verbose_name="班次名称")
    start_time = models.TimeField(verbose_name="开始时间")
    end_time = models.TimeField(verbose_name="结束时间")
    enabled = models.BooleanField(default=True, verbose_name="是否启用")
    remark = models.TextField(blank=True, null=True, verbose_name="备注")
    # 添加大小周配置字段
    big_week = models.JSONField(default=list, help_text="大周工作日列表，0-6代表周一到周日")
    small_week = models.JSONField(default=list, help_text="小周工作日列表，0-6代表周一到周日")

    class Meta:
        db_table = 'shift_definition'

    def __str__(self):
        return self.name


class GroupConfig(models.Model):
    """组配置"""
    name = models.CharField(max_length=50, unique=True)
    remark = models.TextField(null=True, blank=True)  # 备注字段

    class Meta:
        db_table = 'group_config'


class Person(models.Model):
    """人员信息"""
    name = models.CharField(max_length=50)
    group = models.CharField(max_length=50)
    shift_type = models.ForeignKey(ShiftDefinition, on_delete=models.SET_NULL, null=True, blank=True)

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
    reason = models.TextField(blank=True, null=True, verbose_name='原因')  # 修改为可选字段
    
    def __str__(self):
        return f"{self.person.name} - {self.type}"
    
    class Meta:
        verbose_name = '请假/不可用'
        verbose_name_plural = '请假/不可用'


class PersonOverride(models.Model):
    """人员锁定规则"""
    LOCK_TYPE_CHOICES = [
        ('必须上班', '必须上班'),
        ('必须休息', '必须休息'),
    ]
    person = models.ForeignKey(Person, on_delete=models.CASCADE, verbose_name='人员')
    date = models.DateField(verbose_name='日期')
    type = models.CharField(max_length=20, choices=LOCK_TYPE_CHOICES, default='必须上班', verbose_name='锁定类型')
    reason = models.CharField(max_length=200, verbose_name='原因')
    remark = models.TextField(blank=True, null=True, verbose_name='备注')

    class Meta:
        db_table = 'person_override'
        verbose_name = '人员锁定规则'
        verbose_name_plural = '人员锁定规则'


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
    target = models.CharField(max_length=200, blank=True, null=True, verbose_name='目标(组名或人名)')
    reason = models.CharField(max_length=200, blank=True, null=True, verbose_name='原因')

    class Meta:
        db_table = 'calendar_override'
        verbose_name = '日历覆盖'
        verbose_name_plural = '日历覆盖'


class SpecialDateRule(models.Model):
    """特殊日期规则"""
    date = models.DateField(unique=True)
    description = models.CharField(max_length=100)
    is_working_day = models.BooleanField(default=False)

    class Meta:
        db_table = 'special_date_rule'


class WeekRotationConfig(models.Model):
    """大小周配置 - 每个月使用哪种周类型"""
    MONTH_CHOICES = [
        ('一月', '一月'), ('二月', '二月'), ('三月', '三月'), ('四月', '四月'),
        ('五月', '五月'), ('六月', '六月'), ('七月', '七月'), ('八月', '八月'),
        ('九月', '九月'), ('十月', '十月'), ('十一月', '十一月'), ('十二月', '十二月')
    ]
    
    month = models.CharField(max_length=10, choices=MONTH_CHOICES)
    first_week_type = models.CharField(max_length=10, choices=[('大周', '大周'), ('小周', '小周')])
    year = models.IntegerField()

    class Meta:
        db_table = 'week_rotation_config'
        unique_together = ('month', 'year')


# class GlobalRules(models.Model):
#     """全局规则"""
#     min_consecutive_work_days = models.IntegerField(default=5)
#     max_consecutive_work_days = models.IntegerField(default=6)
#     forbidden_rest_days = models.JSONField(default=list)
#     allowed_rest_days = models.JSONField(default=list)
#     small_week_must_consecutive = models.BooleanField(default=True)
#     week_rotation_mode = models.CharField(max_length=20, default='全员同步')
#     override_week_rules = models.BooleanField(default=False)

#     class Meta:
#         db_table = 'global_rules'
