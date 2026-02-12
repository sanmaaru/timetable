import React, {forwardRef, useRef} from 'react';
import './Palette.css';
import {FloatingFocusManager, FloatingPortal} from "@floating-ui/react";
import {recentUsedColor} from "../../util/cookies";
import {shade} from "../../util/color";
import {defaultColors} from "../../constants/colors";
import Close from '../../resources/icon/icn_close.svg?react';
import Add from '../../resources/icon/icn_add.svg?react';
import IconButton from "../button/IconButton";

interface PaletteProps {
    context: PaletteContext;
    color: string;
    setColor: (color: string) => void;
}

interface PaletteContext {
    isMounted: boolean;
    setOpen: (open: boolean) => void;
    styles: React.CSSProperties;
    getFloatingProps: () => Record<string, unknown>;
    context: any;
}

const drawColorBoxes = (colors: string[], selected: string, handleSetColor: (color: string) => void) => {
    return colors.map((color, index) => (
        <div
            key={`${index}-${color}`}
            className={`color-box ${selected === color ? 'selected' : ''}`}
            style={{
                backgroundColor: color,
                border: `0.25px solid ${shade(color, 0.1)}`,
            }}
            onClick={() => handleSetColor(color)}
        />
    ))
}

const Palette = forwardRef<HTMLDivElement, PaletteProps>((props, ref) => {
    const { color, setColor } = props;
    const { setOpen, isMounted, context, styles, getFloatingProps } = props.context;

    if (!isMounted)
        return null;

    const colorPickerRef = useRef<HTMLInputElement>(null);

    const handleClickPicker = () => {
        colorPickerRef.current?.click();
    }

    const handleSetColor = (color: string) => {
        setColor(color);
        recentUsedColor.append(color);
    }

    console.log(recentUsedColor.query());

    return (
        <FloatingPortal>
            <FloatingFocusManager context={context} modal={false}>
                <div
                    className='Palette'
                    ref={ref}
                    style={styles}
                    {...getFloatingProps()}
                >
                    <div className='header'>
                        <span>색상</span>
                        <IconButton onClick={() => setOpen(false)}>
                            <Close/>
                        </IconButton>
                    </div>
                    <div className='content'>
                        <span>최근에 사용한 색상</span>
                        <div>
                            <div className='color-picker' onClick={handleClickPicker}>
                                <Add/>
                            </div>
                            <input
                                ref={colorPickerRef}
                                type='color'
                                value={color}
                                style={{ display: 'none' }}
                            />
                            {drawColorBoxes(recentUsedColor.query(), color, handleSetColor)}
                        </div>
                        <span>기본 팔레트</span>
                        <div>
                            {drawColorBoxes(defaultColors, color, handleSetColor)}
                        </div>
                    </div>
                    <div className='footer'>
                        <div style={{ backgroundColor: color }}/>
                        <span>{color}</span>
                    </div>
                </div>
            </FloatingFocusManager>
        </FloatingPortal>
    )
})

export default Palette;