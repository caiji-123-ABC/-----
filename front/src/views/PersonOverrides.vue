<template>
  <div class="page-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>人员锁定规则</span>
          <el-button type="primary" @click="handleAdd" :icon="Plus">新增锁定</el-button>
        </div>
      </template>
      <el-alert
        title="优先级最高，慎用"
        type="warning"
        :closable="false"
        style="margin-bottom: 16px"
      />
      <el-table :data="overrides" border style="width: 100%" v-loading="loading">
        <el-table-column prop="person" label="人员" width="120">
          <template #default="{ row }">
            {{ persons.find(p => p.id === row.person)?.name || '未知' }}
          </template>
        </el-table-column>
        <el-table-column prop="date" label="日期" width="120">
          <template #default="{ row }">
            {{ formatDate(row.date) }}
          </template>
        </el-table-column>
        <el-table-column prop="type" label="锁定类型" width="120">
          <template #default="{ row }">
            <el-tag :type="row.type === '必须上班' ? 'success' : 'info'">
              {{ row.type }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="reason" label="原因" />
        <el-table-column prop="remark" label="备注" />
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
        <el-form-item label="姓名" required>
          <el-select v-model="form.person" filterable placeholder="选择人员">
            <el-option
              v-for="person in availablePersons"
              :key="person.id"
              :label="person.name"
              :value="person.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="日期" required>
          <el-date-picker
            v-model="form.date"
            type="date"
            value-format="YYYY-MM-DD"
            placeholder="选择日期"
          />
        </el-form-item>
        <el-form-item label="锁定类型" required>
          <el-select v-model="form.type">
            <el-option label="必须上班" value="必须上班" />
            <el-option label="必须休息" value="必须休息" />
          </el-select>
        </el-form-item>
        <el-form-item label="原因" required>
          <el-input v-model="form.reason" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" />
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
import { api, type PersonOverride, type Person } from '../utils/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import dayjs from 'dayjs'

const formatDate = (dateStr: string) => {
  if (!dateStr) return ''
  const dateObj = dayjs(dateStr)
  const month = dateObj.month() + 1
  const day = dateObj.date()
  return `${month}月${day}日`
}

const dialogVisible = ref(false)
const editingIndex = ref<number | null>(null)
const loading = ref(false)
const overrides = ref<PersonOverride[]>([])
const persons = ref<Person[]>([])

const form = ref<Partial<PersonOverride>>({
  person: undefined,
  date: '',
  type: '必须上班',
  reason: '',
  remark: ''
})

const availablePersons = computed(() => {
  return persons.value
})

const dialogTitle = computed(() => editingIndex.value !== null ? '编辑锁定' : '新增锁定')

// 初始化时加载数据
onMounted(async () => {
  await loadPersonOverrides()
  await loadPersons()
})

const loadPersonOverrides = async () => {
  try {
    loading.value = true
    const data = await api.getPersonOverrides()
    if (data) {
      overrides.value = data
    }
  } catch (error) {
    console.error('加载人员锁定规则失败:', error)
    ElMessage.error('加载人员锁定规则失败')
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

const handleAdd = () => {
  editingIndex.value = null
  form.value = {
    person: undefined,
    date: '',
    type: '必须上班',
    reason: '',
    remark: ''
  }
  dialogVisible.value = true
}

const handleEdit = (row: PersonOverride, index: number) => {
  editingIndex.value = index
  form.value = { ...row }
  dialogVisible.value = true
}

const handleDelete = async (index: number) => {
  try {
    const override = overrides.value[index]
    if (!override || !override.id) {
      ElMessage.error('无效的锁定规则或缺少ID')
      return
    }
    
    await ElMessageBox.confirm('确定要删除这条锁定规则吗？', '提示', {
      type: 'warning'
    })
    
    loading.value = true
    await api.deletePersonOverride(override.id)
    await loadPersonOverrides()
    ElMessage.success('删除成功')
  } catch (error) {
    if (error instanceof Error && error.message.includes('cancel')) {
      // 用户取消
    } else {
      console.error('删除锁定规则失败:', error)
      ElMessage.error('删除锁定规则失败')
    }
  } finally {
    loading.value = false
  }
}

const handleSubmit = async () => {
  if (!form.value.person || !form.value.date || !form.value.reason) {
    ElMessage.warning('请填写完整信息')
    return
  }

  try {
    loading.value = true
    
    if (editingIndex.value !== null) {
      // 编辑现有锁定规则
      const override = overrides.value[editingIndex.value]
      if (!override || !override.id) {
        ElMessage.error('无效的锁定规则或ID')
        return
      }
      
      const updatedOverride = await api.updatePersonOverride(override.id, {
        ...override,
        ...form.value,
        id: override.id
      } as PersonOverride)
      
      if (updatedOverride) {
        await loadPersonOverrides()
        ElMessage.success('锁定规则已更新')
      }
    } else {
      // 创建新锁定规则
      const newOverride = await api.createPersonOverride({
        person: form.value.person!,
        date: form.value.date!,
        type: form.value.type!,
        reason: form.value.reason!,
        remark: form.value.remark
      })
      
      if (newOverride) {
        overrides.value.push(newOverride)
        ElMessage.success('锁定规则已创建')
      }
    }
    
    dialogVisible.value = false
  } catch (error) {
    console.error('保存锁定规则失败:', error)
    ElMessage.error('保存锁定规则失败')
  } finally {
    loading.value = false
  }
}
</script>
