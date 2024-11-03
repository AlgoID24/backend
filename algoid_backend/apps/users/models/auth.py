from datetime import datetime
import uuid
from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column
from algoid_backend.config.db import Base
from algoid_backend.config.settings import settings
from algoid_backend.constants.table_names import TABLE_NAMES


class AuthToken(Base):
    __tablename__ = TABLE_NAMES.AUTH_TOKEN
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    token: Mapped[str] = mapped_column(unique=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(f"{TABLE_NAMES.USER}.id"), unique=True
    )
    valid_till: Mapped[datetime] = mapped_column(
        default=(
            lambda: datetime.now() + settings.auth_token_refresh_token_valid_duration
        )()
    )
    date_added: Mapped[datetime] = mapped_column(insert_default=func.now())
    last_updated: Mapped[datetime] = mapped_column(
        insert_default=func.now(), onupdate=func.now()
    )
