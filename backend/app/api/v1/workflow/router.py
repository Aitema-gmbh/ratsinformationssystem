"""
aitema|RIS - Workflow API Endpoints
Paper approval workflows and meeting management workflows.
"""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import Permission, require_permission, TokenPayload
from app.models.extensions import (
    ApprovalDecision,
    ApprovalInstance,
    ApprovalWorkflow,
    ApprovalWorkflowStep,
    WorkflowStatus,
)

router = APIRouter()


# ===================================================================
# Schemas
# ===================================================================

class WorkflowCreate(BaseModel):
    name: str
    description: str | None = None
    steps: list["WorkflowStepCreate"] = []


class WorkflowStepCreate(BaseModel):
    name: str
    description: str | None = None
    order: int
    required_role: str | None = None
    required_organization_id: UUID | None = None
    auto_advance: bool = False


class WorkflowInstanceCreate(BaseModel):
    paper_id: UUID
    workflow_id: UUID


class DecisionCreate(BaseModel):
    decision: str  # approved, rejected, returned
    comment: str | None = None


class WorkflowResponse(BaseModel):
    id: UUID
    name: str
    description: str | None
    is_active: bool

    model_config = {"from_attributes": True}


class InstanceResponse(BaseModel):
    id: UUID
    paper_id: UUID
    workflow_id: UUID
    status: str
    current_step_id: UUID | None

    model_config = {"from_attributes": True}


# ===================================================================
# Workflow Definition CRUD
# ===================================================================

@router.get("/workflows", response_model=list[WorkflowResponse])
async def list_workflows(
    db: AsyncSession = Depends(get_db),
    user: TokenPayload = Depends(require_permission(Permission.WORKFLOW_MANAGE)),
):
    """List all approval workflow definitions."""
    result = await db.execute(
        select(ApprovalWorkflow).where(ApprovalWorkflow.is_active == True)
    )
    return result.scalars().all()


@router.post("/workflows", response_model=WorkflowResponse, status_code=201)
async def create_workflow(
    data: WorkflowCreate,
    db: AsyncSession = Depends(get_db),
    user: TokenPayload = Depends(require_permission(Permission.WORKFLOW_MANAGE)),
):
    """Create a new approval workflow with steps."""
    workflow = ApprovalWorkflow(
        name=data.name,
        description=data.description,
    )
    db.add(workflow)
    await db.flush()

    for step_data in data.steps:
        step = ApprovalWorkflowStep(
            workflow_id=workflow.id,
            name=step_data.name,
            description=step_data.description,
            order=step_data.order,
            required_role=step_data.required_role,
            required_organization_id=step_data.required_organization_id,
            auto_advance=step_data.auto_advance,
        )
        db.add(step)

    await db.commit()
    await db.refresh(workflow)
    return workflow


@router.get("/workflows/{workflow_id}")
async def get_workflow(
    workflow_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: TokenPayload = Depends(require_permission(Permission.WORKFLOW_MANAGE)),
):
    """Get a workflow with all its steps."""
    result = await db.execute(
        select(ApprovalWorkflow).where(ApprovalWorkflow.id == workflow_id)
    )
    workflow = result.scalar_one_or_none()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return {
        "id": workflow.id,
        "name": workflow.name,
        "description": workflow.description,
        "is_active": workflow.is_active,
        "steps": [
            {
                "id": s.id,
                "name": s.name,
                "order": s.order,
                "required_role": s.required_role,
                "auto_advance": s.auto_advance,
            }
            for s in workflow.steps
        ],
    }


# ===================================================================
# Workflow Instances (applied to papers)
# ===================================================================

