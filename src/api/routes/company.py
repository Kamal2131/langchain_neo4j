"""
Custom API routes for Company Knowledge Base use case.
Domain-specific endpoints for querying company data.
"""

from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from src.core.logging import get_logger
from src.services.neo4j_service import neo4j_service

logger = get_logger(__name__)

router = APIRouter(prefix="/company", tags=["Company KB"])


# Response models
class EmployeeInfo(BaseModel):
    """Employee information."""

    name: str
    email: str
    title: str
    department: str
    skills: List[str] = []


class ProjectInfo(BaseModel):
    """Project information."""

    project_id: str
    name: str
    status: str
    description: str
    team_size: int


class SkillExpert(BaseModel):
    """Skill expert information."""

    skill: str
    experts: List[Dict[str, Any]]


class DepartmentStats(BaseModel):
    """Department statistics."""

    department: str
    employee_count: int
    active_projects: int


# Endpoints


@router.get("/employees", response_model=List[EmployeeInfo])
async def get_all_employees(
    department: str = Query(None, description="Filter by department")
) -> List[EmployeeInfo]:
    """
    Get all employees, optionally filtered by department.

    Args:
        department: Optional department name to filter by
    """
    try:
        graph = neo4j_service.get_graph()

        if department:
            query = """
                MATCH (e:Employee)-[:WORKS_IN]->(d:Department {name: $dept})
                OPTIONAL MATCH (e)-[:HAS_SKILL]->(s:Skill)
                RETURN e.name as name, e.email as email, e.title as title,
                       d.name as department, collect(DISTINCT s.name) as skills
            """
            params = {"dept": department}
        else:
            query = """
                MATCH (e:Employee)-[:WORKS_IN]->(d:Department)
                OPTIONAL MATCH (e)-[:HAS_SKILL]->(s:Skill)
                RETURN e.name as name, e.email as email, e.title as title,
                       d.name as department, collect(DISTINCT s.name) as skills
            """
            params = {}

        result = graph.query(query, params=params)

        employees = [
            EmployeeInfo(
                name=row["name"],
                email=row["email"],
                title=row["title"],
                department=row["department"],
                skills=[s for s in row["skills"] if s],
            )
            for row in result
        ]

        logger.info(f"Retrieved {len(employees)} employees")
        return employees

    except Exception as e:
        logger.error(f"Failed to get employees: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/projects", response_model=List[ProjectInfo])
async def get_projects(
    status: str = Query(None, description="Filter by status (active, completed, planning)")
) -> List[ProjectInfo]:
    """
    Get all projects, optionally filtered by status.

    Args:
        status: Optional status to filter by
    """
    try:
        graph = neo4j_service.get_graph()

        if status:
            query = """
                MATCH (p:Project {status: $status})
                OPTIONAL MATCH (e:Employee)-[:WORKS_ON]->(p)
                RETURN p.project_id as project_id, p.name as name, p.status as status,
                       p.description as description, count(DISTINCT e) as team_size
            """
            params = {"status": status}
        else:
            query = """
                MATCH (p:Project)
                OPTIONAL MATCH (e:Employee)-[:WORKS_ON]->(p)
                RETURN p.project_id as project_id, p.name as name, p.status as status,
                       p.description as description, count(DISTINCT e) as team_size
            """
            params = {}

        result = graph.query(query, params=params)

        projects = [
            ProjectInfo(
                project_id=row["project_id"],
                name=row["name"],
                status=row["status"],
                description=row["description"],
                team_size=row["team_size"],
            )
            for row in result
        ]

        logger.info(f"Retrieved {len(projects)} projects")
        return projects

    except Exception as e:
        logger.error(f"Failed to get projects: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/skills/{skill_name}/experts", response_model=SkillExpert)
