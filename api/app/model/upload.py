from typing import Any, Callable, Dict, Literal

import ulid
from sqlalchemy import ForeignKey, String, JSON
from sqlalchemy.orm import Mapped
from sqlalchemy.testing.schema import mapped_column

from app.core.database import Base, ULID, generate_ulid

OVERWRITE_TRANSITIONS: Dict[str, Callable[..., Any]] = {}
REWRITE_TRANSITIONS: Dict[str, Callable[..., Any]] = {}

def register_transition(action_name: str, type: Literal['overwrite', 'rewrite']):
    def decorator(func):
        if type == 'overwrite':
            OVERWRITE_TRANSITIONS[action_name] = func
        else:
            REWRITE_TRANSITIONS[action_name] = func

        return func
    return decorator

class UploadDraft(Base):
    __tablename__ = 'upload_drafts'

    draft_id: Mapped[ulid.ULID] = mapped_column(ULID(), primary_key=True, default=generate_ulid)
    action_name: Mapped[str] = mapped_column(String(128), nullable=False)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)