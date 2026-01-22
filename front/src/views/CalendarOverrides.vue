<template>
  <div class="page-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>休假/节假日管理</span>
          <el-button type="primary" @click="handleAdd" :icon="Plus">新增休假</el-button>
        </div>
      </template>
      <el-table :data="overrides" border style="width: 100%" v-loading="loading">
        <el-table-column prop="date" label="开始日期" width="120">
          <template #default="{ row }">
            {{ formatDate(row.date) }}
          </template>
        </el-table-column>
        <el-table-column prop="endDate" label="结束日期" width="120">
          <template #default="{ row }">
            {{ row.endDate ? formatDate(row.endDate) : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="priority" label="优先级" width="90">
          <template #default="{ row }">
            {{ row.priority ?? 0 }}
          </template>
        </el-table-column>
        <el-table-column prop="overrideType" label="覆盖类型" width="120">
          <template #default="{ row }">
            <el-tag :type="row.overrideType === '上班' ? 'success' : 'info'">
              {{ row.overrideType }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="scope" label="作用范围" width="120" />
        <el-table-column prop="target" label="目标" width="120" />
        <el-table-column prop="reason" label="原因" />
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
        <el-form-item label="开始日期" required>
          <el-date-picker
            v-model="form.date"
            type="date"
            value-format="YYYY-MM-DD"
            placeholder="选择日期"
          />
        </el-form-item>
        <el-form-item label="结束日期">
          <el-date-picker
            v-model="form.endDate"
            type="date"
            value-format="YYYY-MM-DD"
            placeholder="选择日期（可选）"
          />
        </el-form-item>
        <el-form-item label="优先级">
          <el-input-number v-model="form.priority" :min="0" :max="99" />
        </el-form-item>
        <el-form-item label="覆盖类型" required>
          <el-select v-model="form.overrideType">
            <el-option label="上班" value="上班" />
            <el-option label="休息" value="休息" />
          </el-select>
        </el-form-item>
        <el-form-item label="作用范围" required>
          <el-select v-model="form.scope" @change="handleScopeChange">
            <el-option label="全员" value="全员" />
            <el-option label="指定组" value="指定组" />
            <el-option label="指定人员" value="指定人员" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="form.scope === '指定组'" label="目标组" required>
          <el-select v-model="form.target" filterable>
            <el-option
              v-for="group in availableGroups"
              :key="group"
              :label="group"
              :value="group"
            />
          </el-select>
        </el-form-item>
        <el-form-item v-if="form.scope === '指定人员'" label="目标人员" required>
          <el-select v-model="form.target" filterable>
            <el-option
              v-for="person in availablePersons"
              :key="person.name"
              :label="person.name"
              :value="person.name"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="原因" required>
          <el-input v-model="form.reason" />
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
import { api, type CalendarOverride, type Person } from '../utils/api'
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
const overrides = ref<CalendarOverride[]>([])
const persons = ref<Person[]>([])
const groups = ref<string[]>([])

const form = ref<Partial<CalendarOverride>>({
  date: '',
  endDate: '',
  overrideType: '上班',
  scope: '全员',
  target: '',
  reason: '',
  priority: 0
})

const availableGroups = computed(() => groups.value)
const availablePersons = computed(() => persons.value)

const dialogTitle = computed(() => editingIndex.value !== null ? '编辑休假' : '新增休假')

onMounted(async () => {
  await loadCalendarOverrides()
  await loadPersons()
  await loadGroups()
})

const loadCalendarOverrides = async () => {
  try {
    loading.value = true
    const data = await api.getCalendarOverrides()
    if (data) {
      overrides.value = data
    }
  } catch (error) {
    console.error('加载日历覆盖失败:', error)
    ElMessage.error('加载日历覆盖失败')
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

const loadGroups = async () => {
  try {
    const data = await api.getGroupConfigs()
    if (data) {
      groups.value = data.map(g => g.name)
    }
  } catch (error) {
    console.error('加载组配置失败:', error)
  }
}

const handleScopeChange = () => {
  form.value.target = ''
}

const handleAdd = () => {
  editingIndex.value = null
  form.value = {
    date: '',
    endDate: '',
    overrideType: '上班',
    scope: '全员',
    target: '',
    reason: '',
    priority: 0
  }
  dialogVisible.value = true
}

const handleEdit = (row: CalendarOverride, index: number) => {
  editingIndex.value = index
  form.value = { ...row }
  dialogVisible.value = true
}

const handleDelete = async (index: number) => {
  try {
    const override = overrides.value[index]
    if (!override || !override.id) {
      ElMessage.error('无效的休假记录或缺少ID')
      return
    }

    await ElMessageBox.confirm('确定要删除这条休假记录吗？', '提示', {
      type: 'warning'
    })

    loading.value = true
    await api.deleteCalendarOverride(override.id)
    await loadCalendarOverrides()
    ElMessage.success('删除成功')
  } catch (error) {
    if (error instanceof Error && error.message.includes('cancel')) {
      // 用户取消
    } else {
      console.error('删除休假记录失败:', error)
      ElMessage.error('删除休假记录失败')
    }
  } finally {
    loading.value = false
  }
}

const handleSubmit = async () => {
  if (!form.value.date) {
    ElMessage.warning('请填写完整信息')
    return
  }
  if ((form.value.scope === '指定组' || form.value.scope === '指定人员') && !form.value.target) {
    ElMessage.warning('请选择目标')
    return
  }

  try {
    loading.value = true

    if (editingIndex.value !== null) {
      const override = overrides.value[editingIndex.value]
      if (!override || !override.id) {
        ElMessage.error('无效的休假记录或ID')
        return
      }

      const updatedOverride = await api.updateCalendarOverride(override.id, {
        ...override,
        ...form.value,
        id: override.id
      } as CalendarOverride)

      if (updatedOverride) {
        await loadCalendarOverrides()
        ElMessage.success('休假记录已更新')
      }
    } else {
      const newOverride = await api.createCalendarOverride({
        date: form.value.date!,
        endDate: form.value.endDate || undefined,
        overrideType: form.value.overrideType!,
        scope: form.value.scope!,
        target: form.value.target || undefined,
        reason: form.value.reason || '',
        priority: form.value.priority ?? 0
      })

      if (newOverride) {
        overrides.value.push(newOverride)
        ElMessage.success('休假记录已创建')
      }
    }

    dialogVisible.value = false
  } catch (error) {
    console.error('保存休假记录失败:', error)
    ElMessage.error('保存休假记录失败')
  } finally {
    loading.value = false
  }
}
</script>
