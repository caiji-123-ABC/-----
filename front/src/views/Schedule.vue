<template>
  <div class="schedule-page">
    <el-card
      class="schedule-card"
      v-loading="loading"
      element-loading-text="正在生成排班..."
    >
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <h3 class="card-title">排班生成</h3>
            <p class="card-subtitle">显示所选月份的排班</p>
          </div>
          <div class="header-right">
            <el-radio-group v-model="viewMode" size="small" class="view-mode">
              <el-radio-button label="month">按月</el-radio-button>
              <el-radio-button label="year">按年</el-radio-button>
            </el-radio-group>
            <el-date-picker
              v-if="viewMode === 'month'"
              v-model="selectedMonth"
              type="month"
              value-format="YYYY-MM"
              placeholder="选择月份"
              popper-class="month-picker-popper"
              style="margin-right: 12px; width: 140px;"
            />
            <el-date-picker
              v-else
              v-model="selectedYear"
              type="year"
              value-format="YYYY"
              placeholder="选择年份"
              style="margin-right: 12px; width: 120px;"
            />
            <div class="week-type-toggle">
              <span class="week-type-label">更换周类型</span>
              <el-radio-group v-model="baseWeekType" size="small">
                <el-radio-button label="大周">大周</el-radio-button>
                <el-radio-button label="小周">小周</el-radio-button>
              </el-radio-group>
            </div>
            <div class="cross-month-toggle">
              <span class="week-type-label">跨月周</span>
              <el-switch
                v-model="crossMonthContinuous"
                active-text="连续"
                inactive-text="重置"
                inline-prompt
                size="small"
              />
            </div>
            <el-button type="primary" @click="handleGenerate" :icon="Refresh" size="default" :loading="loading">
              生成排班
            </el-button>
            <el-button 
              type="success" 
              @click="handleExport" 
              :icon="Download" 
              :disabled="!hasResults || loading"
              size="default"
            >
              导出 Excel
            </el-button>
          </div>
        </div>
      </template>

      <div v-if="!hasResults" class="empty-state">
        <el-empty description="请选择月份并生成排班" :image-size="100" />
      </div>

      <div v-else>
        <el-row :gutter="16" class="summary-cards">
          <el-col :xs="24" :sm="8">
            <el-card shadow="hover" class="summary-item">
              <div class="summary-content">
                <div class="summary-icon bg-success">
                  <el-icon><User /></el-icon>
                </div>
                <div class="summary-text">
                  <div class="summary-number">{{ totalPersons }}</div>
                  <div class="summary-label">参与排班人数</div>
                </div>
              </div>
            </el-card>
          </el-col>
          <el-col :xs="24" :sm="8">
            <el-card shadow="hover" class="summary-item">
              <div class="summary-content">
                <div class="summary-icon bg-warning">
                  <el-icon><Clock /></el-icon>
                </div>
                <div class="summary-text">
                  <div class="summary-number">{{ totalDays }}</div>
                  <div class="summary-label">总天数</div>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>

        <div v-if="viewMode === 'month'" class="table-container">
          <el-table
            :data="scheduleTable"
            border
            style="width: 100%"
              :header-cell-style="{background: '#f5f7fa', fontWeight: 'bold'}"
              :row-style="{height: '50px'}"
              :row-class-name="rowClassName"
              :cell-class-name="cellClassName"
              :header-cell-class-name="headerCellClassName"
              :span-method="spanMethod"
            table-layout="fixed"
            :fit="true"
            sticky
          >
            <el-table-column prop="group" label="组名" width="80" fixed="left"
                             header-align="center" align="center" />
            <el-table-column prop="personName" label="姓名" width="80" fixed="left" 
                             header-align="center" align="center" />
            <el-table-column
              v-for="day in monthDays"
              :key="day.date"
              :label="day.labelShort"
              :class-name="[
                day.date === todayDate ? 'today-column' : '',
                day.isWeekStart ? 'week-separator' : ''
              ]"
              :min-width="day.date === todayDate ? 44 : 40"
              align="center"
            >
              <template #header>
                <div class="day-header">
                  <div class="day-date">{{ day.labelDate }}</div>
                  <div class="day-week">{{ day.labelWeek }}</div>
                </div>
              </template>
              <template #default="{ row }">
                <div
                    :class="[
                      'schedule-cell',
                      row[day.date]?.status === '休息' ? 'rest-day-cell' : 'shift-day-cell'
                    ]"
                    :style="getCellStyle(row[day.date])"
                  >
                  <div v-if="row[day.date]">
                    <div v-if="row[day.date].status === '上班'" class="shift-info">
                      <span class="shift-text">{{ row[day.date].shift }}</span>
                    </div>
                      <div v-else class="status-info">
                        {{ row[day.date].status }}
                      </div>
                    </div>
                  </div>
              </template>
            </el-table-column>
            </el-table>
        </div>

        <div v-else class="year-grid">
          <div v-for="month in yearMonths" :key="month" class="year-month">
            <div class="month-title">{{ formatMonthTitle(month) }}</div>
            <el-table
              :data="yearTables[month]?.table || []"
              border
              style="width: 100%"
                :max-height="600"
                :header-cell-style="{background: '#f5f7fa', fontWeight: 'bold'}"
                :row-style="{height: '38px'}"
                :row-class-name="rowClassNameYear(month)"
                :cell-class-name="cellClassNameYear(month)"
                :header-cell-class-name="headerCellClassNameYear(month)"
                :span-method="spanMethodYear(month)"
              table-layout="fixed"
              :fit="true"
              class="year-table"
            >
              <el-table-column prop="group" label="组名" width="70" fixed="left"
                               header-align="center" align="center" />
              <el-table-column prop="personName" label="姓名" width="70" fixed="left" 
                               header-align="center" align="center" />
              <el-table-column
              v-for="day in yearTables[month]?.days || []"
                :key="day.date"
                :label="day.labelShort"
                :class-name="day.isWeekStart ? 'week-separator' : ''"
                :min-width="40"
                align="center"
              >
                <template #header>
                  <div class="day-header">
                    <div class="day-date">{{ day.labelDate }}</div>
                    <div class="day-week">{{ day.labelWeek }}</div>
                  </div>
                </template>
                <template #default="{ row }">
                  <div
                    :class="[
                      'schedule-cell',
                      row[day.date]?.status === '休息' ? 'rest-day-cell' : 'shift-day-cell'
                    ]"
                    :style="getCellStyle(row[day.date])"
                  >
                    <div v-if="row[day.date]">
                      <div v-if="row[day.date].status === '上班'" class="shift-info">
                        <span class="shift-text">{{ row[day.date].shift }}</span>
                      </div>
                      <div v-else class="status-info">
                        {{ row[day.date].status }}
                      </div>
                    </div>
                  </div>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { Refresh, Download, User, Clock } from '@element-plus/icons-vue'
