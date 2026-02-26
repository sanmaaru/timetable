export interface MetaDto {
    user_id: string | null;
    status: number;
    response_at: string;
}

export interface BaseResponseDto<T> {
    meta: MetaDto;
    data: T;
}

