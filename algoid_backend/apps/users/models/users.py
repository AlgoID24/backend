import uuid
from typing import Any, Dict, Optional
from datetime import datetime
from sqlalchemy import JSON, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, validates
from algoid_backend.config.db import Base
from algoid_backend.constants.table_names import TABLE_NAMES


class User(Base):
    __tablename__ = TABLE_NAMES.USER
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(unique=True)
    email_verified: Mapped[bool] = mapped_column(default=False)
    password_hash: Mapped[Optional[str]]
    date_added: Mapped[datetime] = mapped_column(insert_default=func.now())
    last_updated: Mapped[datetime] = mapped_column(
        insert_default=func.now(), onupdate=func.now()
    )

    @validates("email")
    def validate_email(self, _, address: str):
        if "@" not in address:
            raise ValueError("Failed simple email validation")
        return address


class Profile(Base):
    __tablename__ = TABLE_NAMES.PROFILE
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    first_name: Mapped[Optional[str]]
    last_name: Mapped[Optional[str]]
    nin: Mapped[Optional[str]]
    face_recognition: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    verified: Mapped[bool] = mapped_column(default=False)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(f"{TABLE_NAMES.USER}.id"), unique=True
    )

    date_added: Mapped[datetime] = mapped_column(insert_default=func.now())
    last_updated: Mapped[datetime] = mapped_column(
        insert_default=func.now(), onupdate=func.now()
    )
