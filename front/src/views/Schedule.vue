<template>
  <div class="schedule-page">
    <el-card class="schedule-card">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <h3 class="card-title">排班生成</h3>
            <p class="card-subtitle">自动为选定月份生成最优排班计划</p>
          </div>
          <div class="header-right">
            <el-date-picker
              v-model="selectedMonth"
              type="month"
              value-format="YYYY-MM"
              placeholder="选择月份"
              popper-class="month-picker-popper"
              style="margin-right: 12px; width: 140px;"
            />
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
              导出Excel
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
                  <div class="summary-number">{{ scheduleTable.length }}</div>
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
                  <div class="summary-number">{{ monthDays.length }}</div>
                  <div class="summary-label">总天数</div>
                </div>
              </div>
            </el-card>
          </el-col>
          <el-col :xs="24" :sm="8">
            <el-card 
              shadow="hover" 
              :class="['summary-item', violationCount > 0 ? 'summary-item-warning' : 'summary-item-success']"
            >
              <div class="summary-content">
                <div class="summary-icon" :class="violationCount > 0 ? 'bg-danger' : 'bg-success'">
                  <el-icon><Warning /></el-icon>
                </div>
                <div class="summary-text">
                  <div class="summary-number">{{ violationCount }}</div>
                  <div class="summary-label">违规数量</div>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>

        <el-alert
          v-if="violationCount > 0"
          :title="`发现 ${violationCount} 条违规，请查看违规明细`"
          type="warning"
          :closable="false"
          show-icon
          class="warning-alert"
        />

        <div class="table-container">
          <el-table
            :data="scheduleTable"
            border
            style="width: 100%"
            :max-height="600"
            :header-cell-style="{background: '#f5f7fa', fontWeight: 'bold'}"
            :row-style="{height: '50px'}"
            sticky
          >
            <el-table-column prop="personName" label="姓名" width="120" fixed="left" 
                             header-align="center" align="center" />
            <el-table-column prop="group" label="组别" width="100" fixed="left" 
                             header-align="center" align="center" />
            <el-table-column
              v-for="day in monthDays"
              :key="day.date"
              :label="day.labelShort"
              :width="day.date === todayDate ? '100' : '80'"
              align="center"
            >
              <template #default="{ row }">
                <div
                  :class="[
                    'schedule-cell',
                    row[day.date]?.status === '休息' ? 'rest-day-cell' : 'work-day-cell',
                    row[day.date]?.isViolation ? 'violation-cell' : '',
                    day.date === todayDate ? 'today-cell' : ''
                  ]"
                >
                  <div v-if="row[day.date]">
                    <div v-if="row[day.date].status === '上班'" class="shift-info">
                      <span :class="['shift-badge', row[day.date].shift === 'A' ? 'shift-a' : 'shift-b']">
                        {{ row[day.date].shift }}班
                      </span>
                    </div>
                    <div v-else class="status-info">
                      {{ row[day.date].status }}
                    </div>
                    <div v-if="row[day.date].isViolation" class="violation-mark">⚠</div>
                  </div>
                </div>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { Refresh, Download, Warning, User, Clock } from '@element-plus/icons-vue'
import dayjs from 'dayjs'
import { api, type ScheduleItem } from '../utils/api'
import { ElMessage } from 'element-plus'
import * as XLSX from 'xlsx'

const selectedMonth = ref(dayjs().format('YYYY-MM'))
const todayDate = dayjs().format('YYYY-MM-DD')
const loading = ref(false)

// 存储后端返回的原始排班数据
const scheduleData = ref<ScheduleItem[]>([])
const violations = ref<any[]>([])

const hasResults = computed(() => scheduleData.value.length > 0)
const violationCount = computed(() => violations.value.length)

const monthDays = computed(() => {
  const start = dayjs(selectedMonth.value + '-01')
  const end = start.endOf('month')
  const days: { date: string; label: string; labelShort: string }[] = []
  let current = start
  while (current.isBefore(end) || current.isSame(end, 'day')) {
    const dateStr = current.format('YYYY-MM-DD')
    const month = current.month() + 1
    const day = current.date()
    const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
    const weekDay = weekdays[current.day()] || '未知'
    const shortDay = current.date()
    days.push({
      date: dateStr,
      label: `${month}月${day}日 ${weekDay}`,
      labelShort: `${shortDay}\n${weekDay.substring(0,1)}`
    })
    current = current.add(1, 'day')
  }
  return days
})

