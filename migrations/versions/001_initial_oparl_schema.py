"""001 initial oparl schema

Revision ID: 001_initial
Revises:
Create Date: 2026-02-19

Creates all tables for the OParl 1.1 data model plus aitema extensions.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB


revision = "001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- Tenant (public schema) ---
    op.create_table(
        "tenant",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("slug", sa.String(100), unique=True, nullable=False, index=True),
        sa.Column("name", sa.String(512), nullable=False),
        sa.Column("ags", sa.String(12), unique=True, nullable=True),
        sa.Column("domain", sa.String(255), unique=True, nullable=True),
        sa.Column("config", JSONB, nullable=False, server_default="{}"),
        sa.Column("keycloak_realm", sa.String(255), nullable=True),
        sa.Column("is_active", sa.Boolean, default=True),
        sa.Column("is_trial", sa.Boolean, default=False),
        sa.Column("contact_email", sa.String(255), nullable=True),
        sa.Column("contact_name", sa.String(255), nullable=True),
        sa.Column("contact_phone", sa.String(100), nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("schema_created", sa.Boolean, default=False),
        sa.Column("created", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("modified", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # --- OParl: Location (referenced by many, must be created first) ---
    op.create_table(
        "location",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("oparl_type", sa.String(255), nullable=False),
        sa.Column("created", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("modified", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted", sa.Boolean, default=False),
        sa.Column("keyword", ARRAY(sa.String), nullable=True),
        sa.Column("web", sa.String(2048), nullable=True),
        sa.Column("license", sa.String(2048), nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("street_address", sa.String(512), nullable=True),
        sa.Column("room", sa.String(255), nullable=True),
        sa.Column("postal_code", sa.String(20), nullable=True),
        sa.Column("locality", sa.String(255), nullable=True),
        sa.Column("sub_locality", sa.String(255), nullable=True),
        sa.Column("geojson", JSONB, nullable=True),
        sa.Column("paper_id", UUID(as_uuid=True), nullable=True),
    )

    # --- OParl: System ---
    op.create_table(
        "system",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("oparl_type", sa.String(255), nullable=False),
        sa.Column("created", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("modified", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted", sa.Boolean, default=False),
        sa.Column("keyword", ARRAY(sa.String), nullable=True),
        sa.Column("web", sa.String(2048), nullable=True),
        sa.Column("license", sa.String(2048), nullable=True),
        sa.Column("oparl_version", sa.String(255), nullable=False),
        sa.Column("name", sa.String(512), nullable=True),
        sa.Column("contact_email", sa.String(255), nullable=True),
        sa.Column("contact_name", sa.String(255), nullable=True),
        sa.Column("website", sa.String(2048), nullable=True),
        sa.Column("vendor", sa.String(2048), nullable=True),
        sa.Column("product", sa.String(2048), nullable=True),
        sa.Column("other_oparl_versions", ARRAY(sa.String), nullable=True),
    )

    # --- OParl: File ---
    op.create_table(
        "file",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("oparl_type", sa.String(255), nullable=False),
        sa.Column("created", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("modified", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted", sa.Boolean, default=False),
        sa.Column("keyword", ARRAY(sa.String), nullable=True),
        sa.Column("web", sa.String(2048), nullable=True),
        sa.Column("license", sa.String(2048), nullable=True),
        sa.Column("name", sa.String(1024), nullable=True),
        sa.Column("file_name", sa.String(512), nullable=True),
        sa.Column("mime_type", sa.String(255), nullable=True),
        sa.Column("date", sa.Date, nullable=True),
        sa.Column("size", sa.Integer, nullable=True),
        sa.Column("sha1_checksum", sa.String(40), nullable=True),
        sa.Column("sha512_checksum", sa.String(128), nullable=True),
        sa.Column("text", sa.Text, nullable=True),
        sa.Column("access_url", sa.String(2048), nullable=True),
        sa.Column("external_service_url", sa.String(2048), nullable=True),
        sa.Column("download_url", sa.String(2048), nullable=True),
        sa.Column("file_license", sa.String(2048), nullable=True),
        sa.Column("storage_key", sa.String(1024), nullable=True),
    )

    # --- OParl: Body ---
    op.create_table(
        "body",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("oparl_type", sa.String(255), nullable=False),
        sa.Column("created", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("modified", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted", sa.Boolean, default=False),
        sa.Column("keyword", ARRAY(sa.String), nullable=True),
        sa.Column("web", sa.String(2048), nullable=True),
        sa.Column("license", sa.String(2048), nullable=True),
        sa.Column("system_id", UUID(as_uuid=True), sa.ForeignKey("system.id"), nullable=False),
        sa.Column("location_id", UUID(as_uuid=True), sa.ForeignKey("location.id"), nullable=True),
        sa.Column("name", sa.String(512), nullable=False),
        sa.Column("short_name", sa.String(255), nullable=True),
        sa.Column("website", sa.String(2048), nullable=True),
        sa.Column("ags", sa.String(12), nullable=True),
        sa.Column("rgs", sa.String(16), nullable=True),
        sa.Column("equivalent", ARRAY(sa.String), nullable=True),
        sa.Column("contact_email", sa.String(255), nullable=True),
        sa.Column("contact_name", sa.String(255), nullable=True),
        sa.Column("classification", sa.String(255), nullable=True),
    )

    # --- OParl: LegislativeTerm ---
    op.create_table(
        "legislative_term",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("oparl_type", sa.String(255), nullable=False),
        sa.Column("created", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("modified", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted", sa.Boolean, default=False),
        sa.Column("keyword", ARRAY(sa.String), nullable=True),
        sa.Column("web", sa.String(2048), nullable=True),
        sa.Column("license", sa.String(2048), nullable=True),
        sa.Column("body_id", UUID(as_uuid=True), sa.ForeignKey("body.id"), nullable=False),
        sa.Column("name", sa.String(512), nullable=True),
        sa.Column("start_date", sa.Date, nullable=True),
        sa.Column("end_date", sa.Date, nullable=True),
    )

    # --- OParl: Organization ---
    op.create_table(
        "organization",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("oparl_type", sa.String(255), nullable=False),
        sa.Column("created", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("modified", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted", sa.Boolean, default=False),
        sa.Column("keyword", ARRAY(sa.String), nullable=True),
        sa.Column("web", sa.String(2048), nullable=True),
        sa.Column("license", sa.String(2048), nullable=True),
        sa.Column("body_id", UUID(as_uuid=True), sa.ForeignKey("body.id"), nullable=False),
        sa.Column("location_id", UUID(as_uuid=True), sa.ForeignKey("location.id"), nullable=True),
        sa.Column("name", sa.String(512), nullable=False),
        sa.Column("short_name", sa.String(255), nullable=True),
        sa.Column("organization_type", sa.String(255), nullable=True),
        sa.Column("post", ARRAY(sa.String), nullable=True),
        sa.Column("start_date", sa.Date, nullable=True),
        sa.Column("end_date", sa.Date, nullable=True),
        sa.Column("external_body", sa.String(2048), nullable=True),
        sa.Column("website", sa.String(2048), nullable=True),
        sa.Column("classification", sa.String(255), nullable=True),
    )

    # --- OParl: Person ---
    op.create_table(
        "person",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("oparl_type", sa.String(255), nullable=False),
        sa.Column("created", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("modified", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted", sa.Boolean, default=False),
        sa.Column("keyword", ARRAY(sa.String), nullable=True),
        sa.Column("web", sa.String(2048), nullable=True),
        sa.Column("license", sa.String(2048), nullable=True),
        sa.Column("body_id", UUID(as_uuid=True), sa.ForeignKey("body.id"), nullable=False),
        sa.Column("location_id", UUID(as_uuid=True), sa.ForeignKey("location.id"), nullable=True),
        sa.Column("name", sa.String(512), nullable=False),
        sa.Column("family_name", sa.String(255), nullable=True),
        sa.Column("given_name", sa.String(255), nullable=True),
        sa.Column("form_of_address", sa.String(100), nullable=True),
        sa.Column("affix", sa.String(100), nullable=True),
        sa.Column("title", ARRAY(sa.String), nullable=True),
        sa.Column("gender", sa.String(50), nullable=True),
        sa.Column("phone", ARRAY(sa.String), nullable=True),
        sa.Column("email", ARRAY(sa.String), nullable=True),
        sa.Column("street_address", sa.String(512), nullable=True),
        sa.Column("postal_code", sa.String(20), nullable=True),
        sa.Column("locality", sa.String(255), nullable=True),
        sa.Column("status", ARRAY(sa.String), nullable=True),
        sa.Column("life", sa.Text, nullable=True),
        sa.Column("life_source", sa.String(2048), nullable=True),
    )

    # --- OParl: Membership ---
    op.create_table(
        "membership",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("oparl_type", sa.String(255), nullable=False),
        sa.Column("created", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("modified", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted", sa.Boolean, default=False),
        sa.Column("keyword", ARRAY(sa.String), nullable=True),
        sa.Column("web", sa.String(2048), nullable=True),
        sa.Column("license", sa.String(2048), nullable=True),
        sa.Column("person_id", UUID(as_uuid=True), sa.ForeignKey("person.id"), nullable=False),
        sa.Column("organization_id", UUID(as_uuid=True), sa.ForeignKey("organization.id"), nullable=False),
        sa.Column("on_behalf_of_id", UUID(as_uuid=True), sa.ForeignKey("organization.id"), nullable=True),
        sa.Column("role", sa.String(255), nullable=True),
        sa.Column("voting_right", sa.Boolean, nullable=True),
        sa.Column("start_date", sa.Date, nullable=True),
        sa.Column("end_date", sa.Date, nullable=True),
    )

    # --- OParl: Paper ---
    op.create_table(
        "paper",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("oparl_type", sa.String(255), nullable=False),
        sa.Column("created", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("modified", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted", sa.Boolean, default=False),
        sa.Column("keyword", ARRAY(sa.String), nullable=True),
        sa.Column("web", sa.String(2048), nullable=True),
        sa.Column("license", sa.String(2048), nullable=True),
        sa.Column("body_id", UUID(as_uuid=True), sa.ForeignKey("body.id"), nullable=False),
        sa.Column("main_file_id", UUID(as_uuid=True), sa.ForeignKey("file.id"), nullable=True),
        sa.Column("name", sa.String(1024), nullable=False),
        sa.Column("reference", sa.String(100), nullable=True),
        sa.Column("date", sa.Date, nullable=True),
        sa.Column("paper_type", sa.String(255), nullable=True),
    )

    # Add FK from location to paper (after paper exists)
    op.create_foreign_key("fk_location_paper", "location", "paper", ["paper_id"], ["id"])

    # --- OParl: Consultation ---
    op.create_table(
        "consultation",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("oparl_type", sa.String(255), nullable=False),
        sa.Column("created", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("modified", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted", sa.Boolean, default=False),
        sa.Column("keyword", ARRAY(sa.String), nullable=True),
        sa.Column("web", sa.String(2048), nullable=True),
        sa.Column("license", sa.String(2048), nullable=True),
        sa.Column("paper_id", UUID(as_uuid=True), sa.ForeignKey("paper.id"), nullable=False),
        sa.Column("meeting_id", UUID(as_uuid=True), nullable=True),
        sa.Column("authoritative", sa.Boolean, nullable=True),
        sa.Column("role", sa.String(255), nullable=True),
    )

    # --- OParl: Meeting ---
    op.create_table(
        "meeting",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("oparl_type", sa.String(255), nullable=False),
        sa.Column("created", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("modified", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted", sa.Boolean, default=False),
        sa.Column("keyword", ARRAY(sa.String), nullable=True),
        sa.Column("web", sa.String(2048), nullable=True),
        sa.Column("license", sa.String(2048), nullable=True),
        sa.Column("body_id", UUID(as_uuid=True), sa.ForeignKey("body.id"), nullable=False),
        sa.Column("location_id", UUID(as_uuid=True), sa.ForeignKey("location.id"), nullable=True),
        sa.Column("invitation_id", UUID(as_uuid=True), sa.ForeignKey("file.id"), nullable=True),
        sa.Column("results_protocol_id", UUID(as_uuid=True), sa.ForeignKey("file.id"), nullable=True),
        sa.Column("verbatim_protocol_id", UUID(as_uuid=True), sa.ForeignKey("file.id"), nullable=True),
        sa.Column("name", sa.String(512), nullable=True),
        sa.Column("meeting_state", sa.String(100), nullable=True),
        sa.Column("cancelled", sa.Boolean, default=False),
        sa.Column("start", sa.DateTime(timezone=True), nullable=True),
        sa.Column("end", sa.DateTime(timezone=True), nullable=True),
    )

    # Add FK from consultation.meeting_id to meeting
    op.create_foreign_key("fk_consultation_meeting", "consultation", "meeting", ["meeting_id"], ["id"])

    # --- OParl: AgendaItem ---
    op.create_table(
        "agenda_item",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("oparl_type", sa.String(255), nullable=False),
        sa.Column("created", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("modified", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted", sa.Boolean, default=False),
        sa.Column("keyword", ARRAY(sa.String), nullable=True),
        sa.Column("web", sa.String(2048), nullable=True),
        sa.Column("license", sa.String(2048), nullable=True),
        sa.Column("meeting_id", UUID(as_uuid=True), sa.ForeignKey("meeting.id"), nullable=False),
        sa.Column("consultation_id", UUID(as_uuid=True), sa.ForeignKey("consultation.id"), nullable=True),
        sa.Column("result_file_id", UUID(as_uuid=True), sa.ForeignKey("file.id"), nullable=True),
        sa.Column("number", sa.String(50), nullable=True),
        sa.Column("name", sa.String(1024), nullable=False),
        sa.Column("public", sa.Boolean, default=True),
        sa.Column("result", sa.Text, nullable=True),
        sa.Column("resolution_text", sa.Text, nullable=True),
        sa.Column("start", sa.DateTime(timezone=True), nullable=True),
        sa.Column("end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("order", sa.Integer, default=0),
    )

    # --- Association Tables ---
    for table_name, col1, fk1, col2, fk2 in [
        ("meeting_organization", "meeting_id", "meeting.id", "organization_id", "organization.id"),
        ("meeting_participant", "meeting_id", "meeting.id", "person_id", "person.id"),
        ("meeting_auxiliary_file", "meeting_id", "meeting.id", "file_id", "file.id"),
        ("paper_originator_person", "paper_id", "paper.id", "person_id", "person.id"),
        ("paper_originator_organization", "paper_id", "paper.id", "organization_id", "organization.id"),
        ("paper_under_direction_organization", "paper_id", "paper.id", "organization_id", "organization.id"),
        ("paper_auxiliary_file", "paper_id", "paper.id", "file_id", "file.id"),
        ("agenda_item_auxiliary_file", "agenda_item_id", "agenda_item.id", "file_id", "file.id"),
        ("consultation_organization", "consultation_id", "consultation.id", "organization_id", "organization.id"),
    ]:
        op.create_table(
            table_name,
            sa.Column(col1, UUID(as_uuid=True), sa.ForeignKey(fk1, ondelete="CASCADE"), primary_key=True),
            sa.Column(col2, UUID(as_uuid=True), sa.ForeignKey(fk2, ondelete="CASCADE"), primary_key=True),
        )

    # --- Extension: ApprovalWorkflow ---
    op.create_table(
        "approval_workflow",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(512), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("is_active", sa.Boolean, default=True),
        sa.Column("created", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "approval_workflow_step",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("workflow_id", UUID(as_uuid=True), sa.ForeignKey("approval_workflow.id"), nullable=False),
        sa.Column("name", sa.String(512), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("order", sa.Integer, nullable=False),
        sa.Column("required_role", sa.String(100), nullable=True),
        sa.Column("required_organization_id", UUID(as_uuid=True), sa.ForeignKey("organization.id"), nullable=True),
        sa.Column("auto_advance", sa.Boolean, default=False),
    )

    # --- Extension: Template ---
    op.create_table(
        "template",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(512), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("paper_type", sa.String(255), nullable=False),
        sa.Column("content_schema", JSONB, nullable=False, server_default="{}"),
        sa.Column("default_workflow_id", UUID(as_uuid=True), sa.ForeignKey("approval_workflow.id"), nullable=True),
        sa.Column("is_active", sa.Boolean, default=True),
        sa.Column("created", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("modified", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # --- Extension: ApprovalInstance ---
    op.create_table(
        "approval_instance",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("paper_id", UUID(as_uuid=True), sa.ForeignKey("paper.id"), nullable=False),
        sa.Column("workflow_id", UUID(as_uuid=True), sa.ForeignKey("approval_workflow.id"), nullable=False),
        sa.Column("current_step_id", UUID(as_uuid=True), sa.ForeignKey("approval_workflow_step.id"), nullable=True),
        sa.Column("status", sa.String(50), default="draft"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "approval_decision",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("instance_id", UUID(as_uuid=True), sa.ForeignKey("approval_instance.id"), nullable=False),
        sa.Column("step_id", UUID(as_uuid=True), sa.ForeignKey("approval_workflow_step.id"), nullable=False),
        sa.Column("decided_by", sa.String(255), nullable=False),
        sa.Column("decision", sa.String(50), nullable=False),
        sa.Column("comment", sa.Text, nullable=True),
        sa.Column("decided_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # --- Extension: Vote ---
    op.create_table(
        "vote",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("agenda_item_id", UUID(as_uuid=True), sa.ForeignKey("agenda_item.id"), nullable=False),
        sa.Column("vote_type", sa.String(50), default="open"),
        sa.Column("subject", sa.String(1024), nullable=False),
        sa.Column("yes_count", sa.Integer, default=0),
        sa.Column("no_count", sa.Integer, default=0),
        sa.Column("abstain_count", sa.Integer, default=0),
        sa.Column("absent_count", sa.Integer, default=0),
        sa.Column("passed", sa.Boolean, nullable=True),
        sa.Column("result_text", sa.Text, nullable=True),
        sa.Column("created", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "individual_vote",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("vote_id", UUID(as_uuid=True), sa.ForeignKey("vote.id"), nullable=False),
        sa.Column("person_id", UUID(as_uuid=True), sa.ForeignKey("person.id"), nullable=False),
        sa.Column("result", sa.String(50), nullable=False),
        sa.Column("delegation_to_id", UUID(as_uuid=True), sa.ForeignKey("person.id"), nullable=True),
    )

    # --- Extension: FileVersion ---
    op.create_table(
        "file_version",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("file_id", UUID(as_uuid=True), sa.ForeignKey("file.id"), nullable=False),
        sa.Column("version_number", sa.Integer, nullable=False),
        sa.Column("storage_key", sa.String(1024), nullable=False),
        sa.Column("file_name", sa.String(512), nullable=False),
        sa.Column("mime_type", sa.String(255), nullable=False),
        sa.Column("size", sa.Integer, nullable=False),
        sa.Column("sha512_checksum", sa.String(128), nullable=True),
        sa.Column("change_note", sa.Text, nullable=True),
        sa.Column("created_by", sa.String(255), nullable=False),
        sa.Column("created", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    tables = [
        "file_version", "individual_vote", "vote",
        "approval_decision", "approval_instance", "template",
        "approval_workflow_step", "approval_workflow",
        "consultation_organization", "agenda_item_auxiliary_file",
        "paper_auxiliary_file", "paper_under_direction_organization",
        "paper_originator_organization", "paper_originator_person",
        "meeting_auxiliary_file", "meeting_participant", "meeting_organization",
        "agenda_item", "meeting", "consultation", "paper",
        "membership", "person", "organization", "legislative_term",
        "body", "file", "system", "location", "tenant",
    ]
    for table in tables:
        op.drop_table(table)
