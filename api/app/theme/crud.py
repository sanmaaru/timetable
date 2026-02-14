from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, with_expression
from ulid import ULID

from app.auth.model import User, UserInfo
from app.core.config import configs
from app.timetable.model import Subject, Lecture, Class, Enrollment
from app.theme.exceptions import ThemeNotOwnedByError, ThemeNotFoundError, ThemeInUseError, LastThemeDeleteError, \
    ColorSchemeNotFoundError
from app.theme.model import Theme, ColorScheme
from app.theme.schemas import ColorSchemeSchema


async def service_create_default_theme(user: User, session: AsyncSession, title: str = None):
    if title is None:
        title = f'{user.username}님의 테마'

    theme = Theme(title=title, published=False)
    theme.owner = user
    session.add(theme)
    await session.flush()

    stmt = (select(Subject)
            .join(Lecture, Lecture.subject_id == Subject.subject_id)
            .join(Class, Class.lecture_id == Lecture.lecture_id)
            .join(Enrollment, Enrollment.class_id == Class.class_id)
            .join(UserInfo, UserInfo.user_info_id == Enrollment.user_info_id)
            .where(UserInfo.user_info_id == user.user_info_id)
            .distinct())
    result = await session.execute(stmt)
    subjects = set(result.scalars().all())
    for subject in subjects:
        color_scheme = ColorScheme(
            theme_id=theme.theme_id,
            subject_id=subject.subject_id,
            color=configs.THEME_DEFAULT_COLOR,
            text_color=configs.THEME_DEFAULT_TEXT_COLOR
        )
        session.add(color_scheme)

    return theme

async def service_delete_theme(user: User, theme_id: ULID, session: AsyncSession):
    theme = query_theme(theme_id, user, session)

    stmt = select(func.count()).select_from(Theme).where(Theme.owner_id == user.user_id)
    count = (await session.execute(stmt)).scalar()
    if count <= 1:
        raise LastThemeDeleteError('Each user is required to posses a minimum of one theme')

    if user.selected_theme_id == theme_id:
        raise ThemeInUseError('Cannot delete the theme currently in use')

    await session.delete(theme)

async def query_selected_theme(user: User, session: AsyncSession):
    stmt = (select(Theme)
            .options(selectinload(Theme.color_schemes),
                     with_expression(Theme.selected, Theme.theme_id == user.selected_theme_id))
            .where(Theme.theme_id == user.selected_theme_id))

    result = await session.execute(stmt)
    return result.scalars().one_or_none()

async def query_all_themes(user: User, session: AsyncSession):
    stmt = (select(Theme)
            .options(selectinload(Theme.color_schemes),
                     with_expression(Theme.selected, Theme.theme_id == user.selected_theme_id))
            .where(Theme.owner_id == user.user_id))
    result = await session.execute(stmt)
    return result.scalars().all()

async def query_theme(theme_id: ULID, user: User, session: AsyncSession):
    stmt = (select(Theme)
            .options(selectinload(Theme.color_schemes),
                     with_expression(Theme.selected, Theme.theme_id == user.selected_theme_id))
            .where(Theme.theme_id == theme_id))
    result = await session.execute(stmt)
    theme = result.scalars().one_or_none()

    if theme is None:
        raise ThemeNotFoundError('Theme does not exist')

    # published 되지 않은 theme의 user가 owner와 다르다면 소유하지 않았다는 뜻
    if (not theme.published) and (theme.owner_id != user.user_id):
        raise ThemeNotOwnedByError('Theme does not owned by ' + str(user.user_id))

    return theme

async def service_change_selected_theme(user: User, theme_id: ULID, session: AsyncSession):
    theme = await query_theme(theme_id, user, session)

    user.selected_theme_id = theme.theme_id
    await session.flush()
    await session.refresh(user)

async def service_change_theme(
        user: User,
        theme_id: ULID,
        session: AsyncSession,
        title: str | None = None,
        color_schemes: list[ColorSchemeSchema] | None = None
):
    theme = await query_theme(theme_id, user, session)

    if title:
        theme.title = title

    if color_schemes:
        current_schemes_map = {cs.subject.name : cs for cs in theme.color_schemes}

        for new_scheme in color_schemes:
            target_scheme = current_schemes_map.get(new_scheme.subject)

            if target_scheme:
                target_scheme.color = new_scheme.color
                target_scheme.text_color = new_scheme.text_color
            else:
                raise ColorSchemeNotFoundError('Cannot find color scheme for ' + str(new_scheme.subject))