import dayjs from 'dayjs'
import { api, type ScheduleItem, type Person } from '../utils/api'
import { ElMessage } from 'element-plus'
import * as XLSX from 'xlsx'

const selectedMonth = ref(dayjs().format('YYYY-MM'))
const selectedYear = ref(dayjs().format('YYYY'))
const viewMode = ref<'month' | 'year'>('month')
const baseWeekType = ref<'大周' | '小周'>('大周')
const crossMonthContinuous = ref(true)
const todayDate = dayjs().format('YYYY-MM-DD')
const loading = ref(false)

// 后端返回的原始排班数据
const scheduleData = ref<ScheduleItem[]>([])
const scheduleYearData = ref<Record<string, ScheduleItem[]>>({})
const personInfoMap = ref(new Map<number, Person>())
const hasResults = computed(() => {
  if (viewMode.value === 'month') {
    return scheduleData.value.length > 0
  }
  return Object.values(scheduleYearData.value).some(items => items.length > 0)
})

const buildMonthDays = (yearMonth: string) => {
  const start = dayjs(yearMonth + '-01')
  const end = start.endOf('month')
  const days: { date: string; label: string; labelShort: string; labelDate: string; labelWeek: string; isWeekStart: boolean }[] = []
  let current = start
  const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']

  while (current.isBefore(end) || current.isSame(end, 'day')) {
    const dateStr = current.format('YYYY-MM-DD')
    const month = current.month() + 1
    const day = current.date()
    const weekDay = weekdays[current.day()] || '未知'

    days.push({
      date: dateStr,
      label: `${month}月${day}日 ${weekDay}`,
      labelShort: `${month}/${day}\n${weekDay}`,
      labelDate: `${month}/${day}`,
      labelWeek: weekDay,
      isWeekStart: current.day() === 1
    })
    current = current.add(1, 'day')
  }
  return days
}