async def get_skill_experts(skill_name: str) -> SkillExpert:
    """
    Find experts for a specific skill.

    Args:
        skill_name: Name of the skill
    """
    try:
        graph = neo4j_service.get_graph()

        query = """
            MATCH (e:Employee)-[r:HAS_SKILL]->(s:Skill {name: $skill})
            MATCH (e)-[:WORKS_IN]->(d:Department)
            RETURN e.name as name, e.email as email, e.title as title,
                   d.name as department, r.proficiency as proficiency,
                   r.years as years
            ORDER BY r.proficiency DESC, r.years DESC
        """

        result = graph.query(query, params={"skill": skill_name})

        if not result:
            raise HTTPException(status_code=404, detail=f"No experts found for skill: {skill_name}")

        experts = [
            {
                "name": row["name"],
                "email": row["email"],
                "title": row["title"],
                "department": row["department"],
                "proficiency": row["proficiency"],
                "years_experience": row["years"],
            }
            for row in result
        ]

        logger.info(f"Found {len(experts)} experts for {skill_name}")
        return SkillExpert(skill=skill_name, experts=experts)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get skill experts: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/departments/stats", response_model=List[DepartmentStats])
async def get_department_stats() -> List[DepartmentStats]:
    """Get statistics for all departments."""
    try:
        graph = neo4j_service.get_graph()

        query = """
            MATCH (d:Department)
            OPTIONAL MATCH (e:Employee)-[:WORKS_IN]->(d)
            OPTIONAL MATCH (emp:Employee)-[:WORKS_ON]->(p:Project {status: 'active'})
            WHERE (emp)-[:WORKS_IN]->(d)
            RETURN d.name as department,
                   count(DISTINCT e) as employee_count,
                   count(DISTINCT p) as active_projects
            ORDER BY employee_count DESC
        """

        result = graph.query(query)

        stats = [
            DepartmentStats(
                department=row["department"],
                employee_count=row["employee_count"],
                active_projects=row["active_projects"],
            )
            for row in result
        ]

        logger.info(f"Retrieved stats for {len(stats)} departments")
        return stats

    except Exception as e:
        logger.error(f"Failed to get department stats: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/employees/{email}/projects")
async def get_employee_projects(email: str) -> Dict[str, Any]:
    """
    Get all projects for a specific employee.

    Args:
        email: Employee email address
    """
    try:
        graph = neo4j_service.get_graph()

        query = """
            MATCH (e:Employee {email: $email})-[r:WORKS_ON]->(p:Project)
            RETURN p.project_id as project_id, p.name as name, p.status as status,
                   r.role as role, r.hours_per_week as hours
            ORDER BY p.status, p.name
        """

        result = graph.query(query, params={"email": email})

        if not result:
            raise HTTPException(status_code=404, detail=f"No projects found for employee: {email}")

        projects = [
            {
                "project_id": row["project_id"],
                "name": row["name"],
                "status": row["status"],
                "role": row["role"],
                "hours_per_week": row["hours"],
            }
            for row in result
        ]

        logger.info(f"Found {len(projects)} projects for {email}")
        return {"email": email, "projects": projects}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get employee projects: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/projects/{project_id}/team")
async def get_project_team(project_id: str) -> Dict[str, Any]:
    """
    Get team members for a specific project.

    Args:
        project_id: Project ID
    """
    try:
        graph = neo4j_service.get_graph()

        query = """
            MATCH (p:Project {project_id: $project_id})
            OPTIONAL MATCH (e:Employee)-[r:WORKS_ON]->(p)
            MATCH (e)-[:WORKS_IN]->(d:Department)
            RETURN p.name as project_name, p.status as status,
                   e.name as employee_name, e.email as email, e.title as title,
                   d.name as department, r.role as project_role
            ORDER BY r.role, e.name
        """

        result = graph.query(query, params={"project_id": project_id})

        if not result:
            raise HTTPException(status_code=404, detail=f"Project not found: {project_id}")

        team = [
            {
                "name": row["employee_name"],
                "email": row["email"],
                "title": row["title"],
                "department": row["department"],
                "project_role": row["project_role"],
            }
            for row in result
            if row["employee_name"]
        ]

        logger.info(f"Found {len(team)} team members for project {project_id}")
        return {
            "project_id": project_id,
            "project_name": result[0]["project_name"],
            "status": result[0]["status"],
            "team": team,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get project team: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e
