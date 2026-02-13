import React, {useEffect} from "react";
import './EditableColorSchemeElement.css';
import {ColorScheme} from "../../types/theme";
import Palette from "./Palette";
import usePalette from "../../hooks/theme/usePalette";
import {shade} from "../../util/color";

interface ColorSchemeElementProps {
    colorScheme: ColorScheme;
    setColorScheme: (subject: string, color?: string, textColor?: string) => void;
    onClick: (subject: string | null) => void;
    focus: string | null;
}

const ColorSchemeElement = ({colorScheme, setColorScheme, onClick, focus}: ColorSchemeElementProps) => {
    const { subject } = colorScheme;
    const [color, setColor] = React.useState<string>(colorScheme.color);
    const [textColor, setTextColor] = React.useState<string>(colorScheme.textColor);

    const colorPalette = usePalette(false);
    const textColorPalette = usePalette(false);

    useEffect(() => {
        setColorScheme(colorScheme.subject, color, textColor);
    }, [color, textColor, colorScheme.subject, setColorScheme]);

    const handleClick = () => {
        if (focus === subject)
            onClick(null);
        else
            onClick(subject);
    }

    return (
        <div
            className={`EditableColorSchemeElement ${focus === subject ? 'focus' : ''}`}
            onClick={() => {handleClick()}}
        >
            <span>{subject}</span>
            <span>{color}</span>
            <div style={{ backgroundColor: color }}></div>
            {focus === subject && <div
                className={'palette'}
                onClick={(e) => {
                    e.stopPropagation();
                }}
            >
                <div>
                    <span>배경 색상</span>
                    <button
                        style={{ backgroundColor: color, border: `solid 1px ${shade(color, 0.1)}` }}
                        ref={colorPalette.refs.setReference}
                        {...colorPalette.getReferenceProps()}
                    />
                </div>
                <div>
                    <span>글자 색상</span>
                    <button
                        style={{ backgroundColor: textColor, border: `solid 1px ${shade(textColor, 0.1)}` }}
                        ref={textColorPalette.refs.setReference}
                        {...textColorPalette.getReferenceProps()}
                    />
                </div>
                <Palette
                    ref={colorPalette.refs.setFloating}
                    context={colorPalette.paletteContext}
                    color={color}
                    setColor={setColor}
                />
                <Palette

                    ref={textColorPalette.refs.setFloating}
                    context={textColorPalette.paletteContext}
                    color={textColor}
                    setColor={setTextColor}
                />
            </div>}
        </div>
    )
}

export default ColorSchemeElement;