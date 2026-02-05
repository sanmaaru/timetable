export const LOGIN_ERROR_MESSAGES = {
    GENERAL: '로그인 과정 중에 오류가 발생하였습니다. 관리자에게 제보해 주세요.',
    PASSWORD: '비밀번호가 일치하지 않습니다',
    USERNAME: '존재하지 않는 사용자 이름입니다.'
}

export const SIGN_UP_ERROR_MESSAGES = {
    GENERAL: '회원가입 과정 중에 오류가 발생하였습니다. 관리자에게 제보해 주세요.',
    USERNAME: '이미 존재하는 사용자 이름 입니다.',
    IDENTIFY_TOKEN: '이미 만료된 인증 토큰 입니다.'
}

export const AUTH_INVALID_TOKEN = {
    USERNAME: 'username',
    PASSWORD: 'password',
    IDENTIFY_TOKEN: 'identify_token',
}

export const handleLoginError = (invalid: string) => {
    let object, message
    switch (invalid) {
        case AUTH_INVALID_TOKEN.USERNAME:
            object = 'username'
            message = LOGIN_ERROR_MESSAGES.USERNAME
            break;

        case AUTH_INVALID_TOKEN.PASSWORD:
            object = 'password'
            message = LOGIN_ERROR_MESSAGES.PASSWORD
            break;

        default:
            object = null
            message = LOGIN_ERROR_MESSAGES.GENERAL
            break;
    }

    return { object, message }
}

export const handleSignUpError = (invalid: string) => {
    let object, message
    switch (invalid) {
        case AUTH_INVALID_TOKEN.USERNAME:
            object = 'username'
            message = SIGN_UP_ERROR_MESSAGES.USERNAME
            break;

        case AUTH_INVALID_TOKEN.IDENTIFY_TOKEN:
            object = 'identifyToken'
            message = SIGN_UP_ERROR_MESSAGES.IDENTIFY_TOKEN
            break;

        default:
            object = null
            message = SIGN_UP_ERROR_MESSAGES.GENERAL
            break;
    }
    return { object, message }
}
