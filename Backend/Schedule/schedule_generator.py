"""
排班生成器 - 根据基本规则生成排班表
"""
from datetime import datetime, timedelta
from django.utils import timezone
from .models import Person, GroupConfig, ShiftDefinition, Absence, PersonOverride, CalendarOverride, WeekRotationConfig
import calendar


def generate_schedule(year_month: str):
    """
    根据月份生成排班表
    
    算法说明：
    1. 按组对人员分类
    2. 每个组内按班次分配两批（A班、B班），进行月度轮换
    3. 每个班次有各自的大小周工作日配置
    4. 根据日期的大小周类型和人员班次，判断是否上班
    
    Args:
        year_month: 格式为 'YYYY-MM' 的月份字符串
    
    Returns:
        {
            'schedule': [
                {
                    'person_id': int,
                    'person_name': str,
                    'group': str,
                    'date': 'YYYY-MM-DD',
                    'shift': str,  # 'A'或'B'，无班次时为''
                    'status': str,  # '上班' 或 '休息'
                    'is_violation': bool,
                    'violation_reason': str
                },
                ...
            ],
            'violations': [...]
        }
    """
    # 解析年月
    year, month = map(int, year_month.split('-'))
    
    # 初始化违规列表
    violations = []
    
    # 获取该月的所有日期
    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = datetime(year, month + 1, 1) - timedelta(days=1)
    
    schedule_data = []
    
    # 获取所有在岗人员
    persons = Person.objects.select_related('shift_type').all()
    
    # 获取大小周配置，默认为大周
    try:
        # 根据具体年月查找配置
        month_str = f"{year}-{month:02d}"
        week_rotation_config = WeekRotationConfig.objects.filter(month=month_str).first()
        if week_rotation_config:
            first_week_type = week_rotation_config.first_week_type
        else:
            first_week_type = '大周'  # 默认值
    except:
        first_week_type = '大周'  # 出错时的默认值

    # 获取大小周工作日安排配置，按班次类型分组
    week_configs = {}
    try:
        # 获取所有班次定义及其关联的大小周配置
        all_shift_definitions = ShiftDefinition.objects.all()
        
        # 按班次类型组织配置
        for shift_def in all_shift_definitions:
            shift_key = shift_def.id
            if shift_key not in week_configs:
                week_configs[shift_key] = {}
            
            # 直接使用配置的工作日列表，不再取补集
            # 一周七天：0-6 (周一到周日)
            
            # 直接使用工作日配置
            big_week_work_days = set(shift_def.big_week) if shift_def.big_week else {0, 1, 2, 3, 4}
            small_week_work_days = set(shift_def.small_week) if shift_def.small_week else {0, 1, 2, 3, 4, 5}
            
            week_configs[shift_key]['大周'] = big_week_work_days
            week_configs[shift_key]['小周'] = small_week_work_days
    
        # 如果没有通用配置，使用默认配置
        if not week_configs:
            week_configs = {
                'default': {
                    '大周': {0, 1, 2, 3, 4},      # 大周：周一到周五上班
                    '小周': {0, 1, 2, 3, 4, 5}   # 小周：周一到周六上班
                }
            }
    except Exception as e:
        print(f"加载配置时出错: {e}")
        # 如果没有配置，则使用默认规则
        week_configs = {
            'default': {
                '大周': {0, 1, 2, 3, 4},      # 大周：周一到周五上班
                '小周': {0, 1, 2, 3, 4, 5}   # 小周：周一到周六上班
            }
        }

    # 按组分配A/B班
    group_persons = {}
    for person in persons:
        if person.group not in group_persons:
            group_persons[person.group] = []
        group_persons[person.group].append(person)
    
    # 为每个组的人分配班次（按月轮换）
    person_shifts = {}  # person_id -> 'A' or 'B'
    for group, group_member_list in group_persons.items():
        group_member_list.sort(key=lambda p: p.id)  # 按ID排序确保一致性
        
        # 计算该月是奇数月还是偶数月（用于轮换）
        # 简单逻辑：奇数月A班在前一半，偶数月B班在前一半
        is_odd_month = month % 2 == 1
        half_count = len(group_member_list) // 2
        
        for idx, person in enumerate(group_member_list):
            if is_odd_month:
                person_shifts[person.id] = 'A' if idx < half_count else 'B'
            else:
                person_shifts[person.id] = 'B' if idx < half_count else 'A'
    
    # 获取第一个完整的周的开始日期作为基准
    # 找到当月第一天所在的周的周一
    first_day_of_month = start_date.replace(day=1)
    # 如果第一天不是周一，则找到这一周的周一
    days_since_monday = first_day_of_month.weekday()
    first_monday = first_day_of_month - timedelta(days=days_since_monday)
    
    # 计算基准日期用于判断大小周
    # 我们使用当月第一个周一作为参考点，确定当月第一周的类型
    reference_date = first_monday

    # 生成每一天的排班
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime('%Y-%m-%d')
        
        # 判断当前日期属于大周还是小周
        # 计算当前日期所在周的周一
        days_since_current_monday = current_date.weekday()
        current_monday = current_date - timedelta(days=days_since_current_monday)
        
        # 计算当前周与参考周之间相隔多少个完整周
        weeks_diff = (current_monday - reference_date).days // 7
        is_big_week = (weeks_diff % 2 == 0 and first_week_type == '大周') or \
                      (weeks_diff % 2 == 1 and first_week_type == '小周')
        is_small_week = not is_big_week

        for person in persons:
            shift = person_shifts.get(person.id, '')
            status = '上班'
            is_violation = False
            violation_reason = ''
            
            # 根据人员的班次类型获取对应的工作日安排
            person_shift_type_id = person.shift_type.id if person.shift_type else 'default'
            
            # 如果当前人员有班次配置，使用该配置，否则使用默认配置
            if person_shift_type_id in week_configs:
                work_days_for_this_person = week_configs[person_shift_type_id]['大周'] if is_big_week else week_configs[person_shift_type_id]['小周']
            else:
                # 如果找不到特定班次配置，使用默认配置
                work_days_for_this_person = week_configs['default']['大周'] if is_big_week else week_configs['default']['小周']
            
            # 根据大小周规则设置默认休息
            weekday = current_date.weekday()
            # 根据当前人员的班次配置判断是否上班
            if weekday not in work_days_for_this_person:
                status = '休息'
                shift = ''
            else:
                status = '上班'

            # 检查请假记录 (Absence)
            absence = Absence.objects.filter(
                person=person,
                start_date__lte=current_date,
                end_date__gte=current_date
            ).first()
            
            if absence:
                if absence.count_as_rest:
                    status = '休息'
                else:
                    status = absence.type  # 请假、病假、出差等
                shift = ''
            
            # 检查人员锁定规则 (PersonOverride)
            person_override = PersonOverride.objects.filter(
                person=person,
                date=current_date
            ).first()
            
            if person_override:
                if person_override.type == '必须休息':
                    status = '休息'
                    shift = ''
                elif person_override.type == '必须上班':
                    status = '上班'
                    # 保持原班次
            
            # 检查日历覆盖规则 (CalendarOverride)
            calendar_override = CalendarOverride.objects.filter(
                date__lte=current_date,
                end_date__gte=current_date
            ).first() or CalendarOverride.objects.filter(
                date=current_date,
                end_date__isnull=True
            ).first()
            
            if calendar_override:
                # 检查范围是否应用到此人
                apply = False
                if calendar_override.scope == '全员':
                    apply = True
                elif calendar_override.scope == '指定组' and calendar_override.target == person.group:
                    apply = True
                elif calendar_override.scope == '指定人员' and calendar_override.target == person.name:
                    apply = True
                
                if apply:
                    if calendar_override.override_type == '上班':
                        status = '上班'
                    elif calendar_override.override_type == '休息':
                        status = '休息'
                        shift = ''
            
            schedule_data.append({
                'person_id': person.id,
                'person_name': person.name,
                'group': person.group,
                'date': date_str,
                'shift': shift if status == '上班' else '',
                'status': status,
                'is_violation': is_violation,
                'violation_reason': violation_reason
            })
        
        current_date += timedelta(days=1)
    
    return {
        'schedule': schedule_data,
        'violations': violations
    }