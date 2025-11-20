"""Initial database schema."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "20250119_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "certificates",
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
        sa.Column("individual_name", sa.String(length=255), nullable=False),
        sa.Column("individual_address", sa.Text(), nullable=False),
        sa.Column("certificate_date", sa.String(length=32), nullable=False),
        sa.Column("engagement_date", sa.String(length=32), nullable=False),
        sa.Column("embassy_name", sa.String(length=255), nullable=False),
        sa.Column("embassy_address", sa.Text(), nullable=False),
        sa.Column("passport_number", sa.String(length=64), nullable=True),
        sa.Column("foreign_currency", sa.String(length=8), nullable=False),
        sa.Column("exchange_rate", sa.Float(), nullable=False),
        sa.Column("bank_accounts_notes", sa.Text(), nullable=True),
        sa.Column("insurance_policies_notes", sa.Text(), nullable=True),
        sa.Column("pf_accounts_notes", sa.Text(), nullable=True),
        sa.Column("deposits_notes", sa.Text(), nullable=True),
        sa.Column("nps_accounts_notes", sa.Text(), nullable=True),
        sa.Column("mutual_funds_notes", sa.Text(), nullable=True),
        sa.Column("shares_notes", sa.Text(), nullable=True),
        sa.Column("vehicles_notes", sa.Text(), nullable=True),
        sa.Column("post_office_schemes_notes", sa.Text(), nullable=True),
        sa.Column("partnership_firms_notes", sa.Text(), nullable=True),
        sa.Column("gold_holdings_notes", sa.Text(), nullable=True),
        sa.Column("properties_notes", sa.Text(), nullable=True),
        sa.Column("liabilities_notes", sa.Text(), nullable=True),
        sa.Column("ca_firm_name", sa.String(length=255), nullable=False),
        sa.Column("ca_frn", sa.String(length=32), nullable=False),
        sa.Column("ca_partner_name", sa.String(length=255), nullable=False),
        sa.Column("ca_membership_no", sa.String(length=64), nullable=False),
        sa.Column("ca_designation", sa.String(length=128), nullable=False),
        sa.Column("ca_place", sa.String(length=128), nullable=False),
        sa.Column("total_movable_assets_inr", sa.Float(), nullable=False),
        sa.Column("total_immovable_assets_inr", sa.Float(), nullable=False),
        sa.Column("total_liabilities_inr", sa.Float(), nullable=False),
        sa.Column("net_worth_inr", sa.Float(), nullable=False),
        sa.Column("net_worth_foreign", sa.Float(), nullable=False),
        sa.Column("data_snapshot", sa.Text(), nullable=False),
        sa.Column("metadata_json", sa.Text(), nullable=True),
        sa.Column("document_file_name", sa.String(length=512), nullable=True),
        sa.Column("document_mime_type", sa.String(length=128), nullable=True),
        sa.Column("document_file_size", sa.Integer(), nullable=True),
        sa.Column("document_bytes", sa.LargeBinary(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_certificates_created_at", "certificates", ["created_at"], unique=False
    )

    op.create_table(
        "bank_accounts",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("certificate_id", sa.String(length=36), nullable=False),
        sa.Column("holder_name", sa.String(length=255), nullable=False),
        sa.Column("account_number", sa.String(length=128), nullable=False),
        sa.Column("bank_name", sa.String(length=255), nullable=False),
        sa.Column("balance_inr", sa.Float(), nullable=False),
        sa.Column("statement_date", sa.String(length=32), nullable=True),
        sa.ForeignKeyConstraint(
            ["certificate_id"], ["certificates.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_bank_accounts_certificate_id",
        "bank_accounts",
        ["certificate_id"],
        unique=False,
    )

    op.create_table(
        "insurance_policies",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("certificate_id", sa.String(length=36), nullable=False),
        sa.Column("holder_name", sa.String(length=255), nullable=False),
        sa.Column("policy_number", sa.String(length=128), nullable=False),
        sa.Column("amount_inr", sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(
            ["certificate_id"], ["certificates.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_insurance_policies_certificate_id",
        "insurance_policies",
        ["certificate_id"],
        unique=False,
    )

    op.create_table(
        "pf_accounts",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("certificate_id", sa.String(length=36), nullable=False),
        sa.Column("holder_name", sa.String(length=255), nullable=False),
        sa.Column("pf_account_number", sa.String(length=128), nullable=False),
        sa.Column("amount_inr", sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(
            ["certificate_id"], ["certificates.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_pf_accounts_certificate_id", "pf_accounts", ["certificate_id"], unique=False
    )

    op.create_table(
        "deposits",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("certificate_id", sa.String(length=36), nullable=False),
        sa.Column("holder_name", sa.String(length=255), nullable=False),
        sa.Column("account_number", sa.String(length=128), nullable=False),
        sa.Column("amount_inr", sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(
            ["certificate_id"], ["certificates.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_deposits_certificate_id", "deposits", ["certificate_id"], unique=False
    )

    op.create_table(
        "nps_accounts",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("certificate_id", sa.String(length=36), nullable=False),
        sa.Column("owner_name", sa.String(length=255), nullable=False),
        sa.Column("pran_number", sa.String(length=128), nullable=False),
        sa.Column("amount_inr", sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(
            ["certificate_id"], ["certificates.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_nps_accounts_certificate_id",
        "nps_accounts",
        ["certificate_id"],
        unique=False,
    )

    op.create_table(
        "mutual_funds",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("certificate_id", sa.String(length=36), nullable=False),
        sa.Column("holder_name", sa.String(length=255), nullable=False),
        sa.Column("folio_number", sa.String(length=128), nullable=False),
        sa.Column("policy_name", sa.String(length=255), nullable=False),
        sa.Column("amount_inr", sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(
            ["certificate_id"], ["certificates.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_mutual_funds_certificate_id",
        "mutual_funds",
        ["certificate_id"],
        unique=False,
    )

    op.create_table(
        "shares",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("certificate_id", sa.String(length=36), nullable=False),
        sa.Column("company_name", sa.String(length=255), nullable=False),
        sa.Column("num_shares", sa.Integer(), nullable=False),
        sa.Column("market_price_inr", sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(
            ["certificate_id"], ["certificates.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_shares_certificate_id", "shares", ["certificate_id"], unique=False
    )

    op.create_table(
        "vehicles",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("certificate_id", sa.String(length=36), nullable=False),
        sa.Column("vehicle_type", sa.String(length=64), nullable=False),
        sa.Column("make_model_year", sa.String(length=255), nullable=False),
        sa.Column("registration_number", sa.String(length=64), nullable=False),
        sa.Column("market_value_inr", sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(
            ["certificate_id"], ["certificates.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_vehicles_certificate_id", "vehicles", ["certificate_id"], unique=False
    )

    op.create_table(
        "post_office_schemes",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("certificate_id", sa.String(length=36), nullable=False),
        sa.Column("scheme_type", sa.String(length=255), nullable=False),
        sa.Column("account_number", sa.String(length=128), nullable=False),
        sa.Column("amount_inr", sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(
            ["certificate_id"], ["certificates.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_post_office_schemes_certificate_id",
        "post_office_schemes",
        ["certificate_id"],
        unique=False,
    )

    op.create_table(
        "partnership_firms",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("certificate_id", sa.String(length=36), nullable=False),
        sa.Column("firm_name", sa.String(length=255), nullable=False),
        sa.Column("partner_name", sa.String(length=255), nullable=False),
        sa.Column("holding_percentage", sa.Float(), nullable=False),
        sa.Column("capital_balance_inr", sa.Float(), nullable=False),
        sa.Column("valuation_date", sa.String(length=32), nullable=True),
        sa.ForeignKeyConstraint(
            ["certificate_id"], ["certificates.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_partnership_firms_certificate_id",
        "partnership_firms",
        ["certificate_id"],
        unique=False,
    )

    op.create_table(
        "gold_holdings",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("certificate_id", sa.String(length=36), nullable=False),
        sa.Column("owner_name", sa.String(length=255), nullable=False),
        sa.Column("weight_grams", sa.Float(), nullable=False),
        sa.Column("rate_per_10g", sa.Float(), nullable=False),
        sa.Column("valuation_date", sa.String(length=32), nullable=True),
        sa.Column("valuer_name", sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(
            ["certificate_id"], ["certificates.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_gold_holdings_certificate_id",
        "gold_holdings",
        ["certificate_id"],
        unique=False,
    )

    op.create_table(
        "properties",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("certificate_id", sa.String(length=36), nullable=False),
        sa.Column("owner_name", sa.String(length=255), nullable=False),
        sa.Column("property_type", sa.String(length=128), nullable=False),
        sa.Column("address", sa.Text(), nullable=False),
        sa.Column("valuation_inr", sa.Float(), nullable=False),
        sa.Column("valuation_date", sa.String(length=32), nullable=True),
        sa.Column("valuer_name", sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(
            ["certificate_id"], ["certificates.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_properties_certificate_id",
        "properties",
        ["certificate_id"],
        unique=False,
    )

    op.create_table(
        "liabilities",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("certificate_id", sa.String(length=36), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=False),
        sa.Column("amount_inr", sa.Float(), nullable=False),
        sa.Column("details", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["certificate_id"], ["certificates.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_liabilities_certificate_id",
        "liabilities",
        ["certificate_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_liabilities_certificate_id", table_name="liabilities")
    op.drop_table("liabilities")
    op.drop_index("ix_properties_certificate_id", table_name="properties")
    op.drop_table("properties")
    op.drop_index("ix_gold_holdings_certificate_id", table_name="gold_holdings")
    op.drop_table("gold_holdings")
    op.drop_index(
        "ix_partnership_firms_certificate_id", table_name="partnership_firms"
    )
    op.drop_table("partnership_firms")
    op.drop_index("ix_post_office_schemes_certificate_id", table_name="post_office_schemes")
    op.drop_table("post_office_schemes")
    op.drop_index("ix_vehicles_certificate_id", table_name="vehicles")
    op.drop_table("vehicles")
    op.drop_index("ix_shares_certificate_id", table_name="shares")
    op.drop_table("shares")
    op.drop_index("ix_mutual_funds_certificate_id", table_name="mutual_funds")
    op.drop_table("mutual_funds")
    op.drop_index("ix_nps_accounts_certificate_id", table_name="nps_accounts")
    op.drop_table("nps_accounts")
    op.drop_index("ix_deposits_certificate_id", table_name="deposits")
    op.drop_table("deposits")
    op.drop_index("ix_pf_accounts_certificate_id", table_name="pf_accounts")
    op.drop_table("pf_accounts")
    op.drop_index("ix_insurance_policies_certificate_id", table_name="insurance_policies")
    op.drop_table("insurance_policies")
    op.drop_index("ix_bank_accounts_certificate_id", table_name="bank_accounts")
    op.drop_table("bank_accounts")
    op.drop_index("ix_certificates_created_at", table_name="certificates")
    op.drop_table("certificates")

