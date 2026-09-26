from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "prices",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("symbol", sa.String(length=20), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("open", sa.Float(), nullable=False),
        sa.Column("high", sa.Float(), nullable=False),
        sa.Column("low", sa.Float(), nullable=False),
        sa.Column("close", sa.Float(), nullable=False),
        sa.Column("volume", sa.Float(), nullable=False),
    )
    op.create_index("ix_prices_symbol", "prices", ["symbol"])
    op.create_index("ix_prices_timestamp", "prices", ["timestamp"])

    op.create_table(
        "predictions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("symbol", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("horizon", sa.Integer(), nullable=False),
        sa.Column("model", sa.String(length=80), nullable=False),
        sa.Column("point", sa.Float(), nullable=False),
        sa.Column("lower", sa.Float(), nullable=False),
        sa.Column("upper", sa.Float(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
    )
    op.create_index("ix_predictions_symbol", "predictions", ["symbol"])

    op.create_table(
        "news",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("symbol", sa.String(length=20), nullable=False),
        sa.Column("published_at", sa.DateTime(), nullable=False),
        sa.Column("headline", sa.Text(), nullable=False),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("sentiment", sa.Float(), nullable=False),
    )
    op.create_index("ix_news_symbol", "news", ["symbol"])


def downgrade() -> None:
    op.drop_index("ix_news_symbol", table_name="news")
    op.drop_table("news")
    op.drop_index("ix_predictions_symbol", table_name="predictions")
    op.drop_table("predictions")
    op.drop_index("ix_prices_timestamp", table_name="prices")
    op.drop_index("ix_prices_symbol", table_name="prices")
    op.drop_table("prices")
