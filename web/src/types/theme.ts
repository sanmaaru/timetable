export interface Theme {
    title: string;
    themeId: string;
    colorSchemes: ColorScheme[]
    selected: boolean;
}

export interface ColorScheme {
    subject: string;
    color: string;
    textColor: string;
}