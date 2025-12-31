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
    neo4j_status?: string;
    schema?: {
        total_nodes: number;
        total_relationships: number;
        node_labels: Record<string, number>;
        relationship_types: Record<string, number>;
    };
}
