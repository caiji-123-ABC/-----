<template>
  <el-container class="app-container">
    <el-header class="app-header">
      <div class="header-content">
        <h1 class="app-title">
          <el-icon><Calendar /></el-icon>
          排班管理系统
        </h1>
        <div class="header-actions">
        </div>
      </div>
    </el-header>
    <el-container>
      <el-aside width="280px" class="app-sidebar">
        <el-menu
          :default-active="activeMenu"
          @select="handleMenuSelect"
          class="sidebar-menu"
          background-color="#f5f7fa"
          text-color="#303133"
          active-text-color="#409EFF"
        >
          <el-menu-item index="shifts">
            <el-icon><Clock /></el-icon>
            <span>班次定义</span>
          </el-menu-item>
          <el-menu-item index="groups">
            <el-icon><OfficeBuilding /></el-icon>
            <span>组配置</span>
          </el-menu-item>
          <el-menu-item index="persons">
            <el-icon><User /></el-icon>
            <span>人员管理</span>
          </el-menu-item>
          <el-menu-item index="absences">
            <el-icon><DocumentRemove /></el-icon>
            <span>请假管理</span>
          </el-menu-item>
          <el-menu-item index="calendar">
            <el-icon><Calendar /></el-icon>
            <span>调休/节假日</span>
          </el-menu-item>
          <el-menu-item index="week-rotation">
            <el-icon><Refresh /></el-icon>
            <span>大小周配置</span>
          </el-menu-item>
          <el-menu-item index="schedule">
            <el-icon><Grid /></el-icon>
            <span>排班生成</span>
          </el-menu-item>
          <el-menu-item index="violations">
            <el-icon><Warning /></el-icon>
            <span>违规明细</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      <el-main class="app-main">
        <router-view v-if="dataLoaded" />
        <div v-else class="loading">正在加载数据...</div>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import {
  Calendar,
  Clock,
  OfficeBuilding,
  User,
  DocumentRemove,
  Edit,
  Refresh,
  Grid,
  Warning
} from '@element-plus/icons-vue'
import { 
  loadFromApi, 
  loadFromLocalStorage, 
} from './stores/scheduleStore'


const router = useRouter()
const route = useRoute()
const activeMenu = ref('shifts')
const dataLoaded = ref(false)

onMounted(async () => {
  // 初始化路由
  if (route.path === '/') {
    router.push('/shifts')
  } else {
    activeMenu.value = route.path.slice(1) || 'shifts'
  }
  
  // 从后端加载数据
  try {
    await loadFromApi()
    console.log("成功从后端加载数据")
  } catch (error) {
    console.error("从后端加载数据失败，将尝试从本地加载:", error)
    // 如果从后端加载失败，尝试从localStorage加载
    loadFromLocalStorage()
  }
  
  dataLoaded.value = true
})

const handleMenuSelect = (key: string) => {
  router.push(`/${key}`)
}

</script>

<style scoped>
.app-container {
  height: 100vh;
}

.app-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 0;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  z-index: 100;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
  padding: 0 24px;
}

.app-title {
  font-size: 22px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.app-sidebar {
  background-color: #f5f7fa;
  border-right: 1px solid #ebeef5;
  box-shadow: inset -2px 0 4px rgba(0, 0, 0, 0.03);
  padding: 24px 0;
  height: calc(100vh - 60px);
  position: sticky;
  top: 0;
}

.sidebar-menu {
  border-right: none;
  background-color: transparent;
}

.app-main {
  background-color: #f5f7fa;
  padding: 24px;
  overflow-y: auto;
  font-size: 16px;
}

.loading {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  font-size: 18px;
  color: #909399;
}

/* 菜单项悬停效果 */
.sidebar-menu .el-menu-item {
  margin: 0 12px;
  border-radius: 8px;
  transition: all 0.3s ease;
  height: 58px;
  display: flex;
  align-items: center;
  padding-left: 20px !important;
  font-size: 16px;
}

.sidebar-menu .el-menu-item .el-icon {
  font-size: 20px;
}

.sidebar-menu .el-menu-item:hover {
  background-color: #eef2ff;
}

.sidebar-menu .el-menu-item.is-active {
  background-color: #eef2ff;
  color: #409EFF;
  font-weight: 500;
}
</style>
