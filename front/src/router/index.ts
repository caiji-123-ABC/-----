import { createRouter, createWebHistory } from 'vue-router'
import ShiftDefinitions from '../views/ShiftDefinitions.vue'
import GroupConfigs from '../views/GroupConfigs.vue'
import Persons from '../views/Persons.vue'
import Absences from '../views/Absences.vue'
import CalendarOverrides from '../views/CalendarOverrides.vue'
import WeekRotation from '../views/WeekRotation.vue'
import Schedule from '../views/Schedule.vue'
import Violations from '../views/Violations.vue'

const routes = [
  { path: '/', redirect: '/rules' },
  { path: '/shifts', component: ShiftDefinitions },
  { path: '/groups', component: GroupConfigs },
  { path: '/persons', component: Persons },
  { path: '/absences', component: Absences },
  { path: '/calendar', component: CalendarOverrides },
  { path: '/week-rotation', component: WeekRotation },
  { path: '/schedule', component: Schedule },
  { path: '/violations', component: Violations }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