const monthDays = computed(() => buildMonthDays(selectedMonth.value))

const yearMonths = computed(() => {
  return Array.from({ length: 12 }, (_, i) => {
    const month = String(i + 1).padStart(2, '0')
    return `${selectedYear.value}-${month}`
  })
})

const buildScheduleTable = (items: ScheduleItem[], days: { date: string }[]) => {
  const table: Record<string, any>[] = []
  const personMap = new Map<string, any>()
  const groupOrder: string[] = []
  const groupPersons = new Map<string, Set<string>>()
  const personGroupMap = new Map<string, string>()
  const personRotationMap = new Map<string, string>()
  const personIdMap = new Map<string, number>()

  items.forEach(item => {
    const groupName = item.group || '未分组'
    if (!groupPersons.has(groupName)) {
      groupPersons.set(groupName, new Set())
      groupOrder.push(groupName)
    }
    groupPersons.get(groupName)!.add(item.person_name)
    if (item.rotation_group) {
      personRotationMap.set(item.person_name, item.rotation_group)
    }
    if (item.shift) {
      personGroupMap.set(item.person_name, item.shift)
    }
    personIdMap.set(`${groupName}__${item.person_name}`, item.person_id)
  })

  groupOrder.forEach(groupName => {
    const names = Array.from(groupPersons.get(groupName) || [])
    names.sort((a, b) => {
      const groupA = personRotationMap.get(a) || personGroupMap.get(a) || ''
      const groupB = personRotationMap.get(b) || personGroupMap.get(b) || ''
      if (groupA !== groupB) {
        return groupA.localeCompare(groupB, 'zh-Hans-CN')
      }
      return a.localeCompare(b, 'zh-Hans-CN')
    })
    names.forEach(personName => {
      const row: Record<string, any> = {
        group: groupName,
        personName,
        personId: personIdMap.get(`${groupName}__${personName}`) || null,
        rotationGroup: personRotationMap.get(personName) || ''
      }
      days.forEach(day => {
        row[day.date] = null
      })
      const rowKey = `${groupName}__${personName}`
      personMap.set(rowKey, row)
      table.push(row)
    })
  })

  // 填充排班数据
  items.forEach(item => {
    const groupName = item.group || '未分组'
    const row = personMap.get(`${groupName}__${item.person_name}`)
    if (row) {
        row[item.date] = {
          status: item.status,
          shift: item.shift,
        }
    }
  })

  return table
}

const scheduleTable = computed(() => buildScheduleTable(scheduleData.value, monthDays.value))

const yearTables = computed(() => {
  const map: Record<string, { days: ReturnType<typeof buildMonthDays>; table: Record<string, any>[] }> = {}
  yearMonths.value.forEach(month => {
    const days = buildMonthDays(month)
    map[month] = {
      days,
      table: buildScheduleTable(scheduleYearData.value[month] || [], days)
    }
  })
  return map
})

const getPastelColor = (index: number) => {
  const hue = (index * 137.508) % 360
  return `hsl(${hue}, 80%, 86%)`
}

