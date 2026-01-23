"""
排班生成器 - 根据基本规则生成排班表
"""
from datetime import datetime, timedelta, date
from django.db.models import Q
from .models import Person, ShiftDefinition, Absence, CalendarOverride


def generate_schedule(year_month: str, base_week_type: str = '大周', cross_month_continuous: bool = True):
    """
    根据月份生成排班表

    规则说明：
    1. 按组对人员分类
    2. 每个组内按人数分配 A/B 班，进行月度轮换
    3. 每个班次有各自的大小周工作日配置
    4. 根据日期的大小周类型和人员班次，判断是否上班
    5. 调休/节假日覆盖支持优先级
    """
    year, month = map(int, year_month.split('-'))

    start_date = datetime(year, month, 1).date()
    if month == 12:
        end_date = (datetime(year + 1, 1, 1) - timedelta(days=1)).date()
    else:
        end_date = (datetime(year, month + 1, 1) - timedelta(days=1)).date()

    schedule_data = []

    persons = list(
        Person.objects.select_related(
            'group',
            'shift_type',
            'rotation_group',
            'rotation_group__odd_shift',
            'rotation_group__even_shift'
        ).all()
    )

    # 大小周以基准周计算，可选跨月连续
    base_week_type = '小周' if base_week_type == '小周' else '大周'
    base_date = date(year, 1, 1) if cross_month_continuous else start_date
    base_date = base_date - timedelta(days=base_date.weekday())

    # 按班次类型组织大小周配置
    week_configs = {}
    try:
        all_shift_definitions = ShiftDefinition.objects.all()
        for shift_def in all_shift_definitions:
            shift_key = shift_def.id
            if shift_key not in week_configs:
                week_configs[shift_key] = {}

            big_week_work_days = set(shift_def.big_week) if shift_def.big_week else {0, 1, 2, 3, 4}
            small_week_work_days = set(shift_def.small_week) if shift_def.small_week else {0, 1, 2, 3, 4, 5}

            week_configs[shift_key]['大周'] = big_week_work_days
            week_configs[shift_key]['小周'] = small_week_work_days

        if not week_configs:
            week_configs = {
                'default': {
                    '大周': {0, 1, 2, 3, 4},
                    '小周': {0, 1, 2, 3, 4, 5}
                }
            }
    except Exception as e:
        print(f"加载配置时出错: {e}")
        week_configs = {
            'default': {
                '大周': {0, 1, 2, 3, 4},
                '小周': {0, 1, 2, 3, 4, 5}
            }
        }

    # 预计算人员班次配置
    person_fixed_shifts = {}
    person_rotation_shifts = {}
    for person in persons:
        if person.rotation_group:
            person_rotation_shifts[person.id] = {
                'odd': person.rotation_group.odd_shift,
                'even': person.rotation_group.even_shift,
            }
        elif person.shift_type:
            person_fixed_shifts[person.id] = person.shift_type
        else:
            person_fixed_shifts[person.id] = None

    # 预计算日期序列
    date_info_list = []
    current_date = start_date
    while current_date <= end_date:
        days_since_current_monday = current_date.weekday()
        current_monday = current_date - timedelta(days=days_since_current_monday)
        weeks_diff = (current_monday - base_date).days // 7
        is_big_week = (weeks_diff % 2 == 0 and base_week_type == '大周') or \
                      (weeks_diff % 2 == 1 and base_week_type == '小周')
        date_info_list.append({
            'date': current_date,
            'date_str': current_date.strftime('%Y-%m-%d'),
            'weekday': current_date.weekday(),
            'is_big_week': is_big_week,
            'week_start_month': current_monday.month
        })
        current_date += timedelta(days=1)

    # 预加载调休/节假日覆盖
    overrides_by_date = {}
    overrides = CalendarOverride.objects.filter(
        Q(end_date__isnull=True, date__gte=start_date, date__lte=end_date) |
        Q(end_date__isnull=False, date__lte=end_date, end_date__gte=start_date)
    )
    for override in overrides:
        range_start = override.date
        range_end = override.end_date or override.date
        if range_end < range_start:
            range_start, range_end = range_end, range_start
        cursor = max(range_start, start_date)
        range_end = min(range_end, end_date)
        while cursor <= range_end:
            overrides_by_date.setdefault(cursor, []).append(override)
            cursor += timedelta(days=1)
    for date_key in overrides_by_date:
        overrides_by_date[date_key].sort(key=lambda x: (x.priority, x.id), reverse=True)

    # 预加载请假记录
    absences_by_person = {}
    absences = Absence.objects.filter(start_date__lte=end_date, end_date__gte=start_date).select_related('person')
    for absence in absences:
        absences_by_person.setdefault(absence.person_id, []).append(absence)

    for date_info in date_info_list:
        current_date = date_info['date']
        date_str = date_info['date_str']
        weekday = date_info['weekday']
        is_big_week = date_info['is_big_week']
        rotation_month = month
        if cross_month_continuous and date_info['week_start_month'] != current_date.month:
            rotation_month = date_info['week_start_month']
        overrides_for_date = overrides_by_date.get(current_date, [])

        for person in persons:
            group_name = person.group.name if person.group else '未分组'
            shift_def = None
            if person.id in person_rotation_shifts:
                rotation = person_rotation_shifts[person.id]
                shift_def = rotation['odd'] if rotation_month % 2 == 1 else rotation['even']
            else:
                shift_def = person_fixed_shifts.get(person.id)
            shift_label = shift_def.name if shift_def else ''

            shift = shift_label
            status = '上班'
            is_violation = False
            violation_reason = ''

            shift_type_id = shift_def.id if shift_def else 'default'
            if shift_type_id in week_configs:
                work_days_for_this_person = week_configs[shift_type_id]['大周'] if is_big_week else week_configs[shift_type_id]['小周']
            else:
                work_days_for_this_person = week_configs['default']['大周'] if is_big_week else week_configs['default']['小周']

            if weekday not in work_days_for_this_person:
                status = '休息'
                shift = ''
            else:
                status = '上班'

            # 处理调休/节假日覆盖（按优先级）
            for override in overrides_for_date:
                apply = False
                if override.scope == '全员':
                    apply = True
                elif override.scope == '指定组' and override.target == group_name:
                    apply = True
                elif override.scope == '指定人员' and override.target == person.name:
                    apply = True

                if apply:
                    if override.override_type == '上班':
                        status = '上班'
                        shift = shift_label
                    elif override.override_type == '休息':
                        status = '休息'
                        shift = ''
                    break

            # 请假记录最后覆盖调休/节假日结果
            absence = None
            for item in absences_by_person.get(person.id, []):
                if item.start_date <= current_date <= item.end_date:
                    absence = item
                    break

            if absence:
                if absence.count_as_rest:
                    status = '休息'
                else:
                    status = absence.type
                shift = ''

            schedule_data.append({
                'person_id': person.id,
                'person_name': person.name,
                'group': group_name,
                'rotation_group': person.rotation_group.name if person.rotation_group else '',
                'date': date_str,
                'shift': shift if status == '上班' else '',
                'status': status,
                'is_violation': is_violation,
                'violation_reason': violation_reason
            })

    return {
        'schedule': sorted(
            schedule_data,
            key=lambda item: (
                item['date'],
                item.get('group') or '',
                item.get('shift') or '',
                item.get('person_name') or ''
            )
        )
    }
