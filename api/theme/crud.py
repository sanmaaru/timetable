from datetime import datetime

from sqlalchemy.orm import Session
from ulid import ULID

from auth.model import User, UserInfo
from core.exceptions import NullValueException
from theme.exceptions import ThemeNotFoundException, ThemeNotOwnedByException, LastThemeDeleteException, \
    ThemeInUseException
from theme.model import Theme, ColorScheme
from theme.schemas import ThemeSchema, parse_color_schemes

DEFAULT_COLOR = '#2B2A2A'
DEFAULT_TEXT_COLOR = '#EEEEEE'

def service_create_default_theme(user: User, user_info: UserInfo, session: Session, title: str = None):
    if title is None:
        title = f'{user.username}님의 테마'

    theme = Theme(
        title=title,
        published=False,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    theme.owner = user
    session.add(theme)

    subjects = set([enrollment.clazz.lecture.subject for enrollment in user_info.enrollments])
    for subject in subjects:
        color_scheme = ColorScheme(
            theme_id=theme.theme_id,
            subject_id=subject.subject_id,
            color=DEFAULT_COLOR,
            text_color=DEFAULT_TEXT_COLOR
        )
        session.add(color_scheme)

    return theme

def service_delete_theme(user: User, theme_id: ULID, session: Session):
    if theme_id is None:
        raise NullValueException('Theme id is null', invalid='theme_id')

    theme = session.query(Theme).filter(Theme.theme_id == theme_id).one_or_none()
    if theme is None:
        raise ThemeNotFoundException('Theme does not exist', theme_id=theme_id)

    if theme.owner_id != user.user_id:
        raise ThemeNotOwnedByException('Theme does not owned by ' + user.user_id, theme_id=theme_id)

    if user.selected_theme_id == theme_id:
        raise ThemeInUseException('Cannot delete the theme currently in use', theme_id=theme_id)

    if len(user.owning_themes) <= 1:
        raise LastThemeDeleteException('Each user is required to posses a minimum of one theme')

    session.delete(theme)

def query_selected_theme(user: User):
    selected_theme = user.selected_theme
    color_schemes = parse_color_schemes(selected_theme.color_schemes)

    return ThemeSchema(
        title=selected_theme.title,
        published=selected_theme.published,
        color_schemes=color_schemes,
        created_at=selected_theme.created_at,
        updated_at=selected_theme.updated_at,
        theme_id=selected_theme.theme_id,
        selected=True
    )

def query_all_themes(user: User):
    theme_schemas = []
    themes = user.owning_themes
    for theme in themes:
        theme_schema_args = {
            'title': theme.title,
            'published': theme.published,
            'color_schemes': parse_color_schemes(theme.color_schemes),
            'created_at': theme.created_at,
            'updated_at': theme.updated_at,
            'theme_id': theme.theme_id,
        }

        if user.selected_theme_id == theme.theme_id:
            theme_schema_args['selected'] = True

        theme_schemas.append(ThemeSchema(**theme_schema_args))

    return theme_schemas

def query_theme(theme_id, user: User, session: Session):
    theme: Theme | None = session.query(Theme).filter(Theme.theme_id == theme_id).one_or_none()

    if theme is None:
        raise ThemeNotFoundException('Theme does not exist', theme_id=theme_id)

    # published 되지 않은 theme의 user가 owner와 다르다면 소유하지 않았다는 뜻
    if (not theme.published) and (theme.owner_id != user.user_id):
        raise ThemeNotOwnedByException('Theme does not owned by ' + user.user_id, theme_id=theme_id)

    return ThemeSchema(
        title=theme.title,
        published=theme.published,
        color_schemes=parse_color_schemes(theme.color_schemes),
        created_at=theme.created_at,
        updated_at=theme.updated_at,
        theme_id=theme.theme_id,
        selected=(user.selected_theme_id == theme.theme_id),
    )

def service_change_selected_theme(user: User, theme_id: ULID, session: Session):
    theme = session.query(Theme).filter(Theme.theme_id == theme_id).one_or_none()
    if theme is None:
        raise ThemeNotFoundException('Theme does not exist', theme_id=theme_id)

    if theme.owner_id != user.user_id:
        raise ThemeNotOwnedByException('Theme does not owned by ' + user.user_id, theme_id=theme_id)

    user.selected_theme_id = theme.theme_id