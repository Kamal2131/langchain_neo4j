import axios, { AxiosError } from 'axios';
import type {
    Employee,
    Project,
    SkillExpert,
    DepartmentStats,
    QueryRequest,
    QueryResponse,
    HealthResponse,
} from '@/types/api';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
    timeout: 30000, // 30 seconds
});

// Add response interceptor for better error handling
api.interceptors.response.use(
    (response) => response,
    (error: AxiosError) => {
        if (error.response) {
            // Server responded with error
            console.error('API Error:', error.response.status, error.response.data);
        } else if (error.request) {
            // Request made but no response
            console.error('Network Error: No response from server');
        } else {
            // Error setting up request
            console.error('Request Error:', error.message);
        }
        return Promise.reject(error);
    }
);

// Health & Info
export const healthApi = {
    getHealth: () => api.get<HealthResponse>('/health'),
    getSchema: () => api.get<HealthResponse>('/health/schema'),
};

// Natural Language Query
export const queryApi = {
    query: (data: QueryRequest) => api.post<QueryResponse>('/query', data),
    getSampleQuestions: () => api.get<string[]>('/query/examples'),
};

// Company Knowledge Base
export const companyApi = {
    getEmployees: (department?: string) =>
        api.get<Employee[]>('/company/employees', {
            params: department ? { department } : undefined,
        }),

    getProjects: (status?: string) =>
        api.get<Project[]>('/company/projects', {
            params: status ? { status } : undefined,
        }),

    getSkillExperts: (skillName: string) =>
        api.get<SkillExpert>(`/company/skills/${encodeURIComponent(skillName)}/experts`),

    getDepartmentStats: () =>
        api.get<DepartmentStats[]>('/company/departments/stats'),

    getEmployeeProjects: (email: string) =>
        api.get(`/company/employees/${encodeURIComponent(email)}/projects`),

    getProjectTeam: (projectId: string) =>
        api.get(`/company/projects/${encodeURIComponent(projectId)}/team`),
};
