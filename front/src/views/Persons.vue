 <template>
  <div class="page-container">
    <el-card class="main-card">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <h3 class="card-title">人员管理</h3>
            <p class="card-subtitle">管理参与排班的人员信息</p>
          </div>
          <el-button type="primary" @click="handleAdd" :icon="Plus" size="default" :loading="loading">
            新增人员
          </el-button>
        </div>
      </template>
      
      <el-table 
        :data="persons" 
        border 
        style="width: 100%" 
        stripe
        :header-cell-style="{background: '#f5f7fa', fontWeight: 'bold'}"
        v-loading="loading"
      >
        <el-table-column prop="name" label="姓名" width="120" />
        <el-table-column prop="group" label="所属组" width="120" />
        <el-table-column prop="shiftType" label="班次类型" width="150">
          <template #default="{ row }">
            <el-tag v-if="getShiftTypeName(row.shiftType)" :type="getShiftTypeTagType(getShiftTypeName(row.shiftType))" disable-transitions>
              {{ getShiftTypeName(row.shiftType) }}
            </el-tag>
            <span v-else>未指定</span>
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

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px" :destroy-on-close="true">
      <el-form :model="form" label-width="120px" style="padding-right: 20px;">
        <el-form-item label="姓名" required>
          <el-input v-model="form.name" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item label="所属组" required>
          <el-select v-model="form.group" placeholder="请选择所属组" filterable style="width: 100%;">
            <el-option
              v-for="group in availableGroups"
              :key="group.id"
              :label="group.name"
              :value="group.name"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="班次类型">
          <el-select v-model="form.shiftType" placeholder="请选择班次类型" filterable style="width: 100%;">
            <el-option
              v-for="shift in availableShifts"
              :key="shift.id"
              :label="shift.name"
              :value="shift.id.toString()"
            />
          </el-select>
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
import type { ShiftDefinition, Person, GroupConfig } from '../utils/api'
import { ElMessage, ElMessageBox } from 'element-plus'

const dialogVisible = ref(false)
const editingIndex = ref<number | null>(null)
const loading = ref(false)

const persons = ref<Person[]>([])
const groups = ref<GroupConfig[]>([])
const shifts = ref<ShiftDefinition[]>([])

const form = ref<{ name: string; group: string; shiftType: number | null }>({
  name: '',
  group: '',
  shiftType: null
})

const availableGroups = computed(() => {
  return groups.value
})

const availableShifts = computed(() => {
  return shifts.value.filter(shift => shift.enabled)
})

const dialogTitle = computed(() => editingIndex.value !== null ? '编辑人员' : '新增人员')

// 初始化时加载数据
onMounted(async () => {
  await loadPersons()
  await loadGroups()
  await loadShifts()
})

const loadPersons = async () => {
  try {
    loading.value = true
    const data = await api.getPersons()
    if (data) {
      // 将API返回的Person数据直接使用
      persons.value = data
    }
  } catch (error) {
    console.error('加载人员信息失败:', error)
    ElMessage.error('加载人员信息失败')
  } finally {
    loading.value = false
  }
}

const loadGroups = async () => {
  try {
    const data = await api.getGroupConfigs()
    if (data) {
      groups.value = data
    }
  } catch (error) {
    console.error('加载组配置失败:', error)
    ElMessage.error('加载组配置失败')
  }
}

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

const getShiftTypeTagType = (shiftType: any) => {
  // 如果传入的是对象，需要获取其name属性
  const shiftTypeName = typeof shiftType === 'object' && shiftType !== null ? shiftType.name : shiftType;
  
  switch (shiftTypeName) {
    case 'A':
      return 'primary'
    case 'B':
      return 'success'
    default:
      return 'info'
  }
}

// 辅助函数：获取班次类型名称
const getShiftTypeName = (shiftType: any) => {
  if (!shiftType) {
    return null;
  }
  
  // 如果shiftType是数字ID，查找对应的班次对象
  if (typeof shiftType === 'number') {
    const shiftObj = shifts.value.find(shift => shift.id === shiftType);
    return shiftObj ? shiftObj.name : null;
  }
  
  // 如果shiftType是对象，直接返回其name属性
  if (typeof shiftType === 'object' && shiftType !== null) {
    return shiftType.name || shiftType.name;
  }
  
  // 如果shiftType是字符串，直接返回
  if (typeof shiftType === 'string') {
    return shiftType;
  }
  
  return null;
}

const handleAdd = () => {
  editingIndex.value = null
  form.value = {
    name: '',
    group: '',
    shiftType: null
  }
  dialogVisible.value = true
}

const handleEdit = (row: Person, index: number) => {
  editingIndex.value = index
  // 根据row.shiftType的数据类型进行相应处理
  let shiftTypeId = null
  if (typeof row.shiftType === 'number') {
    // 如果shiftType是数字ID
    shiftTypeId = row.shiftType
  } else if (row.shiftType && typeof row.shiftType === 'object') {
    // 如果shiftType是对象，获取其ID
    shiftTypeId = row.shiftType.id
  } else if (row.shiftType === null || row.shiftType === undefined) {
    // 如果shiftType为空
    shiftTypeId = null
  }
  
  form.value = { 
    name: row.name,
    group: row.group,
    shiftType: shiftTypeId
  }
  dialogVisible.value = true
}

const handleDelete = async (index: number) => {
  try {
    const person = persons.value[index]
    
    if (!person) {
      ElMessage.error('无法找到要删除的人员')
      return
    }
    
    await ElMessageBox.confirm(`确定要删除人员"${person.name}"吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    if (person.id) {
      loading.value = true
      await api.deletePerson(person.id)
      persons.value.splice(index, 1)
      ElMessage.success('删除成功')
    } else {
      ElMessage.error('无效的人员ID')
    }
  } catch (error) {
    if (error instanceof Error && error.message.includes('cancel')) {
      // 用户取消
    } else {
      console.error('删除人员失败:', error)
      ElMessage.error('删除人员失败')
    }
  } finally {
    loading.value = false
  }
}

const handleSubmit = async () => {
  if (!form.value.name || !form.value.group) {
    ElMessage.warning('请填写完整信息')
    return
  }

  try {
    loading.value = true
    
    if (editingIndex.value !== null) {
      // 编辑现有人员
      const person = persons.value[editingIndex.value]
      if (!person || !person.id) {
        ElMessage.error('无效的人员ID')
        return
      }
      
      // 构造符合API要求的PersonUpdate对象，需要将shiftType的ID转换为ShiftDefinition对象
      const updateData = {
        id: person.id,
        name: form.value.name!,
        group: form.value.group!,
        shiftType: form.value.shiftType ? shifts.value.find(shift => shift.id === Number(form.value.shiftType)) : undefined
      }
      
      const updatedPerson = await api.updatePerson(Number(person.id), updateData)
      
      if (updatedPerson) {
        // 更新UI中的数据
        persons.value[editingIndex.value] = updatedPerson
      }
      ElMessage.success('人员信息已更新')
    } else {
      // 创建新人员
      const createData: Omit<Person, 'id'> = {
        name: form.value.name!,
        group: form.value.group!,
        shiftType: form.value.shiftType ? shifts.value.find(shift => shift.id === Number(form.value.shiftType)) : undefined
      }
      
      const newPerson = await api.createPerson(createData)
      
      if (newPerson) {
        persons.value.push(newPerson)
      }
      ElMessage.success('人员已创建')
    }
    
    dialogVisible.value = false
  } catch (error) {
    console.error('保存人员信息失败:', error)
    ElMessage.error('保存人员信息失败')
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
</style>