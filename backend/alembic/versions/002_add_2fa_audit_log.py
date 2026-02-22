"""Add 2FA and Audit Log tables

Revision ID: add_2fa_audit_log
Revises: initial
Create Date: 2026-02-22

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_2fa_audit_log'
down_revision: Union[str, None] = 'initial'
branch_labels: Union[str, None] = None
depends_on: Union[str, None] = None


def upgrade() -> None:
    # Добавляем 2FA поля в users
    op.add_column('users', sa.Column('two_factor_enabled', sa.Boolean(), nullable=True, default=False))
    op.add_column('users', sa.Column('two_factor_secret', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('two_factor_verified', sa.Boolean(), nullable=True, default=False))
    op.add_column('users', sa.Column('backup_codes', sa.String(length=500), nullable=True))
    op.add_column('users', sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.func.now()))
    op.add_column('users', sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=sa.func.now()))
    
    # Создаем таблицу audit_logs
    op.create_table('audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('entity_type', sa.String(length=50), nullable=False),
        sa.Column('entity_id', sa.Integer(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('old_values', sa.JSON(), nullable=True),
        sa.Column('new_values', sa.JSON(), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True, server_default='success'),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_audit_logs_action'), 'audit_logs', ['action'], unique=False)
    op.create_index(op.f('ix_audit_logs_entity_type'), 'audit_logs', ['entity_type'], unique=False)
    op.create_index(op.f('ix_audit_logs_user_id'), 'audit_logs', ['user_id'], unique=False)
    op.create_index(op.f('ix_audit_logs_created_at'), 'audit_logs', ['created_at'], unique=False)


def downgrade() -> None:
    # Удаляем audit_logs
    op.drop_index(op.f('ix_audit_logs_created_at'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_user_id'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_entity_type'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_action'), table_name='audit_logs')
    op.drop_table('audit_logs')
    
    # Удаляем 2FA поля
    op.drop_column('users', 'updated_at')
    op.drop_column('users', 'created_at')
    op.drop_column('users', 'backup_codes')
    op.drop_column('users', 'two_factor_verified')
    op.drop_column('users', 'two_factor_secret')
    op.drop_column('users', 'two_factor_enabled')
