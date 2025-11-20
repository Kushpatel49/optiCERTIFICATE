"""Add persons table and link certificates."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "20250119_0002"
down_revision = "20250119_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "persons",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column("display_name", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("phone_number", sa.String(length=64), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    with op.batch_alter_table("certificates", schema=None) as batch_op:
        batch_op.add_column(sa.Column("person_id", sa.String(length=36), nullable=True))
        batch_op.create_index(
            "ix_certificates_person_id",
            ["person_id"],
            unique=False,
        )
        batch_op.create_foreign_key(
            "fk_certificates_person_id_persons",
            "persons",
            ["person_id"],
            ["id"],
            ondelete="SET NULL",
        )


def downgrade() -> None:
    with op.batch_alter_table("certificates", schema=None) as batch_op:
        batch_op.drop_constraint(
            "fk_certificates_person_id_persons", type_="foreignkey"
        )
        batch_op.drop_index("ix_certificates_person_id")
        batch_op.drop_column("person_id")
    op.drop_table("persons")