const shiftColorMap = computed(() => {
  const names = Array.from(
    new Set(
      scheduleData.value
        .map(item => item.shift)
        .filter((shift): shift is string => Boolean(shift))
    )
  )
  names.sort((a, b) => a.localeCompare(b, 'zh-Hans-CN'))

  const map = new Map<string, string>()
  names.forEach((name, index) => {
    map.set(name, getPastelColor(index))
  })
  return map
})

const getCellStyle = (cell?: { status: string; shift?: string }) => {
  if (!cell || cell.status !== '上班' || !cell.shift) {
    return {}
  }
  const color = shiftColorMap.value.get(cell.shift)
  if (!color) {
    return {}
  }
  return {
    backgroundColor: color,
    color: '#1f2d3d'
  }
}

const groupRowSpans = computed(() => {
    const spans: number[] = []
    let index = 0
    const rows = scheduleTable.value

    while (index < rows.length) {
      const currentRow = rows[index]
      if (!currentRow) {
        break
      }
      const groupName = currentRow.group
      let count = 1
      while (index + count < rows.length) {
        const nextRow = rows[index + count]
        if (!nextRow || nextRow.group !== groupName) {
          break
        }
        count += 1
      }
      spans[index] = count
    for (let i = 1; i < count; i += 1) {
      spans[index + i] = 0
    }
    index += count
  }

  return spans
})

const spanMethod = ({ rowIndex, columnIndex }: { rowIndex: number; columnIndex: number }) => {
  if (columnIndex !== 0) {
    return { rowspan: 1, colspan: 1 }
  }

  const span = groupRowSpans.value[rowIndex] ?? 1
  if (span === 0) {
    return { rowspan: 0, colspan: 0 }
  }
  return { rowspan: span, colspan: 1 }
}

const cellClassName = ({ columnIndex }: { columnIndex: number }) => {
  if (columnIndex < 2) {
    return ''
  }
  const day = monthDays.value[columnIndex - 2]
  if (day?.isWeekStart) {
    return 'week-separator'
  }
  return ''
}

const headerCellClassName = ({ columnIndex }: { columnIndex: number }) => {
  if (columnIndex < 2) {
    return ''
  }
  const day = monthDays.value[columnIndex - 2]
  if (day?.isWeekStart) {
    return 'week-separator'
  }
  return ''
}

const rowClassName = ({ rowIndex }: { rowIndex: number }) => {
  const rows = scheduleTable.value
  if (rowIndex <= 0 || rowIndex >= rows.length) {
    return ''
  }
  const current = rows[rowIndex]
  const previous = rows[rowIndex - 1]
  if (!current || !previous) {
    return ''
  }
  if (current.group !== previous.group) {
    return 'group-separator'
  }
  if ((current.rotationGroup || '') !== (previous.rotationGroup || '')) {
    return 'rotation-separator'
  }
  return ''
}

const spanMethodYear = (month: string) => {
  return ({ rowIndex, columnIndex }: { rowIndex: number; columnIndex: number }) => {
    if (columnIndex !== 0) {
      return { rowspan: 1, colspan: 1 }
    }
    const rows = yearTables.value[month]?.table || []
    const spans: number[] = []
    let index = 0
    while (index < rows.length) {
      const currentRow = rows[index]
      if (!currentRow) {
        break
      }
      const groupName = currentRow.group
      let count = 1
      while (index + count < rows.length) {
        const nextRow = rows[index + count]
        if (!nextRow || nextRow.group !== groupName) {
          break
        }
        count += 1
      }
      spans[index] = count
      for (let i = 1; i < count; i += 1) {
        spans[index + i] = 0
      }
      index += count
    }
    const span = spans[rowIndex] ?? 1
    if (span === 0) {
      return { rowspan: 0, colspan: 0 }
    }
    return { rowspan: span, colspan: 1 }
  }
}

