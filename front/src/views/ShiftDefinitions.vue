<template>
  <div class="page-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>班次定义</span>
          <el-button type="primary" @click="handleAdd" :icon="Plus">新增班次</el-button>
        </div>
      </template>

      <el-table :data="shifts" border style="width: 100%">
        <el-table-column prop="name" label="班次名称" width="140" />
        <el-table-column prop="startTime" label="开始时间" width="140" />
        <el-table-column prop="endTime" label="结束时间" width="140" />
        <el-table-column prop="enabled" label="是否启用" width="120">
          <template #default="{ row }">
            <el-tag :type="row.enabled ? 'success' : 'info'">
              {{ row.enabled ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" />
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row, $index }">
            <el-button link type="primary" @click="handleEdit(row, $index)">编辑</el-button>
            <el-button link type="danger" @click="handleDelete(row, $index)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="720px">
      <el-form :model="form" label-width="120px">
        <el-form-item label="班次名称" required>
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="开始时间" required>
          <el-time-picker v-model="form.startTime" format="HH:mm" value-format="HH:mm" />
        </el-form-item>
        <el-form-item label="结束时间" required>
          <el-time-picker v-model="form.endTime" format="HH:mm" value-format="HH:mm" />
        </el-form-item>
        <el-form-item label="是否启用">
          <el-switch v-model="form.enabled" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" />
        </el-form-item>

        <el-form-item label="大小周配置">
          <div class="schedule-box">
            <el-tabs v-model="activeTab">
              <el-tab-pane label="大周" name="bigWeek">
                <div class="schedule-hint">请选择该班次在大周时员工工作的日期</div>
                <el-checkbox-group v-model="bigWeekSchedule">
                  <el-checkbox v-for="(day, index) in daysOfWeek" :key="'big-' + index" :label="index">
                    {{ day }}
                  </el-checkbox>
                </el-checkbox-group>
              </el-tab-pane>
              <el-tab-pane label="小周" name="smallWeek">
                <div class="schedule-hint">请选择该班次在小周时员工工作的日期</div>
                <el-checkbox-group v-model="smallWeekSchedule">
                  <el-checkbox v-for="(day, index) in daysOfWeek" :key="'small-' + index" :label="index">
                    {{ day }}
                  </el-checkbox>
                </el-checkbox-group>
              </el-tab-pane>
            </el-tabs>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit" :loading="loading || savingSchedule">确定</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { api } from '../utils/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { ShiftDefinition } from '../utils/api'

const dialogVisible = ref(false)
const editingIndex = ref<number | null>(null)
const loading = ref(false)
const savingSchedule = ref(false)
const activeTab = ref('bigWeek')

const form = ref<Partial<ShiftDefinition>>({
  name: '',
  startTime: '09:00',
  endTime: '19:00',
  enabled: true,
  remark: ''
})

const shifts = ref<ShiftDefinition[]>([])
const bigWeekSchedule = ref<number[]>([0, 1, 2, 3, 4, 5])
const smallWeekSchedule = ref<number[]>([0, 1, 2, 3, 4])
const daysOfWeek = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']

const dialogTitle = computed(() => editingIndex.value !== null ? '编辑班次' : '新增班次')

onMounted(async () => {
  await loadShiftDefinitions()
})

const loadShiftDefinitions = async () => {
  try {
    loading.value = true
    const data = await api.getShiftDefinitions()
    if (data) {
      shifts.value = data
    }
  } catch (error) {
    console.error('加载班次定义失败:', error)
    ElMessage.error('加载班次定义失败')
  } finally {
    loading.value = false
  }
}

const resetScheduleDefaults = () => {
  bigWeekSchedule.value = [0, 1, 2, 3, 4, 5]
  smallWeekSchedule.value = [0, 1, 2, 3, 4]
}

const handleAdd = () => {
  editingIndex.value = null
  form.value = {
    name: '',
    startTime: '09:00',
    endTime: '19:00',
    enabled: true,
    remark: ''
  }
  resetScheduleDefaults()
  activeTab.value = 'bigWeek'
  dialogVisible.value = true
}

const applyScheduleFromShift = (shift: ShiftDefinition | undefined) => {
  if (shift) {
    bigWeekSchedule.value = shift.bigWeek || shift.big_week || []
    smallWeekSchedule.value = shift.smallWeek || shift.small_week || []
  } else {
    resetScheduleDefaults()
  }
}

const handleEdit = (row: ShiftDefinition, index: number) => {
  editingIndex.value = index
  form.value = { ...row }
  applyScheduleFromShift(row)
  activeTab.value = 'bigWeek'
  dialogVisible.value = true
}

const handleDelete = async (row: ShiftDefinition, index: number) => {
  try {
    if (!row.id) {
      ElMessage.error('无效的班次ID')
      return
    }

    await ElMessageBox.confirm(`确定要删除班次"${row.name}"吗？`, '提示', {
      type: 'warning'
    })

    loading.value = true
    await api.deleteShiftDefinition(row.id)
    shifts.value.splice(index, 1)
    ElMessage.success('删除成功')
  } catch (error) {
    if (error instanceof Error && error.message.includes('cancel')) {
      // 用户取消
    } else {
      console.error('删除班次失败:', error)
      ElMessage.error('删除班次失败')
    }
  } finally {
    loading.value = false
  }
}

const saveSchedule = async (shiftId: number) => {
  savingSchedule.value = true
  try {
    const scheduleData = [{
      shiftType: shiftId,
      big_week: bigWeekSchedule.value,
      small_week: smallWeekSchedule.value
    }]
    const result = await api.updateWeekSchedules(scheduleData)
    if (result?.message) {
      ElMessage.success(result.message)
    }
  } catch (error) {
    console.error('保存大小周配置失败:', error)
    ElMessage.error('保存大小周配置失败')
    throw error
  } finally {
    savingSchedule.value = false
  }
}

const handleSubmit = async () => {
  if (!form.value.name || !form.value.startTime || !form.value.endTime) {
    ElMessage.warning('请填写完整信息')
    return
  }

  try {
    loading.value = true

    if (editingIndex.value !== null) {
      const shiftDef = shifts.value[editingIndex.value]
      if (!shiftDef?.id) {
        ElMessage.error('无效的班次ID')
        return
      }

      const updatedShift = await api.updateShiftDefinition(shiftDef.id, {
        ...shiftDef,
        ...form.value
      })

      if (updatedShift) {
        const targetShift = shifts.value[editingIndex.value]
        if (!targetShift) {
          ElMessage.error('目标班次不存在')
          return
        }
        Object.assign(targetShift, updatedShift)
        await saveSchedule(shiftDef.id)
        Object.assign(targetShift, {
          bigWeek: [...bigWeekSchedule.value],
          smallWeek: [...smallWeekSchedule.value],
          big_week: [...bigWeekSchedule.value],
          small_week: [...smallWeekSchedule.value],
        })
        await loadShiftDefinitions()
        ElMessage.success('班次已更新')
      } else {
        ElMessage.error('更新班次失败')
      }
    } else {
      const newShift = await api.createShiftDefinition({
        name: form.value.name!,
        startTime: form.value.startTime!,
        endTime: form.value.endTime!,
        enabled: form.value.enabled ?? true,
        remark: form.value.remark
      })

      if (newShift?.id) {
        shifts.value.push(newShift)
        await saveSchedule(newShift.id)
        const targetShift = shifts.value[shifts.value.length - 1]
        if (targetShift) {
          Object.assign(targetShift, {
          bigWeek: [...bigWeekSchedule.value],
          smallWeek: [...smallWeekSchedule.value],
          big_week: [...bigWeekSchedule.value],
          small_week: [...smallWeekSchedule.value],
        })
        }
        await loadShiftDefinitions()
        ElMessage.success('班次已创建')
      } else {
        ElMessage.error('创建班次失败')
      }
    }

    dialogVisible.value = false
  } catch (error) {
    console.error('保存班次失败:', error)
    ElMessage.error('保存班次失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.schedule-box {
  width: 100%;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  padding: 12px;
}

.schedule-hint {
  color: #909399;
  margin-bottom: 8px;
}

.el-checkbox {
  display: block;
  margin-bottom: 6px;
}
</style>
