export const THEME_ERROR_MESSAGES: Record<string, string> = {
    'THEME_IN_USE': '사용중인 테마는 삭제할 수 없습니다.',
    'LAST_THEME_DELETE': '사용자는 적어도 한 개의 테마를 소유하고 있어야 합니다.',
    'THEME_NOT_OWNED': '소유하고 있지 않은 테마를 삭제할 수 없습니다.',
    'CANNOT_FOUND_THEME': '존재하지 않는 테마입니다.',
    'THEME_ALREADY_SELECTED': '이미 사용중인 테마입니다.',
    'UNKNOWN': '알 수 없는 오류가 발생하였습니다. 관리자에게 문의해주세요.'
}

export const getThemeErrorMessage = (error: string) => {
    return THEME_ERROR_MESSAGES[error] || THEME_ERROR_MESSAGES['UNKNOWN'];
}