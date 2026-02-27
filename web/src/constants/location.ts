export const locations = {
    account: '/account',
    theme: '/theme',
    home: '/'
} as const; // home이 항상 마지막이여야 하는거 주의!
export type LocationKey = keyof typeof locations;

export const getActiveId = (pathname: string) => {
    for (const [key, path] of Object.entries(locations)) {
        if (pathname.startsWith(path))
            return key as LocationKey;
    }
    return 'null';
}
