from datetime import datetime
from typing import Optional

from fastapi import HTTPException

from backend.api.resource.accounting_period_resource import AccountingPeriodResource
from backend.api.resource.misc import ProjectResource, Employee, TaskResource, TaskType
from backend.db.model.unit_of_work import ReportedActivityModel
from backend.db.model.project import ProjectModel
from backend.db.model.derived import TaskModel, ProjectStatsModel
from backend.db.model.employee import EmployeeModel


def convert_project_model_to_project(
        project_model: ProjectModel,
        project_stats_models: list[ProjectStatsModel] = None,
        accounting_period_resources: list[AccountingPeriodResource] = None) -> ProjectResource:

    project_stats_models = project_stats_models or []
    accounting_period_resources = accounting_period_resources or []

    if len(project_stats_models) > 0 and len(accounting_period_resources) > 0:
        raise HTTPException(status_code=500, detail="Cannot provide both project_stats_models and accounting_period_resource")

    total_hours = 0
    total_cost = 0

    normalized_hours = 0
    normalized_cost = 0

    capitalizable_hours = 0
    capitalizable_cost = 0

    updated_at = datetime.min

    if len(project_stats_models) > 0:
        project_stats_model: ProjectStatsModel
        for project_stats_model in project_stats_models:
            total_hours += project_stats_model.total_hours
            total_cost += project_stats_model.total_cost

            normalized_hours += project_stats_model.normalized_hours
            normalized_cost += project_stats_model.normalized_cost

            capitalizable_hours += project_stats_model.capitalizable_hours
            capitalizable_cost += project_stats_model.capitalizable_cost
            updated_at = max(updated_at, project_stats_model.computed_at)

    elif len(accounting_period_resources) > 0:
        accounting_period: AccountingPeriodResource
        for accounting_period in accounting_period_resources:
            total_hours += accounting_period.total_hours if accounting_period.total_hours is not None else 0
            total_cost += accounting_period.total_cost if accounting_period.total_cost is not None else 0

            normalized_hours += accounting_period.normalized_hours if accounting_period.normalized_hours is not None else 0
            normalized_cost += accounting_period.normalized_cost if accounting_period.normalized_cost is not None else 0

            capitalizable_hours += accounting_period.capitalizable_hours if accounting_period.capitalizable_hours is not None else 0
            capitalizable_cost += accounting_period.capitalizable_cost if accounting_period.capitalizable_cost is not None else 0
            updated_at = max(updated_at, accounting_period.updated_at) if accounting_period.updated_at is not None else updated_at

    if total_hours == 0:
        status = "Pending"
    else: # total_hours > 0
        status = "In Progress"

    return ProjectResource(
        id=project_model.id,
        name=project_model.name,
        capitalizable=project_model.capitalizable,
        issue_tracker_ids=project_model.issue_tracker_ids,
        # TODO: get this from metadata about the latest run
        status=status,
        # percent_cost=percent_cost,
        total_hours=total_hours,
        total_cost=total_cost,
        normalized_hours=normalized_hours,
        normalized_cost=normalized_cost,
        capitalizable_hours=capitalizable_hours,
        capitalizable_cost=capitalizable_cost,
        # TODO: don't return current timestamp if there are no accounting periods
        updated_at=updated_at.date() if updated_at is not datetime.min else datetime.utcnow(),
    )

def convert_task_model_to_task(task_model: Optional[TaskModel], employee_model: Optional[EmployeeModel], reported_activity: Optional[ReportedActivityModel] = None) -> TaskResource:
    # ensure at least one of task_model or reported_activity is not None
    if task_model is None and reported_activity is None:
        raise HTTPException(status_code=500, detail="Task and reported activity are both None")

    if task_model and employee_model is None != task_model.employee_id is None:
        raise HTTPException(status_code=500, detail="Task and employee do not match")

    # if employee_model is not None and not (task_model.employee_id == employee_model.id or reported_activity.employee_id == employee_model.id):
    #     raise HTTPException(status_code=500, detail="Task and employee do not match")

    return TaskResource(
        id=task_model.id if task_model is not None else None,
        project_id=task_model.project_id if task_model is not None else None,
        accounting_period_name=task_model.accounting_period_name if task_model is not None else None,
        type=task_model.type if task_model is not None else TaskType.REPORTED.value,
        employee=convert_employee_model_to_employee(employee_model),
        description=task_model.description if task_model is not None else None,
        total_hours=reported_activity.total_hours if reported_activity is not None else task_model.total_hours,
        reported_cap_percentage=reported_activity.capitalization_percentage if reported_activity is not None else None,
        total_cost=task_model.total_cost if task_model is not None else None,
        capitalizable_hours=task_model.capitalizable_hours if task_model is not None else None,
        capitalizable_cost=task_model.computed_capitalizable_cost if task_model is not None else None,
        normalized_hours=task_model.normalized_hours if task_model is not None else None,

        reported_activity_id=reported_activity.id if reported_activity is not None else None,
    )


def convert_employee_model_to_employee(employee_model: Optional[EmployeeModel]) -> Employee:
    # if employee_model is None:
    #     return EMPTY_EMPLOYEE

    return Employee(
        id=employee_model.id,
        name=employee_model.name,
        email=employee_model.email,
    )
