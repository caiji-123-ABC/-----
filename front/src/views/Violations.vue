<template>
  <div class="page-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>违规明细</span>
          <el-button type="primary" @click="handleExport" :icon="Download" :disabled="violations.length === 0">
            导出Excel
          </el-button>
        </div>
      </template>

      <el-table :data="violations" border style="width: 100%">
        <el-table-column prop="month" label="月份" width="120" />
        <el-table-column prop="date" label="日期" width="120">
          <template #default="{ row }">
            {{ formatDate(row.date) }}
          </template>
        </el-table-column>
        <el-table-column prop="personName" label="姓名" width="120">
          <template #default="{ row }">
            {{ row.personName || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="group" label="组别" width="120">
          <template #default="{ row }">
            {{ row.group || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="type" label="违规类型" width="150">
          <template #default="{ row }">
            <el-tag type="danger">{{ row.type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="说明" />
      </el-table>

      <div v-if="violations.length === 0" class="empty-state">
        <el-empty description="暂无违规记录" />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { Download } from '@element-plus/icons-vue'
import { violations } from '../stores/scheduleStore'
import { ElMessage } from 'element-plus'
import * as XLSX from 'xlsx'
import dayjs from 'dayjs'

const formatDate = (dateStr: string) => {
  const dateObj = dayjs(dateStr)
  const month = dateObj.month() + 1
  const day = dateObj.date()
  return `${month}月${day}日`
}

const handleExport = () => {
  if (violations.value.length === 0) {
    ElMessage.warning('没有可导出的数据')
    return
  }

  const exportData = violations.value.map(v => {
    const dateObj = dayjs(v.date)
    const month = dateObj.month() + 1
    const day = dateObj.date()
    return {
      月份: v.month,
      日期: `${month}月${day}日`,
      姓名: v.personName || '',
      组别: v.group || '',
      违规类型: v.type,
      说明: v.description
    }
  })

  const ws = XLSX.utils.json_to_sheet(exportData)
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, '违规明细')

  const today = dayjs()
  const fileName = `违规明细_${today.year()}年${today.month() + 1}月${today.date()}日.xlsx`
  XLSX.writeFile(wb, fileName)
  ElMessage.success('导出成功')
}
</script>

<style scoped>
.empty-state {
  padding: 40px;
  text-align: center;
}
</style>
