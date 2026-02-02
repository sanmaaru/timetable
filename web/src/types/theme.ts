export interface Theme {
    title: string;
    theme_id: string;
    colorSchemas: ColorSchema[]
}

export interface ColorSchema {
    subject: string;
    color: string;
    textColor: string;
}