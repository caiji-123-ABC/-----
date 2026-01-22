import dayjs from 'dayjs'
import type {
  Person,
  Absence,
  PersonOverride,
  CalendarOverride,
  SpecialDateRule,
  WeekRotationConfig,
  ScheduleResult,
  Violation,
  GlobalRules
} from '../types'
import {
  persons,
  absences,
  personOverrides,
  calendarOverrides,
  specialDateRules,
  weekRotationConfigs,
  globalRules,
  groupConfigs 
} from '../stores/scheduleStore'

// 生成排班的核心算法
export function generateSchedule(month: string): {
  results: ScheduleResult[]
  violations: Violation[]
} {
  const results: ScheduleResult[] = []
  const violations: Violation[] = []

  // 获取该月的所有日期
  const startDate = dayjs(month + '-01')
  const endDate = startDate.endOf('month')
  const days: string[] = []
  let current = startDate
  while (current.isBefore(endDate) || current.isSame(endDate, 'day')) {
    days.push(current.format('YYYY-MM-DD'))
    current = current.add(1, 'day')
  }

  // 获取参与排班的人员
  const activePersons = persons.value.filter(
    p => p.status === '在岗参与' && groupConfigs.value.find(g => g.name === p.group)?.enabled
  )
  // console.log('activePersons', activePersons)

  // 为每个人生成排班
  for (const person of activePersons) {
    // 分配A/B班（简化版：按组内顺序分配）
    const group = groupConfigs.value.find(g => g.name === person.group)
    const groupPersons = activePersons.filter(p => p.group === person.group)
    const personIndex = groupPersons.findIndex(p => p.id === person.id)
    const isOddGroup = groupPersons.length % 2 === 1

    let shift: 'A' | 'B' = 'A'
    if (group?.abStrategy === '均分') {
      if (isOddGroup && group?.oddStrategy) {
        // 奇数策略处理（简化）
        const ratio = group.oddStrategy
        if (ratio.includes('2A:3B')) {
          shift = personIndex < 2 ? 'A' : 'B'
        } else if (ratio.includes('3A:2B')) {
          shift = personIndex < 3 ? 'A' : 'B'
        }
      } else {
        shift = personIndex < Math.ceil(groupPersons.length / 2) ? 'A' : 'B'
      }
    }

    // 检查人员班次能力
    if (person.shiftCapability === 'A') shift = 'A'
    if (person.shiftCapability === 'B') shift = 'B'

    // 追踪连续工作天数和上次休息日
    let consecutiveWorkDays = 0
    let lastRestDate: string | null = null

    for (const date of days) {
      const dateObj = dayjs(date)
      const dayOfWeek = dateObj.day() // 0=周日, 1=周一, ..., 6=周六
      const weekDay = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'][dayOfWeek] || '周一'

      // 决策流程
      let status: '上班' | '休息' | '请假' | '调休' = '上班'
      let isViolation = false
      let violationReason = ''

      // 1. 检查人员锁定（优先级最高）
      const override = personOverrides.value.find(
        o => o.personName === person.name && o.date === date
      )
      console.log('override', override)
      if (override) {
        status = override.type === '必须上班' ? '上班' : '休息'
      } else {
        // 2. 检查请假/不可用
        const absence = absences.value.find(
          a =>
            a.personName === person.name &&
            date >= a.startDate &&
            date <= a.endDate &&
            a.hardUnavailable
        )
        if (absence) {
          status = absence.countAsRest ? '休息' : '请假'
        } else {
          // 3. 检查日历覆盖
          const calOverride = calendarOverrides.value.find(
            o =>
              o.date === date &&
              (o.scope === '全员' ||
                (o.scope === '指定组' && o.target === person.group) ||
                (o.scope === '指定人员' && o.target === person.name))
          )
          if (calOverride) {
            status = calOverride.type === '强制上班' ? '上班' : '调休'
          } else {
            // 4. 检查大小周规则
            // 使用系统基准日期来确定大小周轮换（可根据实际情况调整）
            // 设置基准日期及基准周类型，使用周日作为基准天
            const baseDate = dayjs('2026-01-18') // 基准日期（周日），此日所在周的类型是knownBaseWeekType
            console.log('baseDate', baseDate)
            const knownBaseWeekType = '小周' as '大周' | '小周' // 基准日期所在周的类型，根据题目描述，应为小周
            
            // 计算当前日期与基准日期之间的周数差
            // 通过计算两个日期所在的周的起始日（周一）之间的周数差来判断
            const currentWeekStart = dateObj.startOf('week') // 获取当前日期所在周的周一
            const baseWeekStart = baseDate.startOf('week') // 获取基准日期所在周的周一
            
            // 计算两个周之间的周数差
            const weeksDiff = currentWeekStart.diff(baseWeekStart, 'week')
            
            // 根据周数差判断当前周的类型
            const weekType = 
              weeksDiff % 2 === 0 
                ? knownBaseWeekType 
                : knownBaseWeekType === '大周' ? '小周' : '大周'

            // 根据大小周类型安排休息
            if (weekType === '大周') {
              // 大周：固定周日休息
              if (weekDay === '周日') {
                status = '休息'
              } else {
                status = '上班'
              }
            } else {
              // 小周：固定周六、周日休息
              if (weekDay === '周六' || weekDay === '周日') {
                status = '休息'
              } else {
                status = '上班'
              }
            }

            // 检查是否违反禁止排休规则
            if (status === '休息' && weekDay && globalRules.forbiddenRestDays.includes(weekDay)) {
              isViolation = true 
              violationReason = `违反禁止排休规则：${weekDay}不允许休息`
            }
          }
        }
      }

      // 检查连续工作天数
      if (status === '上班') {
        // 连续工作天数增加
        consecutiveWorkDays++
        
        // 检查是否超过最大连续工作天数
        if (consecutiveWorkDays > globalRules.maxConsecutiveWorkDays) {
          isViolation = true
          violationReason = `违反连续工作天数规则：已连续工作${consecutiveWorkDays}天，超过最大${globalRules.maxConsecutiveWorkDays}天`
        }
        // 注意：这里不检查最小连续工作天数，因为算法无法预知未来是否会休息
        // 最小连续工作天数的限制通常需要在休息前检查，看是否达到了最小工作天数
      } else {
        // 休息日重置连续工作天数
        lastRestDate = date
        consecutiveWorkDays = 0
      }

      results.push({
        personName: person.name,
        date,
        shift: status === '上班' ? shift : undefined,
        status,
        isViolation,
        violationReason
      })

      if (isViolation) {
        violations.push({
          month,
          date,
          personName: person.name,
          type: status === '休息' ? '违规休息' : '违规上班',
          description: violationReason
        })
      }
    }
  }

  // 检查每日在岗人数
  for (const date of days) {
    const dateObj = dayjs(date)
    const dayOfWeek = dateObj.day()
    const weekDay = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'][dayOfWeek] || '周一'

    // 计算当前日期所在的周类型（大周/小周）
    const baseDate = dayjs('2026-01-18') // 基准日期（周日），此日所在周的类型是knownBaseWeekType
    const knownBaseWeekType = '小周' as '大周' | '小周' // 基准日期所在周的类型，根据题目描述，应为小周
    
    // 计算当前日期与基准日期所在周的周数差
    const currentWeekStart = dateObj.startOf('week') // 获取当前日期所在周的周一
    const baseWeekStart = baseDate.startOf('week') // 获取基准日期所在周的周一
    
    // 计算两个周之间的周数差
    const weeksDiff = currentWeekStart.diff(baseWeekStart, 'week')
    
    // 根据周数差判断当前周的类型
    const weekType = 
      weeksDiff % 2 === 0 
        ? knownBaseWeekType 
        : knownBaseWeekType === '大周' ? '小周' : '大周'

    for (const group of groupConfigs.value.filter(g => g.enabled)) {
      // 获取当天上班的人数
      const onDutyCount = results.filter(
        r =>
          r.date === date &&
          r.status === '上班' &&  // 只统计上班状态的人            
          persons.value.find(p => p.name === r.personName)?.group === group.name
      ).length

      // 获取当天休息的人数（包括正常的大小周休息、请假、调休等）
      const restCount = results.filter(
        r =>
          r.date === date &&
          persons.value.find(p => p.name === r.personName)?.group === group.name &&
          (r.status === '休息' || r.status === '请假' || r.status === '调休')
      ).length

      // 判断是否是正常的大小周休息日
      let isNormalRestDay = false
      if (weekType === '大周' && weekDay === '周日') {
        isNormalRestDay = true
      } else if (weekType === '小周' && (weekDay === '周六' || weekDay === '周日')) {
        isNormalRestDay = true
      }

      // 如果不是正常的大小周休息日，才检查覆盖不足
      if (!isNormalRestDay && onDutyCount < group.minOnDuty) {
        violations.push({
          month,
          date,
          group: group.name,
          type: '覆盖不足',
          description: `在岗人数${onDutyCount}人，少于最少在岗人数${group.minOnDuty}人`
        })

        // 标记相关结果
        results
          .filter(
            r =>
              r.date === date &&
              persons.value.find(p => p.name === r.personName)?.group === group.name
          )
          .forEach(r => {
            r.isViolation = true
            r.violationReason = `覆盖不足：缺${group.minOnDuty - onDutyCount}人`
          })
      }
    }
  }

  return { results, violations }
}
