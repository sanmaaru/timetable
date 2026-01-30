from sqlalchemy import Column, ForeignKey, String, Boolean, DateTime
from sqlalchemy.dialects.mysql import VARCHAR
from sqlalchemy.orm import relationship

from database import Base, ULID, generate_ulid, Hex


class Theme(Base):

    __tablename__ = "themes"

    theme_id = Column(ULID(), primary_key=True, default=generate_ulid)
    owner_id = Column(String(36), ForeignKey("users.user_id"), nullable=False)
    parent_theme_id = Column(ULID(), ForeignKey("themes.theme_id"))
    title = Column(VARCHAR(255), nullable=False)
    published = Column(Boolean(), default=False)
    created_at = Column(DateTime(), nullable=False)
    updated_at = Column(DateTime(), nullable=False)

    owner = relationship("User", back_populates="owning_themes")
    color_schemes = relationship("ColorScheme", back_populates="theme", cascade='all, delete-orphan')
    selectors = relationship('User', back_populates="selected_theme", passive_deletes=True)



class ColorScheme(Base):

    __tablename__ = "color_schemes"

    color_scheme_id = Column(ULID(), primary_key=True, default=generate_ulid)
    theme_id = Column(ULID(), ForeignKey("themes.theme_id"), nullable=False)
    subject_id = Column(String(36), ForeignKey("subjects.subject_id"), nullable=False)
    color = Column(Hex(length=6), nullable=False)
    text_color = Column(Hex(length=6), nullable=False)

    theme = relationship("Theme", back_populates="color_schemes")
