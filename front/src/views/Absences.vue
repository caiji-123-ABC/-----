<template>
  <div class="page-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>请假管理</span>
          <el-button type="primary" @click="handleAdd" :icon="Plus" :loading="loading">新增请假</el-button>
        </div>
      </template>
      <el-table :data="absences" border style="width: 100%" v-loading="loading">
        <el-table-column prop="person" label="人员ID" width="80" />
        <el-table-column prop="startDate" label="开始日期" width="120">
          <template #default="{ row }">
            {{ formatDate(row.startDate) }}
          </template>
        </el-table-column>
        <el-table-column prop="endDate" label="结束日期" width="120">
          <template #default="{ row }">
            {{ formatDate(row.endDate) }}
          </template>
        </el-table-column>
        <el-table-column prop="type" label="类型" width="100">
          <template #default="{ row }">
            {{ row.type }}
          </template>
        </el-table-column>
        <el-table-column prop="reason" label="原因" width="120" />
        <el-table-column prop="countAsRest" label="是否算休息" width="100">
          <template #default="{ row }">
            <el-tag :type="row.countAsRest ? 'success' : 'info'">
              {{ row.countAsRest ? '是' : '否' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row, $index }">
            <el-button link type="primary" @click="handleEdit(row, $index)">编辑</el-button>
            <el-button link type="danger" @click="handleDelete($index)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px">
      <el-form :model="form" label-width="120px">
        <el-form-item label="人员" required>
          <el-select v-model="form.person" filterable placeholder="选择人员">
            <el-option
              v-for="person in availablePersons"
              :key="person.id"
              :label="person.name"
              :value="person.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="开始日期" required>
          <el-date-picker
            v-model="form.startDate"
            type="date"
            value-format="YYYY-MM-DD"
            placeholder="选择日期"
          />
        </el-form-item>
        <el-form-item label="结束日期" required>
          <el-date-picker
            v-model="form.endDate"
            type="date"
            value-format="YYYY-MM-DD"
            placeholder="选择日期"
          />
        </el-form-item>
        <el-form-item label="类型" required>
          <el-select v-model="form.type" placeholder="选择请假类型">
            <el-option label="请假" value="请假" />
            <el-option label="病假" value="病假" />
            <el-option label="出差" value="出差" />
            <el-option label="培训" value="培训" />
          </el-select>
        </el-form-item>
        <el-form-item label="原因">
          <el-input v-model="form.reason" type="textarea" placeholder="请输入请假原因" />
        </el-form-item>
        <el-form-item label="是否算休息">
          <el-switch v-model="form.countAsRest" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="loading">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { api, type Absence, type Person } from '../utils/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import dayjs from 'dayjs'

const formatDate = (dateStr: string) => {
  if (!dateStr) return ''
  const dateObj = dayjs(dateStr)
  const month = dateObj.month() + 1
  const day = dateObj.date()
  return `${month}月${day}日`
}

const absences = ref<Absence[]>([])
const persons = ref<Person[]>([])
const dialogVisible = ref(false)
const editingIndex = ref<number | null>(null)
const loading = ref(false)

const form = ref<Partial<Absence>>({
  person: undefined,
  startDate: '',
  endDate: '',
  type: '请假',
  reason: '',
  countAsRest: true
})

const availablePersons = computed(() => {
  return persons.value
})

const dialogTitle = computed(() => editingIndex.value !== null ? '编辑请假' : '新增请假')

// 初始化时加载数据
onMounted(async () => {
  await loadAbsences()
  await loadPersons()
})

const loadAbsences = async () => {
  try {
    loading.value = true
    const data = await api.getAbsences()
    if (data) {
      absences.value = data
    }
  } catch (error) {
    console.error('加载请假信息失败:', error)
    ElMessage.error('加载请假信息失败')
  } finally {
    loading.value = false
  }
}

const handleAdd = () => {
  editingIndex.value = null
  form.value = {
    person: undefined,
    startDate: '',
    endDate: '',
    type: '请假',
    reason: '',
    countAsRest: true
  }
  dialogVisible.value = true
}

const handleEdit = (row: Absence, index: number) => {
  editingIndex.value = index
  form.value = { ...row }
  dialogVisible.value = true
}

const handleDelete = async (index: number) => {
  try {
    const absence = absences.value[index]
    if (!absence || !absence.id) {
      ElMessage.error('无效的请假记录或缺少ID')
      return
    }
    
    await ElMessageBox.confirm('确定要删除这条请假记录吗？', '提示', {
      type: 'warning'
    })
    
    loading.value = true
    await api.deleteAbsence(absence.id)
    await loadAbsences() // 重新加载数据
    ElMessage.success('删除成功')
  } catch (error) {
    if (error instanceof Error && error.message.includes('cancel')) {
      // 用户取消
    } else {
      console.error('删除请假记录失败:', error)
      ElMessage.error('删除请假记录失败')
    }
  } finally {
    loading.value = false
  }
}

const handleSubmit = async () => {
  if (!form.value.person || !form.value.startDate || !form.value.endDate || !form.value.type) {
    ElMessage.warning('请填写完整信息')
    return
  }

  try {
    loading.value = true
    
    if (editingIndex.value !== null) {
      // 编辑现有请假
      const absence = absences.value[editingIndex.value]
      if (!absence || !absence.id) {
        ElMessage.error('无效的请假记录或ID')
        return
      }
      
      const updatedAbsence = await api.updateAbsence(absence.id, {
        ...absence,
        ...form.value,
        id: absence.id
      } as Absence)
      
      if (updatedAbsence) {
        // 重新加载数据以确保与服务器同步
        await loadAbsences()
        ElMessage.success('请假记录已更新')
      }
    } else {
      // 创建新请假
      const newAbsence = await api.createAbsence({
        person: form.value.person!,
        startDate: form.value.startDate!,
        endDate: form.value.endDate!,
        type: form.value.type!,
        reason: form.value.reason || '',
        countAsRest: form.value.countAsRest || false
      })
      
      if (newAbsence) {
        absences.value.push(newAbsence)
        ElMessage.success('请假记录已创建')
      }
    }
    
    dialogVisible.value = false
  } catch (error) {
    console.error('保存请假记录失败:', error)
    ElMessage.error('保存请假记录失败')
  } finally {
    loading.value = false
  }
}

const loadPersons = async () => {
  try {
    const data = await api.getPersons()
    if (data) {
      persons.value = data
    }
  } catch (error) {
    console.error('加载人员信息失败:', error)
    ElMessage.error('加载人员信息失败')
  }
}
</script>