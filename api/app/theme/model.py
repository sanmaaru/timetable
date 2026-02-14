from datetime import datetime

import ulid
from sqlalchemy import ForeignKey, Boolean, DateTime, func
from sqlalchemy.dialects.mysql import VARCHAR
from sqlalchemy.orm import relationship, mapped_column, Mapped, query_expression

from app.core.database import Base, ULID, generate_ulid, Hex


class Theme(Base):

    __tablename__ = "themes"

    theme_id: Mapped[ulid.ULID] = mapped_column(ULID(), primary_key=True, default=generate_ulid)
    owner_id: Mapped[ulid.ULID] = mapped_column(ULID(), ForeignKey("users.user_id"), nullable=False)
    parent_theme_id: Mapped[ulid.ULID] = mapped_column(ULID(), ForeignKey("themes.theme_id"))
    title: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)
    published: Mapped[bool] = mapped_column(Boolean(), default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    owner = relationship("User", back_populates="owning_themes", foreign_keys=[owner_id])
    color_schemes = relationship("ColorScheme", back_populates="theme", cascade='all, delete-orphan')
    selectors = relationship('User', back_populates="selected_theme", passive_deletes=True, foreign_keys="[User.selected_theme_id]")

    selected: Mapped[bool] = query_expression()

class ColorScheme(Base):

    __tablename__ = "color_schemes"

    color_scheme_id: Mapped[ulid.ULID] = mapped_column(ULID(), primary_key=True, default=generate_ulid)
    theme_id: Mapped[ulid.ULID] = mapped_column(ULID(), ForeignKey("themes.theme_id"), nullable=False)
    subject_id: Mapped[ulid.ULID] = mapped_column(ULID(), ForeignKey("subjects.subject_id"), nullable=False)
    color: Mapped[str] = mapped_column(Hex(length=6), nullable=False)
    text_color: Mapped[str] = mapped_column(Hex(length=6), nullable=False)

    theme = relationship("Theme", back_populates="color_schemes")
    subject = relationship('Subject')