const scheduleTable = computed(() => {
  const table: Record<string, any>[] = []
  const personMap = new Map<string, any>()

  // 获取所有参与排班的人员（从数据中提取）
  const personSet = new Set<string>()
  scheduleData.value.forEach(item => {
    personSet.add(item.person_name)
  })

  // 初始化每个人的行
  Array.from(personSet).sort().forEach(personName => {
    const firstRecord = scheduleData.value.find(item => item.person_name === personName)
    if (firstRecord) {
      const row: Record<string, any> = {
        personName: personName,
        group: firstRecord.group
      }
      monthDays.value.forEach(day => {
        row[day.date] = null
      })
      personMap.set(personName, row)
      table.push(row)
    }
  })

  // 填充排班数据
  scheduleData.value.forEach(item => {
    const row = personMap.get(item.person_name)
    if (row) {
      row[item.date] = {
        status: item.status,
        shift: item.shift,
        isViolation: item.is_violation,
        violationReason: item.violationReason
      }
    }
  })

  return table
})

const handleGenerate = async () => {
  if (!selectedMonth.value) {
    ElMessage.warning('请选择月份')
    return
  }

  try {
    loading.value = true
    const result = await api.generateSchedule(selectedMonth.value)
    if (result) {
      scheduleData.value = result.schedule
      violations.value = result.violations
      
      if (result.violations.length > 0) {
        ElMessage.warning(`排班已生成，但发现 ${result.violations.length} 条违规`)
      } else {
        ElMessage.success('排班生成成功')
      }
    }
  } catch (error) {
    console.error('生成排班失败:', error)
    ElMessage.error('生成排班失败')
  } finally {
    loading.value = false
  }
}

const handleExport = () => {
  if (!hasResults.value) {
    ElMessage.warning('没有可导出的数据')
    return
  }

  // 准备导出数据
  const exportData: any[] = []
  scheduleData.value.forEach(item => {
    const dateObj = dayjs(item.date)
    const month = dateObj.month() + 1
    const day = dateObj.date()
    const weekDay = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'][dateObj.day()]
    exportData.push({
      日期: `${month}月${day}日`,
      星期: weekDay,
      姓名: item.person_name,
      组别: item.group,
      班次: item.shift || '',
      状态: item.status,
      是否违规: item.is_violation ? '是' : '否',
      违规原因: item.violationReason || ''
    })
  })

  // 创建工作簿
  const ws = XLSX.utils.json_to_sheet(exportData)
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, '排班表')

  // 导出文件
  const monthObj = dayjs(selectedMonth.value + '-01')
  const fileName = `排班表_${monthObj.year()}年${monthObj.month() + 1}月.xlsx`
  XLSX.writeFile(wb, fileName)
  ElMessage.success('导出成功')
}

// 监听月份变化，自动排班
watch(selectedMonth, (newVal) => {
  if(newVal) {
    handleGenerate()
  }
}, { immediate: true }) // 立即执行一次，页面加载时自动生成当前月份的排班
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

.summary-item-warning {
  border: 1px solid #e6a23c;
}

.summary-item-success {
  border: 1px solid #67c23a;
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

.warning-alert {
  margin-bottom: 16px;
  border-radius: 8px;
}

.table-container {
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #ebeef5;
}

.schedule-cell {
  min-height: 60px;
  padding: 4px;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.today-cell {
  background-color: #fff9e6 !important;
  border: 1px solid #ffd700 !important;
}

.shift-info {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.shift-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.status-info {
  color: #909399;
  font-size: 12px;
}

.violation-mark {
  position: absolute;
  top: 2px;
  right: 2px;
  color: #f56c6c;
  font-size: 14px;
}

.violation-cell {
  background-color: #fef0f0 !important;
}

.rest-day-cell {
  background-color: #f0f9ff;
}

.work-day-cell {
  background-color: #ffffff;
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
    overflow-x: auto;
  }
}
</style>