// Base API url
const API_BASE_URL = 'http://localhost:8000/api';

// Data models
export interface ShiftDefinition {
  id: number;
  name: string;
  startTime: string;
  endTime: string;
  enabled: boolean;
  remark?: string;
  // keep snake-case fields for compatibility
  big_week?: number[];
  small_week?: number[];
  bigWeek?: number[];
  smallWeek?: number[];
}

export interface GroupConfig {
  id?: number;
  name: string; // group name
  remark?: string; // note
}

// Person info
export interface Person {
  id: number;
  uid?: string;
  name: string;
  group: number | null;
  groupName?: string;
  shiftType?: ShiftDefinition;
  rotationGroup?: number;
  rotationGroupName?: string;
  remark?: string;
}

export interface Absence {
  id: number;
  person: number;
  startDate: string;
  endDate: string;
  reason: string;
  countAsRest: boolean;
  type: string;
}

export interface CalendarOverride {
  id: number;
  date: string;
  endDate?: string; // optional end date range support
  overrideType: string;
  scope?: string;
  target?: string;
  reason?: string;
  priority?: number;
}

export interface ShiftRotationGroup {
  id: number;
  name: string;
  odd_shift: number;
  even_shift: number;
  oddShiftName?: string;
  evenShiftName?: string;
  remark?: string;
}

export interface GlobalRules {
  id?: number;
  minConsecutiveWorkDays: number;
  maxConsecutiveWorkDays: number;
  forbiddenRestDays: string[];
  allowedRestDays: string[];
  smallWeekMustConsecutive: boolean;
  weekRotationMode: string;
  overrideWeekRules: boolean;
}

export interface ScheduleItem {
  person_id: number;
  person_name: string;
  group: string;
  rotation_group?: string;
  date: string;
  shift: string;
  status: string;
  is_violation: boolean;
  violationReason?: string;
}

export interface ScheduleResult {
  schedule: ScheduleItem[];
}

export interface YearScheduleResult {
  schedules: Record<string, ScheduleResult>;
}

// unified response handler
async function handleResponse<T>(response: Response): Promise<T | null> {
  if (!response.ok) {
    const errorText = await response.text();
    console.error(`API Error: ${response.status} - ${errorText}`);

    if (response.status === 404) {
      // some endpoints might legitimately return 404
      return null;
    }

    try {
      const errorJson = JSON.parse(errorText);
      throw new Error(`HTTP error! status: ${response.status}, details: ${JSON.stringify(errorJson)}`);
    } catch {
      throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
    }
  }

  if (response.status === 204) {
    return null;
  }

  const data = await response.json();
  return data;
}

// normalize snake_case from backend to camelCase for frontend usage
function normalizeShift(def: any): ShiftDefinition {
  return {
    id: def.id,
    name: def.name,
    startTime: def.start_time ?? def.startTime,
    endTime: def.end_time ?? def.endTime,
    enabled: def.enabled,
    remark: def.remark,
    bigWeek: def.big_week ?? def.bigWeek,
    smallWeek: def.small_week ?? def.smallWeek,
    big_week: def.big_week,
    small_week: def.small_week,
  };
}

// serialize camelCase payload to snake_case expected by backend
function serializeShift(def: Omit<ShiftDefinition, 'id'> | ShiftDefinition) {
  return {
    name: def.name,
    start_time: def.startTime,
    end_time: def.endTime,
    enabled: def.enabled,
    remark: def.remark,
    big_week: (def as any).big_week ?? def.bigWeek,
    small_week: (def as any).small_week ?? def.smallWeek,
  };
}

function normalizeAbsence(def: any): Absence {
  return {
    id: def.id,
    person: def.person,
    startDate: def.start_date ?? def.startDate,
    endDate: def.end_date ?? def.endDate,
    reason: def.reason,
    countAsRest: def.count_as_rest ?? def.countAsRest,
    type: def.type,
  };
}

function normalizePerson(def: any): Person {
  return {
    id: def.id,
    uid: def.uid,
    name: def.name,
    group: def.group ?? null,
    groupName: def.groupName ?? def.group_name,
    shiftType: def.shiftType ?? def.shift_type,
    rotationGroup: def.rotation_group ?? def.rotationGroup,
    rotationGroupName: def.rotationGroupName ?? def.rotation_group_name,
    remark: def.remark,
  };
}

function serializeAbsence(def: Omit<Absence, 'id'> | Absence) {
  return {
    person: def.person,
    start_date: def.startDate,
    end_date: def.endDate,
    reason: def.reason,
    count_as_rest: def.countAsRest,
    type: def.type,
  };
}

