import React, {useEffect} from "react";
import style from './EditableColorSchemeElement.module.css';
import colorSchemeStyle from './ColorSchemeElement.module.css';
import {ColorScheme} from "../../types/theme";
import Palette from "./Palette";
import {shade} from "../../util/color";
import useFloatingMenu from "../../hooks/useFloatingMenu";

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

    const [isColorPaletteOpen, setColorPaletteOpen] = React.useState(false);
    const colorPalette = useFloatingMenu(isColorPaletteOpen, setColorPaletteOpen);

    const [isTextColorPaletteOpen, setTextColorPaletteOpen] = React.useState(false);
    const textColorPalette = useFloatingMenu(isTextColorPaletteOpen, setTextColorPaletteOpen);

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
            className={`${colorSchemeStyle.colorSchemeElement} ${focus === subject ? colorSchemeStyle.focus : ''}`}
            onClick={() => {handleClick()}}
        >
            <span>{subject}</span>
            <span>{color}</span>
            <div style={{ backgroundColor: color }}></div>
            {focus === subject && <div
                className={style.selector}
                onClick={(e) => {
                    e.stopPropagation();
                }}
            >
                <div className={style.content}>
                    <span>배경 색상</span>
                    <button
                        style={{ backgroundColor: color, border: `solid 1px ${shade(color, 0.1)}` }}
                        ref={colorPalette.ref}
                        {...colorPalette.getReferenceProps()}
                    />
                </div>
                <div className={style.content}>
                    <span>글자 색상</span>
                    <button
                        style={{ backgroundColor: textColor, border: `solid 1px ${shade(textColor, 0.1)}` }}
                        ref={textColorPalette.ref}
                        {...textColorPalette.getReferenceProps()}
                    />
                </div>
                <Palette
                    context={colorPalette.menuContext}
                    color={color}
                    setColor={setColor}
                />
                <Palette

                    context={textColorPalette.menuContext}
                    color={textColor}
                    setColor={setTextColor}
                />
            </div>}
        </div>
    )
}

export default ColorSchemeElement;