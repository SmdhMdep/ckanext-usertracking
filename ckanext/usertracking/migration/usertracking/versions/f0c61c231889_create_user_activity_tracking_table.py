"""Create user activity tracking table

Revision ID: f0c61c231889
Revises: 
Create Date: 2022-11-11 09:10:16.408729

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = 'f0c61c231889'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        u"user_activity_tracker",
        sa.Column(u"id", sa.UnicodeText),
        sa.Column(u"name", sa.UnicodeText),
        sa.Column(u"organisations", sa.ARRAY(sa.UnicodeText)),
        sa.Column(u"page", sa.UnicodeText),
        sa.Column(u"seconds_on_page", sa.SMALLINT),
        sa.Column(u'timestamp', sa.TIMESTAMP,
            server_default=sa.func.current_timestamp()
        )
    )


def downgrade():
    op.drop_table(u"user_activity_tracker")

