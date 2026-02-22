"""Initial database schema

Revision ID: initial
Revises: 
Create Date: 2026-02-22

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, None] = None
depends_on: Union[str, None] = None


def upgrade() -> None:
    # Users table
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('is_admin', sa.Boolean(), nullable=True, default=False),
        sa.Column('employee_id', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)

    # Departments table
    op.create_table('departments',
        sa.Column('department_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('manager_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('department_id'),
        sa.UniqueConstraint('name'),
    )

    # Positions table
    op.create_table('positions',
        sa.Column('position_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=100), nullable=False),
        sa.Column('min_salary', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('max_salary', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.PrimaryKeyConstraint('position_id'),
        sa.UniqueConstraint('title'),
    )

    # Employees table
    op.create_table('employees',
        sa.Column('employee_id', sa.Integer(), nullable=False),
        sa.Column('personnel_number', sa.String(length=20), nullable=True),
        sa.Column('full_name', sa.String(length=150), nullable=False),
        sa.Column('birth_date', sa.Date(), nullable=True),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('email', sa.String(length=100), nullable=True),
        sa.Column('hire_date', sa.Date(), nullable=False),
        sa.Column('termination_date', sa.Date(), nullable=True),
        sa.Column('department_id', sa.Integer(), nullable=False),
        sa.Column('position_id', sa.Integer(), nullable=False),
        sa.Column('manager_id', sa.Integer(), nullable=True),
        sa.Column('schedule_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('employee_id'),
        sa.UniqueConstraint('personnel_number'),
        sa.UniqueConstraint('email'),
        sa.ForeignKeyConstraint(['department_id'], ['departments.department_id'], ),
        sa.ForeignKeyConstraint(['manager_id'], ['employees.employee_id'], ),
        sa.ForeignKeyConstraint(['position_id'], ['positions.position_id'], ),
    )

    # Projects table
    op.create_table('projects',
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True, server_default='active'),
        sa.Column('manager_id', sa.Integer(), nullable=True),
        sa.Column('budget', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('actual_cost', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('project_id'),
        sa.UniqueConstraint('name'),
    )

    # Tasks table
    op.create_table('tasks',
        sa.Column('task_id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=300), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('assigned_to', sa.Integer(), nullable=True),
        sa.Column('deadline', sa.Date(), nullable=True),
        sa.Column('priority', sa.String(length=20), nullable=True, server_default='medium'),
        sa.Column('estimated_hours', sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True, server_default='new'),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('task_id'),
        sa.ForeignKeyConstraint(['assigned_to'], ['employees.employee_id'], ),
        sa.ForeignKeyConstraint(['project_id'], ['projects.project_id'], ondelete='CASCADE'),
    )

    # Assets table
    op.create_table('assets',
        sa.Column('asset_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('serial_number', sa.String(length=100), nullable=True),
        sa.Column('purchase_date', sa.Date(), nullable=True),
        sa.Column('purchase_price', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('warranty_until', sa.Date(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True, server_default='available'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('asset_id'),
        sa.UniqueConstraint('serial_number'),
    )

    # Asset assignments table
    op.create_table('asset_assignments',
        sa.Column('assignment_id', sa.Integer(), nullable=False),
        sa.Column('asset_id', sa.Integer(), nullable=False),
        sa.Column('employee_id', sa.Integer(), nullable=False),
        sa.Column('assigned_date', sa.Date(), nullable=False, server_default=sa.func.current_date()),
        sa.Column('returned_date', sa.Date(), nullable=True),
        sa.Column('condition_on_return', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('assignment_id'),
        sa.ForeignKeyConstraint(['asset_id'], ['assets.asset_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.employee_id'], ondelete='CASCADE'),
    )

    # Attendance table
    op.create_table('attendance',
        sa.Column('attendance_id', sa.Integer(), nullable=False),
        sa.Column('employee_id', sa.Integer(), nullable=False),
        sa.Column('work_date', sa.Date(), nullable=False),
        sa.Column('check_in', sa.DateTime(), nullable=True),
        sa.Column('check_out', sa.DateTime(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True, server_default='present'),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('attendance_id'),
        sa.UniqueConstraint('employee_id', 'work_date'),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.employee_id'], ondelete='CASCADE'),
    )


def downgrade() -> None:
    op.drop_table('attendance')
    op.drop_table('asset_assignments')
    op.drop_table('assets')
    op.drop_table('tasks')
    op.drop_table('projects')
    op.drop_table('employees')
    op.drop_table('positions')
    op.drop_table('departments')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
