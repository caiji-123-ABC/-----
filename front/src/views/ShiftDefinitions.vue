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
        <el-table-column prop="name" label="班次名称" width="120" />
        <el-table-column prop="startTime" label="开始时间" width="120" />
        <el-table-column prop="endTime" label="结束时间" width="120" />
        <el-table-column prop="enabled" label="是否启用" width="100">
          <template #default="{ row }">
            <el-tag :type="row.enabled ? 'success' : 'info'">
              {{ row.enabled ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row, $index }">
            <el-button link type="primary" @click="handleEdit(row, $index)">编辑</el-button>
            <el-button link type="primary" @click="handleEditSchedule(row)">配置大小周</el-button>
            <el-button link type="danger" @click="handleDelete(row, $index)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px">
      <el-form :model="form" label-width="100px">
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
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit">确定</el-button>
        </div>
      </template>
    </el-dialog>
    
    <!-- 大小周配置对话框 -->
    <el-dialog v-model="scheduleDialogVisible" :title="`配置班次「${currentShift?.name}」的大小周`" width="600px">
      <el-tabs v-model="activeTab">
        <el-tab-pane label="大周配置" name="bigWeek">
          <h3>大周工作安排</h3>
          <p class="tip">请选择该班次在大周时员工工作的日期</p>
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
          <p class="tip">请选择该班次在小周时员工工作的日期</p>
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
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="scheduleDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSaveSchedule" :loading="savingSchedule">保存</el-button>
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
const scheduleDialogVisible = ref(false)
const savingSchedule = ref(false)
const currentShift = ref<ShiftDefinition | null>(null)
const activeTab = ref('bigWeek')

const form = ref<Partial<ShiftDefinition>>({
  name: '',
  startTime: '09:00',
  endTime: '19:00',
  enabled: true
})

const shifts = ref<ShiftDefinition[]>([])
const bigWeekSchedule = ref<number[]>([0, 1, 2, 3, 4, 5])
const smallWeekSchedule = ref<number[]>([0, 1, 2, 3, 4])
const daysOfWeek = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']

const dialogTitle = computed(() => editingIndex.value !== null ? '编辑班次' : '新增班次')

// 初始化时加载数据
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

const handleAdd = () => {
  editingIndex.value = null
  form.value = {
    name: '',
    startTime: '09:00',
    endTime: '19:00',
    enabled: true
  }
  dialogVisible.value = true
}

const handleEdit = (row: ShiftDefinition, index: number) => {
  editingIndex.value = index
  form.value = { ...row }
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

const handleSubmit = async () => {
  if (!form.value.name || !form.value.startTime || !form.value.endTime) {
    ElMessage.warning('请填写完整信息')
    return
  }

  try {
    loading.value = true
    
    if (editingIndex.value !== null) {
      // 编辑现有班次
      const shiftDef = shifts.value[editingIndex.value]
      if (!shiftDef || !shiftDef.id) {
        ElMessage.error('无效的班次ID')
        return
      }
      
      const updatedShift = await api.updateShiftDefinition(shiftDef.id, {
        ...shiftDef,
        ...form.value
      })

      if (updatedShift) {
        const targetShift = shifts.value[editingIndex.value];
        if (targetShift) {
          Object.assign(targetShift, updatedShift)
          ElMessage.success('班次已更新')
        } else {
          ElMessage.error('目标班次不存在')
        }
      } else {
        ElMessage.error('更新班次失败')
      }
    } else {
      // 创建新班次
      const newShift = await api.createShiftDefinition({
        name: form.value.name!,
        startTime: form.value.startTime!,
        endTime: form.value.endTime!,
        enabled: form.value.enabled || true,
        remark: form.value.remark
      })
      
      if (newShift) {
        shifts.value.push(newShift)
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

// 处理打开大小周配置对话框
const handleEditSchedule = async (shift: ShiftDefinition) => {
  currentShift.value = shift
  await loadScheduleForShift(shift.id)
  scheduleDialogVisible.value = true
}

// 加载特定班次的大小周配置
const loadScheduleForShift = async (shiftId: number) => {
  try {
    // 获取所有班次信息，其中包含了大小周配置
    const shifts = await api.getShiftDefinitions();
    
    // 查找指定ID的班次
    const shift = shifts.find(s => s.id === shiftId);
    
    if (shift) {
      // 使用班次中的大小周配置
      bigWeekSchedule.value = shift.bigWeek || shift.big_week || [];
      smallWeekSchedule.value = shift.smallWeek || shift.small_week || [];
    } else {
      // 如果没有找到特定班次的配置，使用默认值
      bigWeekSchedule.value = [0, 1, 2, 3, 4, 5];
      smallWeekSchedule.value = [0, 1, 2, 3, 4];
    }
  } catch (error) {
    console.error('加载大小周配置失败:', error);
    ElMessage.error('加载大小周配置失败');
  }
};

// 保存大小周配置
const handleSaveSchedule = async () => {
  if (!currentShift.value?.id) {
    ElMessage.error('当前班次无效，无法保存配置');
    return;
  }
  
  try {
    savingSchedule.value = true
    
    // 构造数据，使用后端期望的字段名
    const scheduleData = [{
      shiftType: currentShift.value.id,  // 使用shiftType字段关联班次
      big_week: bigWeekSchedule.value,
      small_week: smallWeekSchedule.value
    }]
    
    // 调用后端API保存配置
    const result = await api.updateWeekSchedules(scheduleData)
    
    if (result && result.message) {
      ElMessage.success(result.message || '大小周配置已保存')
      scheduleDialogVisible.value = false
    } else {
      ElMessage.error(result?.message || '保存失败，请稍后重试')
    }
  } catch (error) {
    console.error('保存大小周配置失败:', error)
    ElMessage.error('网络错误，保存大小周配置失败')
  } finally {
    savingSchedule.value = false
  }
}
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

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
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

/* 额外的样式 */
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
</style>