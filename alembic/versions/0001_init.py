"""init schema"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '0001_init'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('users', sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True), sa.Column('created_at', sa.DateTime(), nullable=False))
    op.create_table('skills', sa.Column('id', sa.Integer(), primary_key=True), sa.Column('canonical_name', sa.String(255), unique=True), sa.Column('taxonomy', sa.String(50)), sa.Column('external_id', sa.String(255)), sa.Column('aliases', postgresql.ARRAY(sa.String()), nullable=False))
    op.create_table('roles', sa.Column('id', sa.Integer(), primary_key=True), sa.Column('name', sa.String(255)), sa.Column('family', sa.String(100)), sa.Column('level', sa.String(100)), sa.Column('description', sa.Text()))
    op.create_table('profiles', sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True), sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False), sa.Column('raw_resume_text', sa.Text()), sa.Column('parsed_json', sa.JSON()), sa.Column('version', sa.Integer(), nullable=False), sa.Column('created_at', sa.DateTime(), nullable=False))
    op.create_table('role_requirements', sa.Column('id', sa.Integer(), primary_key=True), sa.Column('role_id', sa.Integer(), sa.ForeignKey('roles.id'), nullable=False), sa.Column('skill_id', sa.Integer(), sa.ForeignKey('skills.id'), nullable=False), sa.Column('required_level', sa.Float(), nullable=False), sa.Column('weight', sa.Float(), nullable=False), sa.Column('must_have', sa.Boolean(), nullable=False))
    op.create_table('plans', sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True), sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False), sa.Column('profile_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('profiles.id'), nullable=False), sa.Column('target_role_id', sa.Integer(), sa.ForeignKey('roles.id'), nullable=False), sa.Column('params_json', sa.JSON()), sa.Column('plan_json', sa.JSON()), sa.Column('progress_json', sa.JSON()), sa.Column('created_at', sa.DateTime(), nullable=False))
    op.create_table('learning_items', sa.Column('id', sa.Integer(), primary_key=True), sa.Column('title', sa.String(255), nullable=False), sa.Column('provider', sa.String(255)), sa.Column('url', sa.String(500), nullable=False), sa.Column('skill_tags', postgresql.ARRAY(sa.String()), nullable=False), sa.Column('level', sa.String(50)), sa.Column('duration', sa.String(50)), sa.Column('language', sa.String(50)), sa.Column('price_type', sa.String(50)), sa.Column('content_text', sa.Text(), nullable=False))
    op.create_table('user_skills', sa.Column('id', sa.Integer(), primary_key=True), sa.Column('profile_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('profiles.id'), nullable=False), sa.Column('skill_id', sa.Integer(), sa.ForeignKey('skills.id')), sa.Column('raw_name', sa.String(255), nullable=False), sa.Column('level_estimate', sa.Float(), nullable=False), sa.Column('confidence', sa.Float(), nullable=False), sa.Column('evidence', postgresql.ARRAY(sa.String()), nullable=False))
    op.create_table('recommendations', sa.Column('id', sa.Integer(), primary_key=True), sa.Column('plan_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('plans.id'), nullable=False), sa.Column('learning_item_id', sa.Integer(), sa.ForeignKey('learning_items.id'), nullable=False), sa.Column('rank', sa.Integer(), nullable=False), sa.Column('rationale', sa.Text(), nullable=False), sa.Column('confidence', sa.Float(), nullable=False), sa.Column('citations', sa.JSON(), nullable=False))
    op.create_table('jobs', sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True), sa.Column('type', sa.String(100), nullable=False), sa.Column('status', sa.String(20), nullable=False), sa.Column('progress', sa.Float(), nullable=False), sa.Column('error', sa.Text()), sa.Column('created_at', sa.DateTime(), nullable=False), sa.Column('updated_at', sa.DateTime(), nullable=False), sa.Column('result_ref', sa.String(255)))


def downgrade() -> None:
    for table in ['jobs', 'recommendations', 'user_skills', 'learning_items', 'plans', 'role_requirements', 'profiles', 'roles', 'skills', 'users']:
        op.drop_table(table)
