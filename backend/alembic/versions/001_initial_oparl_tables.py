"""Initial OParl tables - all 12 OParl 1.1 object types

Revision ID: 001
Revises:
Create Date: 2026-02-20 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ------------------------------------------------------------------ #
    # oparl_systems                                                        #
    # ------------------------------------------------------------------ #
    op.create_table(
        'oparl_systems',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('oparl_version', sa.String(64), nullable=False,
                  server_default='https://schema.oparl.org/1.1/'),
        sa.Column('name', sa.String(256), nullable=False),
        sa.Column('website', sa.String(1024), nullable=True),
        sa.Column('contact_email', sa.String(256), nullable=True),
        sa.Column('contact_name', sa.String(256), nullable=True),
        sa.Column('vendor', sa.String(512), nullable=True),
        sa.Column('product', sa.String(512), nullable=True),
        sa.Column('other_oparl_versions',
                  postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('created', sa.DateTime(), nullable=False),
        sa.Column('modified', sa.DateTime(), nullable=False),
    )

    # ------------------------------------------------------------------ #
    # locations  (created early – referenced by bodies, orgs, persons,   #
    #             meetings)                                               #
    # ------------------------------------------------------------------ #
    op.create_table(
        'locations',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('oparl_id', sa.String(512), unique=True, nullable=True),
        sa.Column('name', sa.String(512), nullable=True),
        sa.Column('short_name', sa.String(128), nullable=True),
        sa.Column('deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('keyword', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('web', sa.String(1024), nullable=True),
        sa.Column('license', sa.String(512), nullable=True),
        sa.Column('tenant_id', sa.String(36), nullable=False),
        sa.Column('body_id', sa.String(36), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('street_address', sa.String(512), nullable=True),
        sa.Column('room', sa.String(256), nullable=True),
        sa.Column('postal_code', sa.String(16), nullable=True),
        sa.Column('sub_locality', sa.String(256), nullable=True),
        sa.Column('locality', sa.String(256), nullable=True),
        sa.Column('geojson', postgresql.JSONB(), nullable=True),
        sa.Column('created', sa.DateTime(), nullable=False),
        sa.Column('modified', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_locations_tenant_id', 'locations', ['tenant_id'])

    # ------------------------------------------------------------------ #
    # bodies                                                              #
    # ------------------------------------------------------------------ #
    op.create_table(
        'bodies',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('oparl_id', sa.String(512), unique=True, nullable=True),
        sa.Column('name', sa.String(512), nullable=True),
        sa.Column('short_name', sa.String(128), nullable=True),
        sa.Column('deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('keyword', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('web', sa.String(1024), nullable=True),
        sa.Column('license', sa.String(512), nullable=True),
        sa.Column('tenant_id', sa.String(36), nullable=False),
        sa.Column('system_id', sa.String(36),
                  sa.ForeignKey('oparl_systems.id'), nullable=False),
        sa.Column('body_type', sa.String(128), nullable=True),
        sa.Column('classification', sa.String(256), nullable=True),
        sa.Column('equivalent_body',
                  postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('contact_email', sa.String(256), nullable=True),
        sa.Column('contact_name', sa.String(256), nullable=True),
        sa.Column('ags', sa.String(12), nullable=True),
        sa.Column('rgs', sa.String(12), nullable=True),
        sa.Column('created', sa.DateTime(), nullable=False),
        sa.Column('modified', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_bodies_tenant_id', 'bodies', ['tenant_id'])
    op.create_index('ix_bodies_tenant_ags', 'bodies', ['tenant_id', 'ags'])

    # Add FK from locations.body_id -> bodies.id
    op.create_foreign_key(
        'fk_locations_body_id', 'locations', 'bodies', ['body_id'], ['id']
    )

    # ------------------------------------------------------------------ #
    # legislative_terms                                                   #
    # ------------------------------------------------------------------ #
    op.create_table(
        'legislative_terms',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('oparl_id', sa.String(512), unique=True, nullable=True),
        sa.Column('name', sa.String(512), nullable=True),
        sa.Column('short_name', sa.String(128), nullable=True),
        sa.Column('deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('keyword', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('web', sa.String(1024), nullable=True),
        sa.Column('license', sa.String(512), nullable=True),
        sa.Column('tenant_id', sa.String(36), nullable=False),
        sa.Column('body_id', sa.String(36),
                  sa.ForeignKey('bodies.id'), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('created', sa.DateTime(), nullable=False),
        sa.Column('modified', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_legislative_terms_tenant_id',
                    'legislative_terms', ['tenant_id'])
    op.create_index('ix_legislative_terms_body_date',
                    'legislative_terms', ['body_id', 'start_date'])

    # ------------------------------------------------------------------ #
    # organizations                                                       #
    # ------------------------------------------------------------------ #
    op.create_table(
        'organizations',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('oparl_id', sa.String(512), unique=True, nullable=True),
        sa.Column('name', sa.String(512), nullable=True),
        sa.Column('short_name', sa.String(128), nullable=True),
        sa.Column('deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('keyword', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('web', sa.String(1024), nullable=True),
        sa.Column('license', sa.String(512), nullable=True),
        sa.Column('tenant_id', sa.String(36), nullable=False),
        sa.Column('body_id', sa.String(36),
                  sa.ForeignKey('bodies.id'), nullable=False),
        sa.Column('organization_type', sa.String(64), nullable=True),
        sa.Column('classification', sa.String(256), nullable=True),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('location_id', sa.String(36),
                  sa.ForeignKey('locations.id'), nullable=True),
        sa.Column('external_body_id', sa.String(36), nullable=True),
        sa.Column('created', sa.DateTime(), nullable=False),
        sa.Column('modified', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_organizations_tenant_id', 'organizations', ['tenant_id'])
    op.create_index('ix_organizations_name', 'organizations', ['name'])
    op.create_index('ix_org_body_type', 'organizations',
                    ['body_id', 'organization_type'])

    # ------------------------------------------------------------------ #
    # persons                                                             #
    # ------------------------------------------------------------------ #
    op.create_table(
        'persons',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('oparl_id', sa.String(512), unique=True, nullable=True),
        sa.Column('name', sa.String(512), nullable=True),
        sa.Column('short_name', sa.String(128), nullable=True),
        sa.Column('deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('keyword', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('web', sa.String(1024), nullable=True),
        sa.Column('license', sa.String(512), nullable=True),
        sa.Column('tenant_id', sa.String(36), nullable=False),
        sa.Column('body_id', sa.String(36),
                  sa.ForeignKey('bodies.id'), nullable=False),
        sa.Column('family_name', sa.String(256), nullable=True),
        sa.Column('given_name', sa.String(256), nullable=True),
        sa.Column('form_of_address', sa.String(64), nullable=True),
        sa.Column('affix', sa.String(64), nullable=True),
        sa.Column('title', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('gender', sa.String(32), nullable=True),
        sa.Column('phone', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('email', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('status', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('life', sa.Text(), nullable=True),
        sa.Column('life_source', sa.String(1024), nullable=True),
        sa.Column('location_id', sa.String(36),
                  sa.ForeignKey('locations.id'), nullable=True),
        sa.Column('created', sa.DateTime(), nullable=False),
        sa.Column('modified', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_persons_tenant_id', 'persons', ['tenant_id'])
    op.create_index('ix_persons_name', 'persons', ['name'])
    op.create_index('ix_persons_family_name', 'persons', ['family_name'])

    # ------------------------------------------------------------------ #
    # memberships                                                         #
    # ------------------------------------------------------------------ #
    op.create_table(
        'memberships',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('oparl_id', sa.String(512), unique=True, nullable=True),
        sa.Column('name', sa.String(512), nullable=True),
        sa.Column('short_name', sa.String(128), nullable=True),
        sa.Column('deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('keyword', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('web', sa.String(1024), nullable=True),
        sa.Column('license', sa.String(512), nullable=True),
        sa.Column('tenant_id', sa.String(36), nullable=False),
        sa.Column('person_id', sa.String(36),
                  sa.ForeignKey('persons.id'), nullable=False),
        sa.Column('organization_id', sa.String(36),
                  sa.ForeignKey('organizations.id'), nullable=False),
        sa.Column('role', sa.String(128), nullable=True),
        sa.Column('voting_right', sa.Boolean(),
                  nullable=False, server_default='true'),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('on_behalf_of_id', sa.String(36),
                  sa.ForeignKey('organizations.id'), nullable=True),
        sa.Column('created', sa.DateTime(), nullable=False),
        sa.Column('modified', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_memberships_tenant_id', 'memberships', ['tenant_id'])
    op.create_index('ix_membership_person_org', 'memberships',
                    ['person_id', 'organization_id'])

    # ------------------------------------------------------------------ #
    # files                                                               #
    # ------------------------------------------------------------------ #
    op.create_table(
        'files',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('oparl_id', sa.String(512), unique=True, nullable=True),
        sa.Column('name', sa.String(512), nullable=True),
        sa.Column('short_name', sa.String(128), nullable=True),
        sa.Column('deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('keyword', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('web', sa.String(1024), nullable=True),
        sa.Column('license', sa.String(512), nullable=True),
        sa.Column('tenant_id', sa.String(36), nullable=False),
        sa.Column('file_name', sa.String(512), nullable=True),
        sa.Column('mime_type', sa.String(128), nullable=True),
        sa.Column('size', sa.Integer(), nullable=True),
        sa.Column('sha512_checksum', sa.String(128), nullable=True),
        sa.Column('text', sa.Text(), nullable=True),
        sa.Column('access_url', sa.String(1024), nullable=True),
        sa.Column('download_url', sa.String(1024), nullable=True),
        sa.Column('external_service_url', sa.String(1024), nullable=True),
        sa.Column('master_file_id', sa.String(36),
                  sa.ForeignKey('files.id'), nullable=True),
        sa.Column('storage_path', sa.String(1024), nullable=True),
        sa.Column('created', sa.DateTime(), nullable=False),
        sa.Column('modified', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_files_tenant_id', 'files', ['tenant_id'])
    op.create_index('ix_file_mime', 'files', ['mime_type'])

    # ------------------------------------------------------------------ #
    # meetings                                                            #
    # ------------------------------------------------------------------ #
    op.create_table(
        'meetings',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('oparl_id', sa.String(512), unique=True, nullable=True),
        sa.Column('name', sa.String(512), nullable=True),
        sa.Column('short_name', sa.String(128), nullable=True),
        sa.Column('deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('keyword', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('web', sa.String(1024), nullable=True),
        sa.Column('license', sa.String(512), nullable=True),
        sa.Column('tenant_id', sa.String(36), nullable=False),
        sa.Column('body_id', sa.String(36),
                  sa.ForeignKey('bodies.id'), nullable=False),
        sa.Column('meeting_state', sa.String(32),
                  nullable=False, server_default='scheduled'),
        sa.Column('cancelled', sa.Boolean(),
                  nullable=False, server_default='false'),
        sa.Column('start', sa.DateTime(), nullable=True),
        sa.Column('end', sa.DateTime(), nullable=True),
        sa.Column('location_id', sa.String(36),
                  sa.ForeignKey('locations.id'), nullable=True),
        sa.Column('invitation_id', sa.String(36),
                  sa.ForeignKey('files.id'), nullable=True),
        sa.Column('results_protocol_id', sa.String(36),
                  sa.ForeignKey('files.id'), nullable=True),
        sa.Column('verbatim_protocol_id', sa.String(36),
                  sa.ForeignKey('files.id'), nullable=True),
        sa.Column('organization_id', sa.String(36),
                  sa.ForeignKey('organizations.id'), nullable=True),
        sa.Column('created', sa.DateTime(), nullable=False),
        sa.Column('modified', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_meetings_tenant_id', 'meetings', ['tenant_id'])
    op.create_index('ix_meeting_body_state', 'meetings',
                    ['body_id', 'meeting_state'])
    op.create_index('ix_meeting_start', 'meetings', ['start'])

    # ------------------------------------------------------------------ #
    # agenda_items                                                        #
    # ------------------------------------------------------------------ #
    op.create_table(
        'agenda_items',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('oparl_id', sa.String(512), unique=True, nullable=True),
        sa.Column('name', sa.String(512), nullable=True),
        sa.Column('short_name', sa.String(128), nullable=True),
        sa.Column('deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('keyword', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('web', sa.String(1024), nullable=True),
        sa.Column('license', sa.String(512), nullable=True),
        sa.Column('tenant_id', sa.String(36), nullable=False),
        sa.Column('meeting_id', sa.String(36),
                  sa.ForeignKey('meetings.id'), nullable=False),
        sa.Column('number', sa.String(32), nullable=True),
        sa.Column('order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('public', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('result', sa.Text(), nullable=True),
        sa.Column('resolution_text', sa.Text(), nullable=True),
        sa.Column('resolution_file_id', sa.String(36),
                  sa.ForeignKey('files.id'), nullable=True),
        sa.Column('start', sa.DateTime(), nullable=True),
        sa.Column('end', sa.DateTime(), nullable=True),
        sa.Column('created', sa.DateTime(), nullable=False),
        sa.Column('modified', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_agenda_items_tenant_id', 'agenda_items', ['tenant_id'])
    op.create_index('ix_agenda_items_meeting', 'agenda_items',
                    ['meeting_id', 'order'])

    # ------------------------------------------------------------------ #
    # papers                                                              #
    # ------------------------------------------------------------------ #
    op.create_table(
        'papers',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('oparl_id', sa.String(512), unique=True, nullable=True),
        sa.Column('name', sa.String(512), nullable=True),
        sa.Column('short_name', sa.String(128), nullable=True),
        sa.Column('deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('keyword', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('web', sa.String(1024), nullable=True),
        sa.Column('license', sa.String(512), nullable=True),
        sa.Column('tenant_id', sa.String(36), nullable=False),
        sa.Column('body_id', sa.String(36),
                  sa.ForeignKey('bodies.id'), nullable=False),
        sa.Column('reference', sa.String(128), nullable=True),
        sa.Column('date', sa.Date(), nullable=True),
        sa.Column('paper_type', sa.String(128), nullable=True),
        sa.Column('main_file_id', sa.String(36),
                  sa.ForeignKey('files.id'), nullable=True),
        sa.Column('created', sa.DateTime(), nullable=False),
        sa.Column('modified', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_papers_tenant_id', 'papers', ['tenant_id'])
    op.create_index('ix_paper_body_ref', 'papers', ['body_id', 'reference'])
    op.create_index('ix_paper_date', 'papers', ['date'])
    op.create_index('ix_paper_name', 'papers', ['name'])

    # ------------------------------------------------------------------ #
    # consultations                                                       #
    # ------------------------------------------------------------------ #
    op.create_table(
        'consultations',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('oparl_id', sa.String(512), unique=True, nullable=True),
        sa.Column('name', sa.String(512), nullable=True),
        sa.Column('short_name', sa.String(128), nullable=True),
        sa.Column('deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('keyword', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('web', sa.String(1024), nullable=True),
        sa.Column('license', sa.String(512), nullable=True),
        sa.Column('tenant_id', sa.String(36), nullable=False),
        sa.Column('paper_id', sa.String(36),
                  sa.ForeignKey('papers.id'), nullable=False),
        sa.Column('agenda_item_id', sa.String(36),
                  sa.ForeignKey('agenda_items.id'), nullable=True),
        sa.Column('organization_id', sa.String(36),
                  sa.ForeignKey('organizations.id'), nullable=True),
        sa.Column('authoritative', sa.Boolean(),
                  nullable=False, server_default='false'),
        sa.Column('role', sa.String(128), nullable=True),
        sa.Column('created', sa.DateTime(), nullable=False),
        sa.Column('modified', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_consultations_tenant_id', 'consultations', ['tenant_id'])
    op.create_index('ix_consultations_paper', 'consultations', ['paper_id'])

    # ------------------------------------------------------------------ #
    # Association tables (M:N)                                            #
    # ------------------------------------------------------------------ #
    op.create_table(
        'paper_originator_person',
        sa.Column('paper_id', sa.String(36), sa.ForeignKey('papers.id')),
        sa.Column('person_id', sa.String(36), sa.ForeignKey('persons.id')),
    )
    op.create_index('ix_pop_paper', 'paper_originator_person', ['paper_id'])

    op.create_table(
        'paper_originator_org',
        sa.Column('paper_id', sa.String(36), sa.ForeignKey('papers.id')),
        sa.Column('organization_id', sa.String(36),
                  sa.ForeignKey('organizations.id')),
    )
    op.create_index('ix_poo_paper', 'paper_originator_org', ['paper_id'])

    op.create_table(
        'meeting_participant',
        sa.Column('meeting_id', sa.String(36), sa.ForeignKey('meetings.id')),
        sa.Column('person_id', sa.String(36), sa.ForeignKey('persons.id')),
    )
    op.create_index('ix_mp_meeting', 'meeting_participant', ['meeting_id'])

    op.create_table(
        'paper_file',
        sa.Column('paper_id', sa.String(36), sa.ForeignKey('papers.id')),
        sa.Column('file_id', sa.String(36), sa.ForeignKey('files.id')),
    )
    op.create_index('ix_pf_paper', 'paper_file', ['paper_id'])

    # ------------------------------------------------------------------ #
    # GIN indexes for JSONB fields                                        #
    # ------------------------------------------------------------------ #
    op.execute(
        "CREATE INDEX ix_locations_geojson_gin ON locations USING gin (geojson)"
    )


def downgrade() -> None:
    # Drop in reverse dependency order
    op.execute("DROP INDEX IF EXISTS ix_locations_geojson_gin")

    op.drop_table('paper_file')
    op.drop_table('meeting_participant')
    op.drop_table('paper_originator_org')
    op.drop_table('paper_originator_person')
    op.drop_table('consultations')
    op.drop_table('papers')
    op.drop_table('agenda_items')
    op.drop_table('meetings')
    op.drop_table('files')
    op.drop_table('memberships')
    op.drop_table('persons')
    op.drop_table('organizations')
    op.drop_table('legislative_terms')

    # Remove FK before dropping bodies
    op.drop_constraint('fk_locations_body_id', 'locations', type_='foreignkey')
    op.drop_table('bodies')
    op.drop_table('locations')
    op.drop_table('oparl_systems')
