export interface ColorSchemeDto {
    subject: string;
    color: string;
    text_color: string;
}

export interface ThemeDto {
    theme_id: string;
    title: string;
    published: boolean;
    color_schemes: ColorSchemeDto[];
    created_at: string;
    updated_at: string;
    selected: boolean;
}