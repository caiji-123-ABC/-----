<template>
  <div class="page-container">
    <el-card class="main-card">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <h3 class="card-title">轮换组合</h3>
            <p class="card-subtitle">配置两班次的月轮换组合</p>
          </div>
          <el-button type="primary" @click="handleAdd" :icon="Plus" :loading="loading">
            新增组合
          </el-button>
        </div>
      </template>

      <el-table
        :data="rotationGroups"
        border
        stripe
        style="width: 100%"
        :header-cell-style="{background: '#f5f7fa', fontWeight: 'bold'}"
        v-loading="loading"
      >
        <el-table-column prop="name" label="组合名称" />
        <el-table-column label="奇数月班次">
          <template #default="{ row }">
            <span>{{ row.oddShiftName || getShiftName(row.odd_shift) || '未知' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="偶数月班次">
          <template #default="{ row }">
            <span>{{ row.evenShiftName || getShiftName(row.even_shift) || '未知' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" />
        <el-table-column label="操作" width="160">
          <template #default="{ row, $index }">
            <el-button link type="primary" @click="handleEdit(row, $index)">编辑</el-button>
            <el-button link type="danger" @click="handleDelete(row, $index)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="560px" :destroy-on-close="true">
      <el-form :model="form" label-width="120px" class="rotation-form">
        <el-form-item label="组合名称" required>
          <el-input v-model="form.name" placeholder="请输入组合名称" />
        </el-form-item>
        <el-form-item label="奇数月班次" required>
          <el-select v-model="form.oddShift" placeholder="请选择奇数月班次" filterable>
            <el-option
              v-for="shift in availableShifts"
              :key="shift.id"
              :label="shift.name"
              :value="shift.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="偶数月班次" required>
          <el-select v-model="form.evenShift" placeholder="请选择偶数月班次" filterable>
            <el-option
              v-for="shift in availableShifts"
              :key="shift.id"
              :label="shift.name"
              :value="shift.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" :rows="3" placeholder="可选" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit" :loading="loading">确定</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { api } from '../utils/api'
import type { ShiftDefinition, ShiftRotationGroup } from '../utils/api'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const dialogVisible = ref(false)
const editingIndex = ref<number | null>(null)

const rotationGroups = ref<ShiftRotationGroup[]>([])
const shifts = ref<ShiftDefinition[]>([])

const form = ref<{ name: string; oddShift: number | null; evenShift: number | null; remark?: string }>({
  name: '',
  oddShift: null,
  evenShift: null,
  remark: ''
})

const availableShifts = computed(() => shifts.value.filter(shift => shift.enabled))
const dialogTitle = computed(() => editingIndex.value !== null ? '编辑组合' : '新增组合')

onMounted(async () => {
  await loadShifts()
  await loadGroups()
})

const loadShifts = async () => {
  try {
    const data = await api.getShiftDefinitions()
    if (data) {
      shifts.value = data
    }
  } catch (error) {
    console.error('加载班次定义失败:', error)
    ElMessage.error('加载班次定义失败')
  }
}

const loadGroups = async () => {
  try {
    loading.value = true
    const data = await api.getShiftRotationGroups()
    rotationGroups.value = data
  } catch (error) {
    console.error('加载轮换组合失败:', error)
    ElMessage.error('加载轮换组合失败')
  } finally {
    loading.value = false
  }
}

const getShiftName = (shiftId: number) => {
  const shift = shifts.value.find(item => item.id === shiftId)
  return shift?.name || ''
}

const handleAdd = () => {
  editingIndex.value = null
  form.value = {
    name: '',
    oddShift: null,
    evenShift: null,
    remark: ''
  }
  dialogVisible.value = true
}

const handleEdit = (row: ShiftRotationGroup, index: number) => {
  editingIndex.value = index
  form.value = {
    name: row.name,
    oddShift: row.odd_shift,
    evenShift: row.even_shift,
    remark: row.remark || ''
  }
  dialogVisible.value = true
}

const handleDelete = async (row: ShiftRotationGroup, index: number) => {
  try {
    await ElMessageBox.confirm(`确定要删除组合"${row.name}"吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    loading.value = true
    await api.deleteShiftRotationGroup(row.id)
    rotationGroups.value.splice(index, 1)
    ElMessage.success('删除成功')
  } catch (error) {
    if (error instanceof Error && error.message.includes('cancel')) {
      // 用户取消
    } else {
      console.error('删除组合失败:', error)
      ElMessage.error('删除组合失败')
    }
  } finally {
    loading.value = false
  }
}

const handleSubmit = async () => {
  if (!form.value.name || !form.value.oddShift || !form.value.evenShift) {
    ElMessage.warning('请填写完整信息')
    return
  }
  if (form.value.oddShift === form.value.evenShift) {
    ElMessage.warning('奇数月班次和偶数月班次不能相同')
    return
  }

  try {
    loading.value = true
    if (editingIndex.value !== null) {
      const group = rotationGroups.value[editingIndex.value]
      if (!group) {
        ElMessage.error('无效的组合记录')
        return
      }
      const updated = await api.updateShiftRotationGroup(group.id, {
        ...group,
        name: form.value.name,
        odd_shift: form.value.oddShift,
        even_shift: form.value.evenShift,
        remark: form.value.remark || ''
      })
      if (updated) {
        rotationGroups.value[editingIndex.value] = updated
      }
      ElMessage.success('组合已更新')
    } else {
      const created = await api.createShiftRotationGroup({
        name: form.value.name,
        odd_shift: form.value.oddShift,
        even_shift: form.value.evenShift,
        remark: form.value.remark || ''
      })
      if (created) {
        rotationGroups.value.push(created)
      }
      ElMessage.success('组合已创建')
    }
    dialogVisible.value = false
  } catch (error) {
    console.error('保存组合失败:', error)
    ElMessage.error('保存组合失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.main-card {
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

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.rotation-form {
  max-width: 420px;
  margin: 0 auto;
  padding: 0 20px 10px;
}

.rotation-form .el-input,
.rotation-form .el-select {
  width: 100%;
}
</style>