const rowClassNameYear = (month: string) => {
  return ({ rowIndex }: { rowIndex: number }) => {
    const rows = yearTables.value[month]?.table || []
    if (rowIndex <= 0 || rowIndex >= rows.length) {
      return ''
    }
    const current = rows[rowIndex]
    const previous = rows[rowIndex - 1]
    if (!current || !previous) {
      return ''
    }
    if (current.group !== previous.group) {
      return 'group-separator'
    }
    if ((current.rotationGroup || '') !== (previous.rotationGroup || '')) {
      return 'rotation-separator'
    }
    return ''
  }
}

const cellClassNameYear = (month: string) => {
  return ({ columnIndex }: { columnIndex: number }) => {
    if (columnIndex < 2) {
      return ''
    }
    const days = yearTables.value[month]?.days || []
    const day = days[columnIndex - 2]
    if (day?.isWeekStart) {
      return 'week-separator'
    }
    return ''
  }
}

const headerCellClassNameYear = (month: string) => {
  return ({ columnIndex }: { columnIndex: number }) => {
    if (columnIndex < 2) {
      return ''
    }
    const days = yearTables.value[month]?.days || []
    const day = days[columnIndex - 2]
    if (day?.isWeekStart) {
      return 'week-separator'
    }
    return ''
  }
}

const totalPersons = computed(() => {
  if (viewMode.value === 'month') {
    return scheduleTable.value.length
  }
  const set = new Set<string>()
  Object.values(scheduleYearData.value).forEach(items => {
    items.forEach(item => {
      set.add(`${item.group || '未分组'}__${item.person_name}`)
    })
  })
  return set.size
})

const totalDays = computed(() => {
  if (viewMode.value === 'month') {
    return monthDays.value.length
  }
  return yearMonths.value.reduce((sum, month) => sum + buildMonthDays(month).length, 0)
})

const formatMonthTitle = (yearMonth: string) => {
  const [year, month] = yearMonth.split('-')
  return `${year}年${Number(month)}月`
}

const handleGenerateYear = async () => {
  if (!selectedYear.value) {
    ElMessage.warning('请选择年份')
    return
  }
  try {
    loading.value = true
    const result = await api.generateYearSchedule(
      selectedYear.value,
      baseWeekType.value,
      crossMonthContinuous.value
    )
    const resultMap: Record<string, ScheduleItem[]> = {}
    if (result?.schedules) {
      Object.entries(result.schedules).forEach(([month, payload]) => {
        resultMap[month] = payload?.schedule || []
      })
    }
    scheduleYearData.value = resultMap
    ElMessage.success('全年排班生成成功')
  } catch (error) {
    console.error('生成全年排班失败:', error)
    ElMessage.error('生成全年排班失败')
  } finally {
    loading.value = false
  }
}

const handleGenerate = async () => {
  if (viewMode.value === 'year') {
    await handleGenerateYear()
    return
  }

  try {
    loading.value = true
    const result = await api.generateSchedule(
      selectedMonth.value,
      baseWeekType.value,
      crossMonthContinuous.value
    )
    if (result) {
      scheduleData.value = result.schedule
      ElMessage.success('排班生成成功')
    }
  } catch (error) {
    console.error('生成排班失败:', error)
    ElMessage.error('生成排班失败')
  } finally {
    loading.value = false
  }
}

