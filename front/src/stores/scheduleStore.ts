import { ref, reactive } from 'vue'
import type {
  GlobalRules,
  ShiftDefinition,
  GroupConfig,
  Person,
  Absence,
  PersonOverride,
  CalendarOverride,
  SpecialDateRule,
  WeekRotationConfig,
  ScheduleResult,
  Violation,
  ScheduleGenerationRecord
} from '../types'
import { api } from '../utils/api'

// 全局规则
export const globalRules = reactive<GlobalRules>({
  minConsecutiveWorkDays: 5,
  maxConsecutiveWorkDays: 6,
  forbiddenRestDays: [],
  allowedRestDays: [],
  smallWeekMustConsecutive: true,
  weekRotationMode: '全员同步',
  overrideWeekRules: true
})

// 班次定义
export const shiftDefinitions = ref<ShiftDefinition[]>([])

// 组配置
export const groupConfigs = ref<GroupConfig[]>([])

// 人员列表
export const persons = ref<Person[]>([])

// 请假列表
export const absences = ref<Absence[]>([])

// 人员锁定规则
export const personOverrides = ref<PersonOverride[]>([])

// 日历覆盖
export const calendarOverrides = ref<CalendarOverride[]>([])

// 特殊日期规则
export const specialDateRules = ref<SpecialDateRule[]>([])

// 大小周配置
export const weekRotationConfigs = ref<WeekRotationConfig[]>([])

// 排班结果
export const scheduleResults = ref<ScheduleResult[]>([])

// 违规明细
export const violations = ref<Violation[]>([])

// 生成记录
export const generationRecords = ref<ScheduleGenerationRecord[]>([])

// 工具函数：生成唯一ID
export function generateId(): string {
  return Date.now().toString(36) + Math.random().toString(36).substr(2)
}

// 从后端API加载数据
export async function loadFromApi() {
  try {
    // 加载班次定义
    shiftDefinitions.value = await api.getShiftDefinitions()
    
    // 加载组配置
    groupConfigs.value = await api.getGroupConfigs()
    
    // 加载人员信息
    persons.value = await api.getPersons()
    
    // 加载请假信息
    absences.value = await api.getAbsences()
    
    // 加载人员锁定规则
    personOverrides.value = await api.getPersonOverrides()
    
    // 加载日历覆盖
    calendarOverrides.value = await api.getCalendarOverrides()
    
    // 加载特殊日期规则
    specialDateRules.value = await api.getSpecialDateRules()
    
    // 加载大小周配置
    weekRotationConfigs.value = await api.getWeekRotationConfigs()
    
    // 加载全局规则
    const rules = await api.getGlobalRules()
    if (rules) {
      Object.assign(globalRules, rules)
    }
    
    console.log('数据已从后端加载')
  } catch (error) {
    console.error('从后端加载数据失败:', error)
  }
}

// 保存数据到后端API
export async function saveToApi() {
  try {
    // 由于后端API是CRUD操作，我们需要分别处理每种数据
    // 这里是一个简单的实现，实际项目中可能需要更复杂的同步逻辑
    
    // 注意：在实际应用中，你可能需要对比原始数据和当前数据，
    // 并决定是创建、更新还是删除特定记录
    
    // 更新全局规则
    await api.updateGlobalRules(globalRules)
    
    console.log('数据已保存到后端')
  } catch (error) {
    console.error('保存到后端失败:', error)
  }
}

// 同步特定类型的数据到后端
export async function syncShiftDefinitions() {
  try {
    // 获取当前后端数据
    const backendData = await api.getShiftDefinitions()
    
    // 将当前前端数据与后端数据同步
    for (const item of shiftDefinitions.value) {
      if (item.id) {
        // 如果有ID，更新现有记录
        await api.updateShiftDefinition(item.id, item)
      } else {
        // 如果没有ID，创建新记录
        const newItem = await api.createShiftDefinition({
          name: item.name,
          startTime: item.startTime,
          endTime: item.endTime,
          enabled: item.enabled
        })
        // 更新本地ID
        item.id = newItem.id
      }
    }
    
    // 删除后端有但前端没有的记录
    for (const backendItem of backendData) {
      const exists = shiftDefinitions.value.some(item => item.id === backendItem.id)
      if (!exists) {
        await api.deleteShiftDefinition(backendItem.id!)
      }
    }
    
    console.log('班次定义已同步到后端')
  } catch (error) {
    console.error('同步班次定义失败:', error)
  }
}

export async function syncPersons() {
  try {
    const backendData = await api.getPersons()
    
    for (const item of persons.value) {
      if (item.id) {
        await api.updatePerson(item.id, item)
      } else {
        const newItem = await api.createPerson({
          name: item.name,
          group: item.group,
          enabled: item.enabled
        })
        item.id = newItem.id
      }
    }
    
    for (const backendItem of backendData) {
      const exists = persons.value.some(person => person.id === backendItem.id)
      if (!exists) {
        await api.deletePerson(backendItem.id!)
      }
    }
    
    console.log('人员数据已同步到后端')
  } catch (error) {
    console.error('同步人员数据失败:', error)
  }
}

export async function syncAbsences() {
  try {
    const backendData = await api.getAbsences()
    
    for (const item of absences.value) {
      if (item.id) {
        await api.updateAbsence(item.id, item)
      } else {
        const newItem = await api.createAbsence({
          personId: item.personId,
          startDate: item.startDate,
          endDate: item.endDate,
          reason: item.reason,
          countAsRest: item.countAsRest
        })
        item.id = newItem.id
      }
    }
    
    for (const backendItem of backendData) {
      const exists = absences.value.some(absence => absence.id === backendItem.id)
      if (!exists) {
        await api.deleteAbsence(backendItem.id!)
      }
    }
    
    console.log('请假数据已同步到后端')
  } catch (error) {
    console.error('同步请假数据失败:', error)
  }
}

