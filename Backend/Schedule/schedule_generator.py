"""
排班生成器 - 根据基本规则生成排班表
"""
from datetime import datetime, timedelta
from django.db.models import Q
from .models import Person, ShiftDefinition, Absence, CalendarOverride


def generate_schedule(year_month: str):
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

    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = datetime(year, month + 1, 1) - timedelta(days=1)

    schedule_data = []

    persons = Person.objects.select_related('shift_type', 'rotation_group', 'rotation_group__odd_shift', 'rotation_group__even_shift').all()

    # 大小周默认从大周开始
    first_week_type = '大周'

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

    # 预计算人员轮换班次
    person_shift_defs = {}
    person_shifts = {}
    for person in persons:
        if person.rotation_group:
            shift_def = person.rotation_group.odd_shift if month % 2 == 1 else person.rotation_group.even_shift
            person_shift_defs[person.id] = shift_def
        elif person.shift_type:
            person_shift_defs[person.id] = person.shift_type
        else:
            person_shifts[person.id] = ''

    # 计算参考周
    first_day_of_month = start_date.replace(day=1)
    days_since_monday = first_day_of_month.weekday()
    first_monday = first_day_of_month - timedelta(days=days_since_monday)
    reference_date = first_monday

    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime('%Y-%m-%d')

        days_since_current_monday = current_date.weekday()
        current_monday = current_date - timedelta(days=days_since_current_monday)
        weeks_diff = (current_monday - reference_date).days // 7
        is_big_week = (weeks_diff % 2 == 0 and first_week_type == '大周') or \
                      (weeks_diff % 2 == 1 and first_week_type == '小周')

        # 当天所有调休/节假日覆盖，按优先级排序
        overrides_for_date = CalendarOverride.objects.filter(
            Q(end_date__isnull=True, date=current_date) |
            Q(end_date__isnull=False, date__lte=current_date, end_date__gte=current_date)
        ).order_by('-priority', '-id')

        for person in persons:
            shift_def = person_shift_defs.get(person.id)
            shift_label = shift_def.name if shift_def else person_shifts.get(person.id, '')

            shift = shift_label
            status = '上班'
            is_violation = False
            violation_reason = ''

            shift_type_id = shift_def.id if shift_def else 'default'
            if shift_type_id in week_configs:
                work_days_for_this_person = week_configs[shift_type_id]['大周'] if is_big_week else week_configs[shift_type_id]['小周']
            else:
                work_days_for_this_person = week_configs['default']['大周'] if is_big_week else week_configs['default']['小周']

            weekday = current_date.weekday()
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
                elif override.scope == '指定组' and override.target == person.group:
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
            absence = Absence.objects.filter(
                person=person,
                start_date__lte=current_date,
                end_date__gte=current_date
            ).first()

            if absence:
                if absence.count_as_rest:
                    status = '休息'
                else:
                    status = absence.type
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
