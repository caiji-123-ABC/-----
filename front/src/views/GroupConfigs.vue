<template>
  <div class="page-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>组配置</span>
          <el-button type="primary" @click="handleAdd" :icon="Plus">新增组</el-button>
        </div>
      </template>
      <el-table :data="groups" border style="width: 100%">
        <el-table-column prop="name" label="组名称" width="120" />
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
      <el-form :model="form" label-width="100px">
        <el-form-item label="组名称" required>
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { api } from '../utils/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { GroupConfig } from '../utils/api'

const dialogVisible = ref(false)
const editingIndex = ref<number | null>(null)
const loading = ref(false)

const form = ref<Partial<GroupConfig>>({
  name: '',
  remark: ''
})

const groups = ref<GroupConfig[]>([])

const dialogTitle = computed(() => editingIndex.value !== null ? '编辑组' : '新增组')

// 初始化时加载数据
onMounted(async () => {
  await loadGroupConfigs()
})

const loadGroupConfigs = async () => {
  try {
    loading.value = true
    const data = await api.getGroupConfigs()
    if (data) {
      groups.value = data
    }
  } catch (error) {
    console.error('加载组配置失败:', error)
    ElMessage.error('加载组配置失败')
  } finally {
    loading.value = false
  }
}

const handleAdd = () => {
  editingIndex.value = null
  form.value = {
    name: '',
    remark: ''
  }
  dialogVisible.value = true
}

const handleEdit = (row: GroupConfig, index: number) => {
  editingIndex.value = index
  form.value = { ...row }
  dialogVisible.value = true
}

const handleDelete = async (index: number) => {
  try {
    const group = groups.value[index]
    
    // 检查 group 是否存在
    if (!group) {
      ElMessage.error('要删除的组不存在')
      return
    }
    
    await ElMessageBox.confirm(`确定要删除组"${group.name}"吗？`, '提示', {
      type: 'warning'
    })
    
    if (group.id) {
      loading.value = true
      await api.deleteGroupConfig(group.id)
      groups.value.splice(index, 1)
      ElMessage.success('删除成功')
    } else {
      // 如果没有ID，则直接从本地删除
      groups.value.splice(index, 1)
      ElMessage.success('删除成功')
    }
  } catch (error) {
    if (error instanceof Error && error.message.includes('cancel')) {
      // 用户取消
    } else {
      console.error('删除组失败:', error)
      ElMessage.error('删除组失败')
    }
  } finally {
    loading.value = false
  }
}

const handleSubmit = async () => {
  if (!form.value.name) {
    ElMessage.warning('请填写组名称')
    return
  }

  try {
    loading.value = true
    
    if (editingIndex.value !== null) {
      // 编辑现有组
      const group = groups.value[editingIndex.value]
      if (!group || !group.id) {
        ElMessage.error('无效的组或组ID')
        return
      }
      
      const updatedGroup = await api.updateGroupConfig(group.id, {
        ...group,
        ...form.value,
        id: group.id
      } as GroupConfig)
      
      if (!updatedGroup) {
        ElMessage.error('更新失败：服务器未返回数据')
        return
      }
      
      if (groups.value[editingIndex.value]) {
        Object.assign(groups.value[editingIndex.value]!, updatedGroup)
      } else {
        // 防止边界错误，如果原位置元素不存在则直接替换
        groups.value[editingIndex.value] = updatedGroup
      }
      ElMessage.success('组信息已更新')
    } else {
      // 创建新组
      const newGroup = await api.createGroupConfig({
        name: form.value.name!,
        remark: form.value.remark
      })
      
      if (!newGroup) {
        ElMessage.error('创建失败：服务器未返回数据')
        return
      }
      
      groups.value.push(newGroup)
      ElMessage.success('组已创建')
    }
    
    dialogVisible.value = false
  } catch (error) {
    console.error('保存组信息失败:', error)
    ElMessage.error('保存组信息失败')
  } finally {
    loading.value = false
  }
}
</script>