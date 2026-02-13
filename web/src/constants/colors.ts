import {ToastType} from "../components/alert/toast/types";

export const defaultColors = [
    '#000000', '#242424', '#5b5b5b', '#808080', '#a4a4a4', '#dbdbdb', '#ffffff',
    '#E3FAFF', '#E7FDFD', '#F7FCFA', '#FDFCF9', '#FFF8EC', '#FFEFE8', '#FDECEB',
    '#8FECFF', '#A0F7F9', '#E8F5F1', '#FAF7EC', '#FFE4B2', '#FEC1A5', '#F6B3AD',
    '#3BDEFF', '#5AF2F4', '#C9E8DE', '#F4EBD2', '#FFC965', '#FC834A', '#EE685B',
    '#00A8C9', '#0ED8DB', '#AADCCB', '#EDE0B8', '#FFAE17', '#FB5406', '#E72F1E',
    '#005F73', '#0A9396', '#94D2BD', '#E9D8A6', '#EE9B00', '#BB3E03', '#AE2012',
]

export const toastTextColor: Record<ToastType, string> = {
    'info': '#000000',
    'success': '#4f772d',
    'error': '#d62828'
}