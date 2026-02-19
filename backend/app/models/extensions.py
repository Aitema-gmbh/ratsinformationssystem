"""
aitema|RIS - Extension Models
Additional models beyond the OParl standard for aitema-specific features.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from enum import StrEnum
from typing import Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Table,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


# ===================================================================
# Template - Reusable document templates (Vorlagen-Vorlagen)
# ===================================================================

class Template(Base):
    """Template for creating papers (Vorlagen) with predefined structure."""
    __tablename__ = "template"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(512), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    paper_type: Mapped[str] = mapped_column(
        String(255), nullable=False,
        doc="Type of paper this template creates (Beschlussvorlage, Antrag, etc.)"
    )
    content_schema: Mapped[dict] = mapped_column(
        JSONB, nullable=False, default=dict,
        doc="JSON Schema defining the template structure and required fields"
    )
    default_workflow_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("approval_workflow.id"), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    modified: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    default_workflow: Mapped[Optional["ApprovalWorkflow"]] = relationship(
        "ApprovalWorkflow", lazy="selectin"
    )


# ===================================================================
# ApprovalWorkflow - Multi-step approval process
# ===================================================================

class WorkflowStatus(StrEnum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"
    PUBLISHED = "published"


class ApprovalWorkflow(Base):
    """
    Defines a multi-step approval workflow for papers.
    Each workflow has ordered steps that must be completed.
    """
    __tablename__ = "approval_workflow"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(512), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    steps: Mapped[list["ApprovalWorkflowStep"]] = relationship(
        "ApprovalWorkflowStep", back_populates="workflow",
        order_by="ApprovalWorkflowStep.order", lazy="selectin"
    )


class ApprovalWorkflowStep(Base):
    """A single step in an approval workflow."""
    __tablename__ = "approval_workflow_step"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    workflow_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("approval_workflow.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(512), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    order: Mapped[int] = mapped_column(Integer, nullable=False)
    required_role: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True,
        doc="Role required to approve this step"
    )
    required_organization_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organization.id"), nullable=True,
        doc="Organization that must approve this step"
    )
    auto_advance: Mapped[bool] = mapped_column(
        Boolean, default=False,
        doc="Automatically advance to next step on approval"
    )

    workflow: Mapped["ApprovalWorkflow"] = relationship(
        "ApprovalWorkflow", back_populates="steps"
    )


class ApprovalInstance(Base):
    """
    An instance of a workflow applied to a specific paper.
    Tracks the current state and history of approvals.
    """
    __tablename__ = "approval_instance"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    paper_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("paper.id"), nullable=False
    )
    workflow_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("approval_workflow.id"), nullable=False
    )
    current_step_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("approval_workflow_step.id"), nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(50), default=WorkflowStatus.DRAFT, nullable=False
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    decisions: Mapped[list["ApprovalDecision"]] = relationship(
        "ApprovalDecision", back_populates="instance", lazy="selectin"
    )

    __table_args__ = (
        Index("ix_approval_instance_paper", "paper_id"),
        Index("ix_approval_instance_status", "status"),
    )


class ApprovalDecision(Base):
    """A decision made at a workflow step."""
    __tablename__ = "approval_decision"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    instance_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("approval_instance.id"), nullable=False
    )
    step_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("approval_workflow_step.id"), nullable=False
    )
    decided_by: Mapped[str] = mapped_column(
        String(255), nullable=False, doc="User ID of the person deciding"
    )
    decision: Mapped[str] = mapped_column(
        String(50), nullable=False, doc="approved, rejected, returned"
    )
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    decided_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    instance: Mapped["ApprovalInstance"] = relationship(
        "ApprovalInstance", back_populates="decisions"
    )


# ===================================================================
# Vote - Electronic voting on agenda items
# ===================================================================

class VoteType(StrEnum):
    OPEN = "open"           # Offene Abstimmung
    ROLL_CALL = "roll_call" # Namentliche Abstimmung
    SECRET = "secret"       # Geheime Abstimmung


class VoteResult(StrEnum):
    YES = "yes"
    NO = "no"
    ABSTAIN = "abstain"
    ABSENT = "absent"


class Vote(Base):
    """A vote on an agenda item."""
    __tablename__ = "vote"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    agenda_item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("agenda_item.id"), nullable=False
    )
    vote_type: Mapped[str] = mapped_column(
        String(50), default=VoteType.OPEN, nullable=False
    )
    subject: Mapped[str] = mapped_column(
        String(1024), nullable=False, doc="What is being voted on"
    )
    yes_count: Mapped[int] = mapped_column(Integer, default=0)
    no_count: Mapped[int] = mapped_column(Integer, default=0)
    abstain_count: Mapped[int] = mapped_column(Integer, default=0)
    absent_count: Mapped[int] = mapped_column(Integer, default=0)
    passed: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    result_text: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, doc="Textual description of the result"
    )
    created: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    individual_votes: Mapped[list["IndividualVote"]] = relationship(
        "IndividualVote", back_populates="vote", lazy="selectin"
    )

    __table_args__ = (
        Index("ix_vote_agenda_item", "agenda_item_id"),
    )


class IndividualVote(Base):
    """A single person's vote (for roll-call votes)."""
    __tablename__ = "individual_vote"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    vote_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("vote.id"), nullable=False
    )
    person_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("person.id"), nullable=False
    )
    result: Mapped[str] = mapped_column(
        String(50), nullable=False, doc="yes, no, abstain, absent"
    )
    delegation_to_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("person.id"), nullable=True,
        doc="Person who voted on behalf (Stellvertretung)"
    )

    vote: Mapped["Vote"] = relationship(
        "Vote", back_populates="individual_votes"
    )

    __table_args__ = (
        Index("ix_individual_vote_vote", "vote_id"),
        Index("ix_individual_vote_person", "person_id"),
    )


# ===================================================================
# FileVersion - Document versioning
# ===================================================================

class FileVersion(Base):
    """
    Tracks versions of files. Each edit creates a new version
    while keeping the original file reference intact.
    """
    __tablename__ = "file_version"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    file_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("file.id"), nullable=False
    )
    version_number: Mapped[int] = mapped_column(
        Integer, nullable=False, doc="Sequential version number"
    )
    storage_key: Mapped[str] = mapped_column(
        String(1024), nullable=False, doc="MinIO object key for this version"
    )
    file_name: Mapped[str] = mapped_column(
        String(512), nullable=False
    )
    mime_type: Mapped[str] = mapped_column(
        String(255), nullable=False
    )
    size: Mapped[int] = mapped_column(Integer, nullable=False)
    sha512_checksum: Mapped[Optional[str]] = mapped_column(
        String(128), nullable=True
    )
    change_note: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, doc="Description of what changed"
    )
    created_by: Mapped[str] = mapped_column(
        String(255), nullable=False, doc="User ID who created this version"
    )
    created: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (
        Index("ix_file_version_file", "file_id"),
        Index("ix_file_version_number", "file_id", "version_number", unique=True),
    )
