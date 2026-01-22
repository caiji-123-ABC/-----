<template>
  <div class="page-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>大小周配置</span>
        </div>
      </template>
      
      <!-- 班次选择 -->
      <el-form :model="form" label-width="120px">
        <el-form-item label="选择班次">
          <el-select v-model="selectedShiftTypeId" placeholder="请选择班次，留空则为默认配置" clearable @change="loadScheduleForShift">
            <el-option 
              v-for="shift in shiftTypes" 
              :key="shift.id" 
              :label="shift.name" 
              :value="shift.id"
            />
            <el-option label="默认配置（适用于所有班次）" :value="null" />
          </el-select>
        </el-form-item>
      </el-form>
      
      <el-tabs v-model="activeTab">
        <el-tab-pane label="大周配置" name="bigWeek">
          <h3>大周工作安排</h3>
          <p class="tip">请选择{{ selectedShiftTypeName }}在大周时员工工作的日期</p>
          <div class="week-config">
            <el-checkbox-group v-model="bigWeekSchedule">
              <el-checkbox 
                v-for="(day, index) in daysOfWeek" 
                :key="'big-'+index" 
                :label="index"
              >
                {{ day }}
              </el-checkbox>
            </el-checkbox-group>
          </div>
        </el-tab-pane>
        
        <el-tab-pane label="小周配置" name="smallWeek">
          <h3>小周工作安排</h3>
          <p class="tip">请选择{{ selectedShiftTypeName }}在小周时员工工作的日期</p>
          <div class="week-config">
            <el-checkbox-group v-model="smallWeekSchedule">
              <el-checkbox 
                v-for="(day, index) in daysOfWeek" 
                :key="'small-'+index" 
                :label="index"
              >
                {{ day }}
              </el-checkbox>
            </el-checkbox-group>
          </div>
        </el-tab-pane>
      </el-tabs>
      
      <div class="save-section">
        <el-button type="primary" @click="saveSchedule" :loading="saving">保存设置</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { api, type WeekScheduleConfig, type ShiftDefinition } from '../utils/api'

const activeTab = ref('bigWeek')
const bigWeekSchedule = ref<number[]>([0, 1, 2, 3, 4, 5]) // 默认周一到周六上班
const smallWeekSchedule = ref<number[]>([0, 1, 2, 3, 4]) // 默认周一到周五上班
const saving = ref(false)
const selectedShiftTypeId = ref<number | null>(null)
const shiftTypes = ref<ShiftDefinition[]>([])
const form = ref({})

// 星期数组
const daysOfWeek = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']

// 根据选中的班次获取显示名称
const selectedShiftTypeName = computed(() => {
  if (selectedShiftTypeId.value === null) {
    return '默认'
  }
  const shift = shiftTypes.value.find(s => s.id === selectedShiftTypeId.value)
  return shift ? shift.name : '未知班次'
})

const saveSchedule = async () => {
  try {
    saving.value = true
    
    // 准备发送给后端的数据
    const schedules: Omit<WeekScheduleConfig, 'id'>[] = [
      {
        weekType: '大周',
        workDays: bigWeekSchedule.value,
        shiftType: selectedShiftTypeId.value || undefined
      },
      {
        weekType: '小周',
        workDays: smallWeekSchedule.value,
        shiftType: selectedShiftTypeId.value || undefined
      }
    ]
    
    // 调用后端API保存配置
    const result = await api.updateWeekSchedules(schedules)
    
    ElMessage.success(result.message || '保存成功')
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

// 从后端加载配置
const loadSchedule = async () => {
  try {
    // 加载班次类型
    const shifts = await api.getShiftDefinitions()
    shiftTypes.value = shifts || []

    // 加载默认配置
    await loadScheduleForShift(null)
  } catch (error) {
    console.error('加载配置失败:', error)
    ElMessage.error('加载配置失败')
  }
}

// 加载特定班次的配置
const loadScheduleForShift = async (shiftId: number | null) => {
  try {
    const configs = await api.getWeekSchedules()
    
    // 查找指定班次的大周和小周配置
    const bigWeekConfig = configs.find(config => 
      config.weekType === '大周' && 
      (config.shiftType === shiftId || (shiftId === null && !config.shiftType))
    )
    const smallWeekConfig = configs.find(config => 
      config.weekType === '小周' && 
      (config.shiftType === shiftId || (shiftId === null && !config.shiftType))
    )
    
    if (bigWeekConfig) {
      bigWeekSchedule.value = bigWeekConfig.workDays
    } else {
      // 如果没有找到特定班次的配置，使用默认值
      bigWeekSchedule.value = [0, 1, 2, 3, 4, 5]
    }
    
    if (smallWeekConfig) {
      smallWeekSchedule.value = smallWeekConfig.workDays
    } else {
      // 如果没有找到特定班次的配置，使用默认值
      smallWeekSchedule.value = [0, 1, 2, 3, 4]
    }
  } catch (error) {
    console.error('加载配置失败:', error)
    ElMessage.error('加载配置失败')
  }
}

// 监听班次选择变化
watch(selectedShiftTypeId, () => {
  loadScheduleForShift(selectedShiftTypeId.value)
})

// 页面加载时读取配置
onMounted(() => {
  loadSchedule()
})
</script>

<style scoped>
.week-config {
  margin: 20px 0;
  padding: 20px;
  border: 1px solid #eee;
  border-radius: 4px;
}

.week-config .el-checkbox {
  display: block;
  margin-bottom: 10px;
}

.save-section {
  margin-top: 20px;
  text-align: center;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.tip {
  color: #666;
  font-size: 14px;
  margin-top: 10px;
}

.el-select {
  width: 100%;
}
</style>