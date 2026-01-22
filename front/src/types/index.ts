// 排班系统类型定义

// 人员状态
export type PersonStatus = '在岗参与' | '在岗不参与' | '离职'

// 班次类型
export type ShiftType = 'A' | 'B' | 'A+B'

// 不可用类型
export type AbsenceType = '请假' | '病假' | '出差' | '培训'

// 锁定类型
export type OverrideType = '必须上班' | '必须休息'

// 日历覆盖类型
export type CalendarOverrideType = '强制上班' | '强制休息'

// 作用范围
export type ScopeType = '全员' | '指定组' | '指定人员'

// 周类型
export type WeekType = '大周' | '小周'

// 人员信息 - 使用后端API定义的类型
// export interface Person {
//   id: string // 唯一ID
//   name: string // 姓名
//   group: string // 所属组
//   shiftType?: ShiftDefinition; // 班次类型（外键关联到ShiftDefinition）
//   remark?: string // 备注
// }

// 全局规则配置
export interface GlobalRules {
  id?: number; // 规则ID，可选
  minConsecutiveWorkDays: number // 连续工作最少天数
  maxConsecutiveWorkDays: number // 连续工作最多天数
  forbiddenRestDays: string[] // 禁止排休星期 ['周二', '周三', '周四']
  allowedRestDays: string[] // 允许排休星期 ['周五', '周六', '周日', '周一']
  smallWeekMustConsecutive: boolean // 小周是否必须连休
  weekRotationMode: string // 大小周执行方式
  overrideWeekRules: boolean // 调休是否覆盖周规则
}

// 班次定义 - 使用后端API定义的类型
// export interface ShiftDefinition {
//   id: number;
//   name: string;
//   startTime: string;
//   endTime: string;
//   enabled: boolean;
//   remark?: string;
// }

// 组配置 - 使用后端API定义的类型
// export interface GroupConfig {
//   id?: number
//   name: string // 组名称
//   remark?: string // 备注
// }

// 请假/不可用
export interface Absence {
  id: string
  personName: string // 姓名
  startDate: string // 开始日期 YYYY-MM-DD
  endDate: string // 结束日期 YYYY-MM-DD
  type: AbsenceType // 类型
  countAsRest: boolean // 是否算休息
  hardUnavailable: boolean // 是否硬不可用
  remark?: string // 说明
}

// 人员锁定规则
export interface PersonOverride {
  id: string
  personName: string // 姓名
  date: string // 日期 YYYY-MM-DD
  type: OverrideType // 锁定类型
  reason: string // 原因
  remark?: string // 备注
}

// 调休/节假日（日历覆盖）
export interface CalendarOverride {
  id: string
  date: string // 日期 YYYY-MM-DD
  type: CalendarOverrideType // 覆盖类型
  scope: ScopeType // 作用范围
  target?: string // 目标（组名或人员名）
  reason: string // 原因
}

// 特殊日期规则
export interface SpecialDateRule {
  id: string
  date: string // 日期 YYYY-MM-DD
  label: string // 标签
  group: string // 组别
  minOnDuty: number // 最少在岗人数
  requiredPersons?: string[] // 必须在岗人员
  remark?: string // 备注
}

// 大小周配置
export interface WeekRotationConfig {
  month: string // 月份 YYYY-MM
  firstWeekType: WeekType // 第一周类型
  remark?: string // 备注
}

// 排班结果
export interface ScheduleResult {
  personName: string
  date: string
  shift?: 'A' | 'B' // 班次
  status: '上班' | '休息' | '请假' | '调休'
  isViolation?: boolean // 是否违规
  violationReason?: string // 违规原因
}

// 违规明细
export interface Violation {
  month: string
  date: string
  personName?: string
  group?: string
  type: string // 违规类型
  description: string // 说明
}

// 排班生成记录
export interface ScheduleGenerationRecord {
  month: string
  generateTime: string
  ruleVersion: string
  status: '完全合规' | '有违规' | '无法生成'
  violationCount: number
  operator: string
}