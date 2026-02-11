export interface Theme {
    title: string;
    theme_id: string;
    colorSchemes: ColorScheme[]
    selected: boolean;
}

export interface ColorScheme {
    subject: string;
    color: string;
    textColor: string;
}