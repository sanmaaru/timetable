import React, {forwardRef} from 'react';
import './Palette.css';
import {
    autoUpdate,
    flip,
    FloatingFocusManager,
    FloatingPortal,
    offset,
    shift, useClick,
    useDismiss,
    useFloating, useInteractions
} from "@floating-ui/react";
import {recentUsedColor} from "../../util/cookies";
import {shade} from "../../util/color";
import {defaultColors} from "../../constants/colors";
import Close from '../../resources/icon/icn_close.svg?react';
import Add from '../../resources/icon/icn_add.svg?react';
import IconButton from "../button/IconButton";
import {ChromePicker, ColorResult} from "react-color";

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

const drawColorBox = (color: string, selected: string, handleSetColor: (color: string) => void, key?: string) => {
    return <div
        key={key}
        className={`color-box ${selected === color ? 'selected' : ''}`}
        style={{
            backgroundColor: color,
            border: `0.25px solid ${shade(color, 0.1)}`,
        }}
        onClick={() => handleSetColor(color)}
    />
}

const drawColorBoxes = (colors: string[], selected: string, handleSetColor: (color: string) => void) => {
    return colors.map((color, index) => (
        drawColorBox(color, selected, handleSetColor, `${index}-${color}`)
    ))
}

const Palette = forwardRef<HTMLDivElement, PaletteProps>((props, ref) => {
    const { color, setColor } = props;
    const { setOpen, isMounted, context, styles, getFloatingProps } = props.context;
    const [displayPicker, setDisplayPicker] = React.useState(false);

    const handleClickPicker= () => {
        if (displayPicker) {
            handleSetColor(color);
            setDisplayPicker(false);
        } else {
            setPickerColor(color);
            setDisplayPicker(true);
        }
    }

    const [pickerColor, setPickerColor] = React.useState(color);
    const {
        refs: pickerRefs,
        floatingStyles: pickerStyles,
        context: pickerContext
    } = useFloating({
        open: displayPicker,
        onOpenChange: handleClickPicker,
        placement: 'bottom-start',
        middleware: [
            offset(10),
            flip(),
            shift()
        ],
        whileElementsMounted: autoUpdate
    })

    const dismiss = useDismiss(pickerContext, {
        bubbles: false,
        outsidePressEvent: 'mousedown'
    })
    const click = useClick(pickerContext)
    const { getReferenceProps, getFloatingProps: getPickerFloatingProps } = useInteractions([ dismiss, click ])

    if (!isMounted)
        return null;

    const handleSetColor = (color: string) => {
        setColor(color);
        recentUsedColor.append(color);
    }

    const handlePickerChange = (color: ColorResult) => {
        setPickerColor(color.hex)
        setColor(color.hex)
    }


    return (
        <FloatingPortal>
            <FloatingFocusManager context={context} modal={false}>
                <div
                    className='Palette'
                    ref={ref}
                    style={styles}
                    {...getFloatingProps()}
                    onClick={handleClickPicker}
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
                            <div className='color-picker'>
                                <div
                                    ref={pickerRefs.setReference}
                                    {...getReferenceProps()}
                                    style={{ display: 'inline' }}
                                >
                                    <IconButton>
                                        <Add/>
                                    </IconButton>
                                </div>
                                {displayPicker && (
                                    <FloatingPortal>
                                        <div
                                            ref={pickerRefs.setFloating}
                                            style={{
                                                ...pickerStyles,
                                                zIndex: 9999
                                            }}
                                            {...getPickerFloatingProps()}
                                            onMouseDown={(e) => e.stopPropagation()}
                                            onClick={(e) => e.stopPropagation()}
                                        >
                                            <ChromePicker
                                                color={pickerColor}
                                                onChange={handlePickerChange}
                                                disableAlpha={true}
                                            />
                                        </div>
                                    </FloatingPortal>
                                )}
                            </div>
                            {[displayPicker && drawColorBox(pickerColor, color, handleSetColor),
                                ...drawColorBoxes(recentUsedColor.query(), color, handleSetColor)]}
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