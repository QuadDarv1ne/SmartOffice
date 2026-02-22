"""Add task comments, activity feed, calendar and more features

Revision ID: add_advanced_features
Revises: add_2fa_audit_log
Create Date: 2026-02-22

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_advanced_features'
down_revision: Union[str, None] = 'add_2fa_audit_log'
branch_labels: Union[str, None] = None
depends_on: Union[str, None] = None


def upgrade() -> None:
    # Создаем таблицу task_comments
    op.create_table('task_comments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('task_id', sa.Integer(), nullable=False),
        sa.Column('author_id', sa.Integer(), nullable=False),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('is_edited', sa.Boolean(), nullable=True, default=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=True, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.task_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['author_id'], ['users.id']),
        sa.ForeignKeyConstraint(['parent_id'], ['task_comments.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_task_comments_task_id'), 'task_comments', ['task_id'], unique=False)
    op.create_index(op.f('ix_task_comments_author_id'), 'task_comments', ['author_id'], unique=False)
    op.create_index(op.f('ix_task_comments_parent_id'), 'task_comments', ['parent_id'], unique=False)
    op.create_index(op.f('ix_task_comments_created_at'), 'task_comments', ['created_at'], unique=False)
    
    # Создаем таблицу activity_feed
    op.create_table('activity_feed',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('action_type', sa.String(length=50), nullable=False),
        sa.Column('entity_type', sa.String(length=50), nullable=False),
        sa.Column('entity_id', sa.Integer(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_activity_feed_user_id'), 'activity_feed', ['user_id'], unique=False)
    op.create_index(op.f('ix_activity_feed_action_type'), 'activity_feed', ['action_type'], unique=False)
    op.create_index(op.f('ix_activity_feed_created_at'), 'activity_feed', ['created_at'], unique=False)
    
    # Создаем таблицу events (календарь)
    op.create_table('events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('event_type', sa.String(length=50), nullable=False),  # meeting, vacation, deadline, etc.
        sa.Column('start_date', sa.DateTime(), nullable=False),
        sa.Column('end_date', sa.DateTime(), nullable=True),
        sa.Column('all_day', sa.Boolean(), nullable=True, default=False),
        sa.Column('location', sa.String(length=200), nullable=True),
        sa.Column('organizer_id', sa.Integer(), nullable=True),
        sa.Column('is_recurring', sa.Boolean(), nullable=True, default=False),
        sa.Column('recurrence_pattern', sa.String(length=50), nullable=True),  # daily, weekly, monthly
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['organizer_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_events_event_type'), 'events', ['event_type'], unique=False)
    op.create_index(op.f('ix_events_start_date'), 'events', ['start_date'], unique=False)
    
    # Создаем таблицу event_participants (участники событий)
    op.create_table('event_participants',
        sa.Column('event_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=True, default='pending'),  # pending, accepted, declined
        sa.PrimaryKeyConstraint('event_id', 'user_id'),
        sa.ForeignKeyConstraint(['event_id'], ['events.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
    )


def downgrade() -> None:
    # Удаляем таблицы в обратном порядке
    op.drop_table('event_participants')
    op.drop_index(op.f('ix_events_start_date'), table_name='events')
    op.drop_index(op.f('ix_events_event_type'), table_name='events')
    op.drop_table('events')
    
    op.drop_index(op.f('ix_activity_feed_created_at'), table_name='activity_feed')
    op.drop_index(op.f('ix_activity_feed_action_type'), table_name='activity_feed')
    op.drop_index(op.f('ix_activity_feed_user_id'), table_name='activity_feed')
    op.drop_table('activity_feed')
    
    op.drop_index(op.f('ix_task_comments_created_at'), table_name='task_comments')
    op.drop_index(op.f('ix_task_comments_parent_id'), table_name='task_comments')
    op.drop_index(op.f('ix_task_comments_author_id'), table_name='task_comments')
    op.drop_index(op.f('ix_task_comments_task_id'), table_name='task_comments')
    op.drop_table('task_comments')