const handleExport = async () => {
  if (viewMode.value === 'year') {
    ElMessage.warning('年度视图暂不支持导出')
    return
  }
  if (!hasResults.value) {
    ElMessage.warning('没有可导出的数据')
    return
  }

  if (personInfoMap.value.size === 0) {
    try {
      const persons = await api.getPersons()
      const map = new Map<number, Person>()
      persons.forEach(person => {
        map.set(person.id, person)
      })
      personInfoMap.value = map
    } catch (error) {
      console.warn('加载人员信息失败，导出UID可能为空', error)
    }
  }

  let shiftInfoText = '班次信息: 休息'
  try {
    const shiftDefs = await api.getShiftDefinitions()
    if (shiftDefs.length > 0) {
      const parts = shiftDefs.map(def => `${def.name}: ${def.startTime}-${def.endTime}`)
      shiftInfoText = `班次信息: ${parts.join(', ')}, 休息`
    }
  } catch (error) {
    console.warn('加载班次信息失败，将使用默认提示', error)
  }

  const groupNames = Array.from(new Set(scheduleTable.value.map(row => row.group))).filter(Boolean)
  const title = groupNames.length === 1 ? `${groupNames[0]}排班表` : '排班表'
  const noteText = '注意: UID为用户唯一标识，请与员工表保持一致，排班数据中UID不能重复'

  const headerRow = ['UID', '部门', '工号', '姓名', ...monthDays.value.map(day => `${dayjs(day.date).format('YYYY/M/D')}\n${day.labelWeek}`)]
  const dataRows = scheduleTable.value.map(row => {
    const personInfo = row.personId ? personInfoMap.value.get(row.personId) : undefined
    const rowData: (string | number)[] = [
      personInfo?.uid || '',
      row.group || '',
      '',
      row.personName
    ]
    monthDays.value.forEach(day => {
      const cell = row[day.date]
      let value = ''
      if (cell) {
        value = cell.status === '上班' ? (cell.shift || '') : cell.status
      }
      rowData.push(value)
    })
    return rowData
  })

  const aoa = [
    [title],
    [noteText],
    [shiftInfoText],
    headerRow,
    ...dataRows
  ]

  const ws = XLSX.utils.aoa_to_sheet(aoa)
  const totalCols = headerRow.length
  ws['!merges'] = [
    { s: { r: 0, c: 0 }, e: { r: 0, c: totalCols - 1 } },
    { s: { r: 1, c: 0 }, e: { r: 1, c: totalCols - 1 } },
    { s: { r: 2, c: 0 }, e: { r: 2, c: totalCols - 1 } }
  ]
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, 'schedule')

  const monthObj = dayjs(selectedMonth.value + '-01')
  const fileName = `schedule_${monthObj.year()}-${monthObj.month() + 1}.xlsx`
  XLSX.writeFile(wb, fileName)
  ElMessage.success('导出成功')
}

// 监听月份变化，自动拉取排班
watch(selectedMonth, (newVal) => {
  if (newVal && viewMode.value === 'month') {
    handleGenerate()
  }
}, { immediate: true })

watch(selectedYear, (newVal) => {
  if (newVal && viewMode.value === 'year') {
    handleGenerate()
  }
})

watch(viewMode, (newVal) => {
  if (newVal === 'year') {
    handleGenerateYear()
  } else if (newVal === 'month') {
    handleGenerate()
  }
})

watch(baseWeekType, () => {
  if (viewMode.value === 'year') {
    handleGenerateYear()
  } else {
    handleGenerate()
  }
})

watch(crossMonthContinuous, () => {
  if (viewMode.value === 'year') {
    handleGenerateYear()
  } else {
    handleGenerate()
  }
})
</script>

<style scoped>
.schedule-page {
  padding: 20px;
}

.schedule-card {
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
}

.header-left {
  display: flex;
  flex-direction: column;
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  margin: 0 0 4px 0;
  color: #303133;
}

.card-subtitle {
  font-size: 14px;
  color: #909399;
  margin: 0;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.week-type-toggle {
  display: flex;
  align-items: center;
  gap: 6px;
}

.cross-month-toggle {
  display: flex;
  align-items: center;
  gap: 6px;
}

.week-type-label {
  font-size: 12px;
  color: #606266;
}

.view-mode :deep(.el-radio-button__inner) {
  padding: 6px 10px;
}

.empty-state {
  padding: 40px;
  text-align: center;
}

.summary-cards {
  margin-bottom: 24px;
}

.summary-item {
  border-radius: 10px;
  transition: transform 0.3s ease;
  height: 100%;
}

.summary-item:hover {
  transform: translateY(-4px);
}

.summary-content {
  display: flex;
  align-items: center;
}

.summary-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 50px;
  height: 50px;
  border-radius: 10px;
  margin-right: 12px;
  color: white;
}