function normalizeCalendarOverride(def: any): CalendarOverride {
  return {
    id: def.id,
    date: def.date,
    endDate: def.end_date ?? def.endDate,
    overrideType: def.override_type ?? def.overrideType,
    scope: def.scope,
    target: def.target,
    reason: def.reason,
    priority: def.priority ?? 0,
  };
}

function serializeCalendarOverride(def: Omit<CalendarOverride, 'id'> | CalendarOverride) {
  return {
    date: def.date,
    end_date: def.endDate,
    override_type: def.overrideType,
    scope: def.scope,
    target: def.target,
    reason: def.reason,
    priority: def.priority ?? 0,
  };
}

// API methods
export const api = {
  // Shift Definition
  getShiftDefinitions: async (): Promise<ShiftDefinition[]> => {
    const response = await fetch(`${API_BASE_URL}/shift-definitions/`);
    const result = await handleResponse<any[]>(response);
    return (result || []).map(normalizeShift);
  },

  createShiftDefinition: async (shiftDef: Omit<ShiftDefinition, 'id'>): Promise<ShiftDefinition | null> => {
    const response = await fetch(`${API_BASE_URL}/shift-definitions/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(serializeShift(shiftDef)),
    });
    const result = await handleResponse<any>(response);
    return result ? normalizeShift(result) : null;
  },

  updateShiftDefinition: async (id: number, shiftDef: ShiftDefinition): Promise<ShiftDefinition | null> => {
    const response = await fetch(`${API_BASE_URL}/shift-definitions/${id}/`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(serializeShift(shiftDef)),
    });
    const result = await handleResponse<any>(response);
    return result ? normalizeShift(result) : null;
  },

  deleteShiftDefinition: async (id: number): Promise<void> => {
    const response = await fetch(`${API_BASE_URL}/shift-definitions/${id}/`, {
      method: 'DELETE',
    });
    await handleResponse(response);
  },

  // Group Config
  getGroupConfigs: async (): Promise<GroupConfig[] | null> => {
    const response = await fetch(`${API_BASE_URL}/group-configs/`);
    return handleResponse(response);
  },

  createGroupConfig: async (groupConfig: Omit<GroupConfig, 'id'>): Promise<GroupConfig | null> => {
    const response = await fetch(`${API_BASE_URL}/group-configs/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(groupConfig),
    });
    return handleResponse(response);
  },

  updateGroupConfig: async (id: number, groupConfig: GroupConfig): Promise<GroupConfig | null> => {
    const response = await fetch(`${API_BASE_URL}/group-configs/${id}/`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(groupConfig),
    });
    return handleResponse(response);
  },

  deleteGroupConfig: async (id: number): Promise<void> => {
    const response = await fetch(`${API_BASE_URL}/group-configs/${id}/`, {
      method: 'DELETE',
    });
    await handleResponse(response);
  },

  // Person management
  getPersons: async (): Promise<Person[]> => {
    const response = await fetch(`${API_BASE_URL}/persons/`);
    const result = await handleResponse<any[]>(response);
    return (result || []).map(normalizePerson);
  },

  async createPerson(person: Omit<Person, 'id'>): Promise<Person> {
    const personData = {
      ...person,
      uid: person.uid ?? null,
      shift_type: typeof person.shiftType === 'object' ? person.shiftType.id : person.shiftType,
      rotation_group: person.rotationGroup ?? null,
    };

    const response = await fetch(`${API_BASE_URL}/persons/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(personData),
    });
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return await response.json();
  },

  async updatePerson(id: number, person: Partial<Person>): Promise<Person> {
    const personData = {
      ...person,
      uid: person.uid ?? null,
      shift_type: typeof person.shiftType === 'object' ? person.shiftType?.id : person.shiftType,
      rotation_group: person.rotationGroup ?? null,
    };

    const response = await fetch(`${API_BASE_URL}/persons/${id}/`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(personData),
    });
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return await response.json();
  },

  deletePerson: async (id: number): Promise<void> => {
    const response = await fetch(`${API_BASE_URL}/persons/${id}/`, {
      method: 'DELETE',
    });
    await handleResponse(response);
  },

  // Shift rotation groups
  getShiftRotationGroups: async (): Promise<ShiftRotationGroup[]> => {
    const response = await fetch(`${API_BASE_URL}/shift-rotation-groups/`);
    return (await handleResponse(response)) ?? [];
  },

  createShiftRotationGroup: async (group: Omit<ShiftRotationGroup, 'id'>): Promise<ShiftRotationGroup | null> => {
    const response = await fetch(`${API_BASE_URL}/shift-rotation-groups/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(group),
    });
    return handleResponse(response);
  },

  updateShiftRotationGroup: async (id: number, group: ShiftRotationGroup): Promise<ShiftRotationGroup | null> => {
    const response = await fetch(`${API_BASE_URL}/shift-rotation-groups/${id}/`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(group),
    });
    return handleResponse(response);
  },

  deleteShiftRotationGroup: async (id: number): Promise<void> => {
    const response = await fetch(`${API_BASE_URL}/shift-rotation-groups/${id}/`, {
      method: 'DELETE',
    });
    await handleResponse(response);
  },

  // Absence management
  getAbsences: async (): Promise<Absence[]> => {
    const response = await fetch(`${API_BASE_URL}/absences/`);
    const result = await handleResponse<any[]>(response);
    return (result || []).map(normalizeAbsence);
  },

  createAbsence: async (absence: Omit<Absence, 'id'>): Promise<Absence | null> => {
    const response = await fetch(`${API_BASE_URL}/absences/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(serializeAbsence(absence)),
    });
    const result = await handleResponse<any>(response);
    return result ? normalizeAbsence(result) : null;
  },

  updateAbsence: async (id: number, absence: Absence): Promise<Absence | null> => {
    const response = await fetch(`${API_BASE_URL}/absences/${id}/`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(serializeAbsence(absence)),
    });
    const result = await handleResponse<any>(response);
    return result ? normalizeAbsence(result) : null;
  },

  deleteAbsence: async (id: number): Promise<void> => {
    const response = await fetch(`${API_BASE_URL}/absences/${id}/`, {
      method: 'DELETE',
    });
    await handleResponse(response);
  },

  // Calendar overrides
  getCalendarOverrides: async (): Promise<CalendarOverride[]> => {
    const response = await fetch(`${API_BASE_URL}/calendar-overrides/`);
    const result = await handleResponse<any[]>(response);
    return (result || []).map(normalizeCalendarOverride);
  },

  createCalendarOverride: async (override: Omit<CalendarOverride, 'id'>): Promise<CalendarOverride | null> => {
    const response = await fetch(`${API_BASE_URL}/calendar-overrides/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(serializeCalendarOverride(override)),
    });
    const result = await handleResponse<any>(response);
    return result ? normalizeCalendarOverride(result) : null;
  },

  updateCalendarOverride: async (id: number, override: CalendarOverride): Promise<CalendarOverride | null> => {
    const response = await fetch(`${API_BASE_URL}/calendar-overrides/${id}/`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(serializeCalendarOverride(override)),
    });
    const result = await handleResponse<any>(response);
    return result ? normalizeCalendarOverride(result) : null;
  },

  deleteCalendarOverride: async (id: number): Promise<void> => {
    const response = await fetch(`${API_BASE_URL}/calendar-overrides/${id}/`, {
      method: 'DELETE',
    });
    await handleResponse(response);
  },

  // Week schedule
  getWeekSchedules: async (): Promise<(ShiftDefinition & { bigWeek?: number[]; smallWeek?: number[] })[]> => {
    const response = await fetch(`${API_BASE_URL}/week-schedules/`);
    return (await handleResponse(response)) ?? [];
  },

  updateWeekSchedules: async (schedules: { shiftType: number; big_week: number[]; small_week: number[] }[]): Promise<{ message: string }> => {
    const response = await fetch(`${API_BASE_URL}/week-schedules/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(schedules),
    });
    return (await handleResponse(response)) ?? { message: '' };
  },

  // Schedule generator
  generateSchedule: async (
    yearMonth: string,
    baseWeekType?: '大周' | '小周',
    crossMonthContinuous: boolean = true
  ): Promise<ScheduleResult | null> => {
    const response = await fetch(`${API_BASE_URL}/generate-schedule/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        year_month: yearMonth,
        base_week_type: baseWeekType,
        cross_month_continuous: crossMonthContinuous,
      }),
    });
    return handleResponse(response);
  },

  generateYearSchedule: async (
    year: string,
    baseWeekType?: '大周' | '小周',
    crossMonthContinuous: boolean = true
  ): Promise<YearScheduleResult | null> => {
    const response = await fetch(`${API_BASE_URL}/generate-year-schedule/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        year,
        base_week_type: baseWeekType,
        cross_month_continuous: crossMonthContinuous,
      }),
    });
    return handleResponse(response);
  },
};
