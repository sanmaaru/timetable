import React, {useEffect} from "react";
import style from './ColorSchemeEditDialog.module.css';
import useFloatingMenu from "../../../hooks/useFloatingMenu";
import {DialogContextType} from "./DialogProvider";
import {ColorScheme} from "../../../types/theme";
import {shade} from "../../../util/color";
import Palette from "../../theme/Palette";
import IconButton from "../../button/IconButton";
import Close from '../../../resources/icon/icn_close.svg?react';

interface ColorSchemeEditDialogProps {
    context: DialogContextType
    colorScheme: ColorScheme
    setColorScheme: (subject: string, color?: string, textColor?: string) => void;
}

const ColorSchemeEditDialog = ({context, colorScheme, setColorScheme}: ColorSchemeEditDialogProps) => {
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

    return (
        <div className={style.colorSchemeEditDialog}>
            <div className={style.title}>
                <span>{`${subject}`}</span>
                <IconButton className={style.button} onClick={context.close}>
                    <Close/>
                </IconButton>
            </div>
            <div className={style.container}>
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
        </div>
    )
}

export default ColorSchemeEditDialog;