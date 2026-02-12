export const tint = (hex: string, factor: number) => {
    const rgb = hex2rgb(hex);

    const tintRGB = rgb.map((c: number) => Math.round(c + (255 - c) * factor));

    return rgb2hex(...(tintRGB as [number, number, number]));
}

export const shade = (hex: string, factor: number) => {
    const rgb = hex2rgb(hex);

    const tintRGB = rgb.map((c: number) => Math.round(c - c * factor));

    return rgb2hex(...(tintRGB as [number, number, number]));
}

export const hex2rgb = (hex: string): [number, number, number] => {
    let r = 0, g= 0, b = 0
    const cleanHex = hex.replace('#', '')

    if (cleanHex.length === 3) {
        r = parseInt(cleanHex[0] + cleanHex[0], 16)
        g = parseInt(cleanHex[1] + cleanHex[1], 16)
        b = parseInt(cleanHex[2] + cleanHex[2], 16)
    } else {
        r = parseInt(cleanHex.substring(0, 2), 16)
        g = parseInt(cleanHex.substring(2, 4), 16)
        b = parseInt(cleanHex.substring(4, 6), 16)
    }

    return [r, g, b]
}

export const rgb2hex = (r: number, g: number, b: number) => {
    const toHex = (c: number) => c.toString(16).padStart(2, '0')

    return `#${toHex(r)}${toHex(g)}${toHex(b)}`
}