.bg-success {
  background: linear-gradient(135deg, #67c23a 0%, #85ce61 100%);
}

.bg-warning {
  background: linear-gradient(135deg, #e6a23c 0%, #ebb563 100%);
}

.bg-danger {
  background: linear-gradient(135deg, #f56c6c 0%, #f78989 100%);
}

.summary-text {
  flex: 1;
}

.summary-number {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.summary-label {
  font-size: 14px;
  color: #909399;
}

.table-container {
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #ebeef5;
}

:deep(.el-table .cell) {
  padding: 0 !important;
  line-height: 1.2;
}

:deep(.el-table th .cell) {
  font-size: 11px;
  padding: 6px 0;
  line-height: 1.2;
}

:deep(.el-table th) {
  height: 54px;
}

.day-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  line-height: 1.1;
}

.day-date {
  font-size: 11px;
  font-weight: 600;
}

.day-week {
  font-size: 11px;
  color: #606266;
}

.schedule-cell {
  width: 100%;
  height: 100%;
  min-height: 46px;
  padding: 0;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0;
  transition: background-color 0.2s ease;
}

.today-cell {
  background-color: #fff9e6 !important;
  border: 1px solid #ffd700 !important;
}

:deep(.today-column .cell) {
  background-color: #fff9e6;
  font-weight: 600;
  color: #a06200;
}

:deep(.week-separator) {
  position: relative;
}

:deep(.week-separator)::before {
  content: '';
  position: absolute;
  top: -1px;
  bottom: -1px;
  left: -1px;
  width: 3px;
  background-color: #7b8188;
  z-index: 2;
}

.shift-info {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.shift-text {
  font-size: 11px;
  font-weight: 600;
  line-height: 1.2;
}

.status-info {
  color: #909399;
  font-size: 11px;
}

.rest-day-cell {
  background-color: #f3f6fb;
}

.shift-day-cell {
  background-color: #ffffff;
}

:deep(.el-table__body tr.group-separator td) {
  border-top: 1px solid #606266 !important;
  box-shadow: inset 0 5px 0 #606266;
}

:deep(.el-table__fixed-body-wrapper tr.group-separator td),
:deep(.el-table__fixed-right-body-wrapper tr.group-separator td) {
  border-top: 5px solid #606266 !important;
  box-shadow: inset 0 5px 0 #606266;
}

:deep(.el-table__body tr.rotation-separator td) {
  border-top: 1px solid #c0c4cc !important;
  box-shadow: inset 0 2px 0 #c0c4cc;
}

:deep(.el-table__fixed-body-wrapper tr.rotation-separator td),
:deep(.el-table__fixed-right-body-wrapper tr.rotation-separator td) {
  border-top: 2px solid #c0c4cc !important;
  box-shadow: inset 0 2px 0 #c0c4cc;
}

.year-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.year-month {
  border: 1px solid #ebeef5;
  border-radius: 8px;
  background-color: #ffffff;
  padding: 8px;
}

.month-title {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 8px;
  text-align: center;
}

.year-table :deep(.el-table .cell) {
  padding: 0 !important;
}

.year-table :deep(.el-table th .cell) {
  font-size: 10px;
  padding: 4px 0;
}

.year-table :deep(.el-table th) {
  height: 48px;
}

.year-table .schedule-cell {
  min-height: 34px;
  height: 34px;
}

.year-table .shift-text,
.year-table .status-info {
  font-size: 10px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .card-header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .header-right {
    order: -1;
    justify-content: space-between;
  }
  
  .header-left {
    text-align: center;
  }
  
  .table-container {
    overflow-x: hidden;
  }

  .year-grid {
    grid-template-columns: 1fr;
  }
}
</style>
