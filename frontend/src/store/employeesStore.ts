import { create } from 'zustand'

interface Employee {
  employee_id: number
  full_name: string
  email: string | null
  phone: string | null
  hire_date: string
  department_id: number
  position_id: number
  personnel_number?: string
  birth_date?: string
  termination_date?: string
}

interface EmployeesState {
  employees: Employee[]
  total: number
  skip: number
  limit: number
  isLoading: boolean
  error: string | null

  // Actions
  setEmployees: (employees: Employee[], total: number) => void
  addEmployee: (employee: Employee) => void
  updateEmployee: (id: number, employee: Partial<Employee>) => void
  deleteEmployee: (id: number) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  clearEmployees: () => void
}

export const useEmployeesStore = create<EmployeesState>((set) => ({
  employees: [],
  total: 0,
  skip: 0,
  limit: 20,
  isLoading: false,
  error: null,

  setEmployees: (employees, total) => set({ employees, total, error: null }),

  addEmployee: (employee) =>
    set((state) => ({
      employees: [...state.employees, employee],
      total: state.total + 1,
    })),

  updateEmployee: (id, employee) =>
    set((state) => ({
      employees: state.employees.map((emp) =>
        emp.employee_id === id ? { ...emp, ...employee } : emp
      ),
    })),

  deleteEmployee: (id) =>
    set((state) => ({
      employees: state.employees.filter((emp) => emp.employee_id !== id),
      total: state.total - 1,
    })),

  setLoading: (loading) => set({ isLoading: loading }),

  setError: (error) => set({ error, isLoading: false }),

  clearEmployees: () =>
    set({
      employees: [],
      total: 0,
      skip: 0,
      limit: 20,
      isLoading: false,
      error: null,
    }),
}))
