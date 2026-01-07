// API Types
export interface Employee {
    name: string;
    email: string;
    title: string;
    department: string;
    skills: string[];
}

export interface Project {
    project_id: string;
    name: string;
    status: 'active' | 'completed' | 'planning' | 'on-hold' | 'cancelled';
    type: string;
    description: string;
    team_size: number;
    budget?: number;
    priority?: string;
}

export interface SkillExpert {
    skill: string;
    experts: Array<{
        name: string;
        email: string;
        title: string;
        department: string;
        proficiency: string;
        years_experience: number;
    }>;
}

export interface DepartmentStats {
    department: string;
    employee_count: number;
    active_projects: number;
}

export interface QueryRequest {
    question: string;
    include_cypher?: boolean;
}

export interface QueryResponse {
    question: string;
    answer: string;
    cypher_query?: string;
    metadata?: {
        provider: string;
        model: string;
    };
}

export interface HealthResponse {
    status: string;
    neo4j_connected: boolean;
    details?: {
        environment?: string;
        version?: string;
        llm_provider?: string;
        redis_connected?: boolean;
        celery_workers?: number;
        celery_healthy?: boolean;
    };
}

export interface SchemaResponse {
    nodes: Record<string, number>;
    relationships: Record<string, number>;
    total_nodes: number;
    total_relationships: number;
}
