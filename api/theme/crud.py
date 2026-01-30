from datetime import datetime

import ulid.ulid
from sqlalchemy.orm import Session

from theme.model import Theme, ColorScheme
from theme.exceptions import ThemeNotFoundException, ThemeNotOwnedByException
from theme.schemas import ColorSchemeSchema, ThemeSchema
from core.exceptions import NullValueException
from database import User

DEFAULT_COLOR = '#2B2A2A'
DEFAULT_TEXT_COLOR = '#EEEEEE'

def create_default_theme(user: User, session: Session, title: str = None):
    if title is None:
        title = f'{user.username}님의 테마'

    theme = Theme(
        owner_id=user.user_id,
        title=title,
        published=False,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    session.add(theme)

    subjects = [enrollment.clazz.lecture.subject.name for enrollment in user.user_info.enrollments]
    for subject in subjects:
        color_scheme = ColorScheme(
            theme_id=theme.theme_id,
            subject_id=subject.subject_id,
            color=DEFAULT_COLOR,
            text_color=DEFAULT_TEXT_COLOR
        )
        session.add(color_scheme)


def get_selected_theme(user: User):
    selected_theme = user.selected_theme
    color_schemas = []
    for color_schema in selected_theme.color_schemas:
        color_schemas.append(ColorSchemeSchema(
            subject = color_schema.subject.name,
            color = color_schema.color,
            text_color = color_schema.text_color
        ))

    return ThemeSchema(
        title=selected_theme.title,
        published=selected_theme.published,
        color_schemas=color_schemas,
        created_at=selected_theme.created_at,
        updated_at=selected_theme.updated_at,
        theme_id=selected_theme.theme_id,
    )

def get_theme(theme_id, user: User, session):
    if theme_id is None:
        raise NullValueException('Theme ID must not be null', 'theme_id')

    if isinstance(theme_id, str):
        theme_id = ulid.from_str(theme_id)

    theme = (session.query(Theme)
             .filter(Theme.theme_id == theme_id)
             .one_or_none())

    if theme is None:
        raise ThemeNotFoundException('Theme does not exist')

    # published 되지 않은 theme의 user가 owner와 다르다면 소유하지 않았다는 뜻
    if (not theme.published) and (theme.owner_id != user.user_id):
        raise ThemeNotOwnedByException('Theme does not owned by ' + theme.owner)

    return theme