@router.post("/instances", response_model=InstanceResponse, status_code=201)
async def start_workflow(
    data: WorkflowInstanceCreate,
    db: AsyncSession = Depends(get_db),
    user: TokenPayload = Depends(require_permission(Permission.PAPER_SUBMIT)),
):
    """Start a workflow for a paper (submit paper for approval)."""
    # Verify workflow exists
    wf_result = await db.execute(
        select(ApprovalWorkflow).where(ApprovalWorkflow.id == data.workflow_id)
    )
    workflow = wf_result.scalar_one_or_none()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    # Get first step
    first_step = workflow.steps[0] if workflow.steps else None

    instance = ApprovalInstance(
        paper_id=data.paper_id,
        workflow_id=data.workflow_id,
        current_step_id=first_step.id if first_step else None,
        status=WorkflowStatus.SUBMITTED,
    )
    db.add(instance)
    await db.commit()
    await db.refresh(instance)
    return instance


@router.get("/instances/{instance_id}")
async def get_instance(
    instance_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: TokenPayload = Depends(require_permission(Permission.OPARL_READ)),
):
    """Get workflow instance with decision history."""
    result = await db.execute(
        select(ApprovalInstance).where(ApprovalInstance.id == instance_id)
    )
    instance = result.scalar_one_or_none()
    if not instance:
        raise HTTPException(status_code=404, detail="Instance not found")
    return {
        "id": instance.id,
        "paper_id": instance.paper_id,
        "workflow_id": instance.workflow_id,
        "status": instance.status,
        "current_step_id": instance.current_step_id,
        "decisions": [
            {
                "id": d.id,
                "step_id": d.step_id,
                "decided_by": d.decided_by,
                "decision": d.decision,
                "comment": d.comment,
                "decided_at": d.decided_at.isoformat(),
            }
            for d in instance.decisions
        ],
    }


@router.post("/instances/{instance_id}/decide")
async def make_decision(
    instance_id: UUID,
    data: DecisionCreate,
    db: AsyncSession = Depends(get_db),
    user: TokenPayload = Depends(require_permission(Permission.WORKFLOW_APPROVE)),
):
    """Make a decision (approve/reject) on the current workflow step."""
    result = await db.execute(
        select(ApprovalInstance).where(ApprovalInstance.id == instance_id)
    )
    instance = result.scalar_one_or_none()
    if not instance:
        raise HTTPException(status_code=404, detail="Instance not found")

    if instance.status not in (WorkflowStatus.SUBMITTED, WorkflowStatus.IN_REVIEW):
        raise HTTPException(
            status_code=400,
            detail=f"Cannot decide on instance with status '{instance.status}'",
        )

    # Record the decision
    decision = ApprovalDecision(
        instance_id=instance.id,
        step_id=instance.current_step_id,
        decided_by=user.sub,
        decision=data.decision,
        comment=data.comment,
    )
    db.add(decision)

    if data.decision == "approved":
        # Try to advance to next step
        wf_result = await db.execute(
            select(ApprovalWorkflow).where(
                ApprovalWorkflow.id == instance.workflow_id
            )
        )
        workflow = wf_result.scalar_one()
        steps = sorted(workflow.steps, key=lambda s: s.order)

        current_idx = next(
            (i for i, s in enumerate(steps) if s.id == instance.current_step_id),
            -1,
        )

        if current_idx < len(steps) - 1:
            # Advance to next step
            instance.current_step_id = steps[current_idx + 1].id
            instance.status = WorkflowStatus.IN_REVIEW
        else:
            # All steps completed
            instance.status = WorkflowStatus.APPROVED
            instance.current_step_id = None
            from datetime import datetime, timezone
            instance.completed_at = datetime.now(timezone.utc)

    elif data.decision == "rejected":
        instance.status = WorkflowStatus.REJECTED
        from datetime import datetime, timezone
        instance.completed_at = datetime.now(timezone.utc)

    elif data.decision == "returned":
        # Send back to previous step or draft
        instance.status = WorkflowStatus.DRAFT

    await db.commit()
    await db.refresh(instance)
    return {
        "id": instance.id,
        "status": instance.status,
        "current_step_id": instance.current_step_id,
    }
