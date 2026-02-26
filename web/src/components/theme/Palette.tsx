import React from 'react';
import style from './Palette.module.css';
import {FloatingFocusManager, FloatingPortal} from "@floating-ui/react";
import {recentUsedColor} from "../../util/storage";
import {shade} from "../../util/color";
import {defaultColors} from "../../constants/colors";
import Close from '../../resources/icon/icn_close.svg?react';
import Add from '../../resources/icon/icn_add.svg?react';
import IconButton from "../button/IconButton";
import {ChromePicker, ColorResult} from "react-color";
import useFloatingMenu, {FloatingMenuContext} from "../../hooks/useFloatingMenu";
import FloatingMenu from "../menu/FloatingMenu";

interface PaletteProps {
    context: FloatingMenuContext;
    color: string;
    setColor: (color: string) => void;
}

const drawColorBox = (color: string, selected: string, handleSetColor: (color: string) => void, key?: string) => {
    return <div
        key={key}
        className={`${style.colorBox} ${selected === color ? style.selected : ''}`}
        style={{
            backgroundColor: color,
            border: `0.25px solid ${shade(color, 0.1)}`,
        }}
        onClick={() => handleSetColor(color)}
    />
}

const drawColorBoxes = (colors: string[], selected: string, handleSetColor: (color: string) => void) => {
    return colors.map((color, index) => (
        drawColorBox(color, selected, handleSetColor, `${color}`)
    ))
}

const Palette = ({ color, setColor, context }: PaletteProps) => {
    const [displayPicker, setDisplayPicker] = React.useState(false);
    const { menuContext, ref, getReferenceProps } = useFloatingMenu(displayPicker, setDisplayPicker)

    const handleClickPicker= () => {
        if (displayPicker) {
            handleSetColor(color);
            setDisplayPicker(false);
        } else {
            setPickerColor(color);
            setDisplayPicker(true);
        }
    }

    const closeColorPicker = () => {
        if (displayPicker) {
            handleSetColor(color);
            setDisplayPicker(false);
        }
    }

    const handleSetColor = (color: string) => {
        setColor(color);
        recentUsedColor.append(color);
    }

    const [pickerColor, setPickerColor] = React.useState(color);
    const handlePickerChange = (color: ColorResult) => {
        setPickerColor(color.hex)
        setColor(color.hex)
    }

    return (
        <FloatingMenu context={context}>
            <div className={style.palette} onClick={closeColorPicker}>
                <div className={style.palette}>
                    <span>색상</span>
                    <IconButton onClick={() => context.setOpen(false)}>
                        <Close/>
                    </IconButton>
                </div>
                <div className={style.content}>
                    <span>최근에 사용한 색상</span>
                    <div>
                        <div className={style.colorBox}>
                            <IconButton
                                className={style.colorPicker}
                                onClick={() => handleClickPicker()}
                                props={{
                                    ref: ref,
                                    ...getReferenceProps()
                                }}
                            >
                                <Add/>
                            </IconButton>
                            <FloatingMenu context={menuContext}>
                                <div
                                    onMouseDown={(e) => e.stopPropagation()}
                                    onClick={(e) => e.stopPropagation()}
                                >
                                    <ChromePicker
                                        color={pickerColor}
                                        onChange={handlePickerChange}
                                        disableAlpha={true}
                                    />
                                </div>
                            </FloatingMenu>
                        </div>
                        {[displayPicker && drawColorBox(pickerColor, color, handleSetColor),
                            ...drawColorBoxes(recentUsedColor.query(), color, handleSetColor)]}
                    </div>
                    <span>기본 팔레트</span>
                    <div>
                        {drawColorBoxes(defaultColors, color, handleSetColor)}
                    </div>
                </div>
                <div className={style.footer}>
                    <div style={{ backgroundColor: color }}/>
                    <span>{color}</span>
                </div>
            </div>
        </FloatingMenu>
    )
}

export default Palette;