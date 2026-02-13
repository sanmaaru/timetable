export const map: Record<string, string> = {
    'top': 'bottom center',
    'bottom': 'top center',
    'left': 'right center',
    'right': 'left center',
    'top-start': 'bottom left',
    'top-end': 'bottom right',
    'bottom-start': 'top left',
    'bottom-end': 'top right',
    'left-start': 'right top',
    'left-end': 'right bottom',
    'right-start': 'left top',
    'right-end': 'left bottom',
}

export const getTransformOrigin = (placement: string) => {
    return map[placement] || 'center center';
};