export async function syncPersonOverrides() {
  try {
    const backendData = await api.getPersonOverrides()
    
    for (const item of personOverrides.value) {
      if (item.id) {
        await api.updatePersonOverride(item.id, item)
      } else {
        const newItem = await api.createPersonOverride({
          personId: item.personId,
          date: item.date,
          lockedShift: item.lockedShift,
          lockedOff: item.lockedOff
        })
        item.id = newItem.id
      }
    }
    
    for (const backendItem of backendData) {
      const exists = personOverrides.value.some(override => override.id === backendItem.id)
      if (!exists) {
        await api.deletePersonOverride(backendItem.id!)
      }
    }
    
    console.log('人员锁定数据已同步到后端')
  } catch (error) {
    console.error('同步人员锁定数据失败:', error)
  }
}

export async function syncCalendarOverrides() {
  try {
    const backendData = await api.getCalendarOverrides()
    
    for (const item of calendarOverrides.value) {
      if (item.id) {
        await api.updateCalendarOverride(item.id, item)
      } else {
        const newItem = await api.createCalendarOverride({
          date: item.date,
          overrideType: item.overrideType
        })
        item.id = newItem.id
      }
    }
    
    for (const backendItem of backendData) {
      const exists = calendarOverrides.value.some(override => override.id === backendItem.id)
      if (!exists) {
        await api.deleteCalendarOverride(backendItem.id!)
      }
    }
    
    console.log('日历覆盖数据已同步到后端')
  } catch (error) {
    console.error('同步日历覆盖数据失败:', error)
  }
}

export async function syncSpecialDateRules() {
  try {
    const backendData = await api.getSpecialDateRules()
    
    for (const item of specialDateRules.value) {
      if (item.id) {
        await api.updateSpecialDateRule(item.id, item)
      } else {
        const newItem = await api.createSpecialDateRule({
          date: item.date,
          description: item.description,
          isWorkingDay: item.isWorkingDay
        })
        item.id = newItem.id
      }
    }
    
    for (const backendItem of backendData) {
      const exists = specialDateRules.value.some(rule => rule.id === backendItem.id)
      if (!exists) {
        await api.deleteSpecialDateRule(backendItem.id!)
      }
    }
    
    console.log('特殊日期规则已同步到后端')
  } catch (error) {
    console.error('同步特殊日期规则失败:', error)
  }
}

export async function syncWeekRotationConfigs() {
  try {
    const backendData = await api.getWeekRotationConfigs()
    
    for (const item of weekRotationConfigs.value) {
      if (item.id) {
        await api.updateWeekRotationConfig(item.id, item)
      } else {
        const newItem = await api.createWeekRotationConfig({
          month: item.month,
          firstWeekType: item.firstWeekType,
          year: item.year
        })
        item.id = newItem.id
      }
    }
    
    for (const backendItem of backendData) {
      const exists = weekRotationConfigs.value.some(config => config.id === backendItem.id)
      if (!exists) {
        await api.deleteWeekRotationConfig(backendItem.id!)
      }
    }
    
    console.log('大小周配置已同步到后端')
  } catch (error) {
    console.error('同步大小周配置失败:', error)
  }
}

export async function syncGroupConfigs() {
  try {
    const backendData = await api.getGroupConfigs()
    
    for (const item of groupConfigs.value) {
      if (item.id) {
        await api.updateGroupConfig(item.id, item)
      } else {
        const newItem = await api.createGroupConfig({
          name: item.name,
          enabled: item.enabled,
          abStrategy: item.abStrategy,
          oddStrategy: item.oddStrategy,
          minOnDuty: item.minOnDuty,
          allowBreakWeekRule: item.allowBreakWeekRule
        })
        item.id = newItem.id
      }
    }
    
    for (const backendItem of backendData) {
      const exists = groupConfigs.value.some(config => config.id === backendItem.id)
      if (!exists) {
        await api.deleteGroupConfig(backendItem.id!)
      }
    }
    
    console.log('组配置已同步到后端')
  } catch (error) {
    console.error('同步组配置失败:', error)
  }
}

// 保存到localStorage（保留用于备份或离线使用）
export function saveToLocalStorage() {
  const data = {
    globalRules,
    shiftDefinitions: shiftDefinitions.value,
    groupConfigs: groupConfigs.value,
    persons: persons.value,
    absences: absences.value,
    personOverrides: personOverrides.value,
    calendarOverrides: calendarOverrides.value,
    specialDateRules: specialDateRules.value,
    weekRotationConfigs: weekRotationConfigs.value,
    scheduleResults: scheduleResults.value,
    violations: violations.value,
    generationRecords: generationRecords.value
  }
  localStorage.setItem('scheduleSystem', JSON.stringify(data))
}

// 从localStorage加载（保留用于备份或离线使用）
export function loadFromLocalStorage() {
  const data = localStorage.getItem('scheduleSystem')
  if (data) {
    try {
      const parsed = JSON.parse(data)
      Object.assign(globalRules, parsed.globalRules || {})
      shiftDefinitions.value = parsed.shiftDefinitions || []
      groupConfigs.value = parsed.groupConfigs || []
      persons.value = parsed.persons || []
      absences.value = parsed.absences || []
      personOverrides.value = parsed.personOverrides || []
      calendarOverrides.value = parsed.calendarOverrides || []
      specialDateRules.value = parsed.specialDateRules || []
      weekRotationConfigs.value = parsed.weekRotationConfigs || []
      scheduleResults.value = parsed.scheduleResults || []
      violations.value = parsed.violations || []
      generationRecords.value = parsed.generationRecords || []
    } catch (e) {
      console.error('Failed to load from localStorage', e)
    }
  }
}