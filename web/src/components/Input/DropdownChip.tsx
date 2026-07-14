import React, {useMemo, useRef, useState} from 'react';
import style from './DropdownChip.module.css';
import FloatingMenu from "../menu/FloatingMenu";
import useFloatingMenu from "../../hooks/useFloatingMenu";
import {RadioButtonList} from "./RadioButtonList";

export interface DropdownOption<T> {
    label: string;
    value: T;
}

interface DropdownChipProps<T> {
    options: DropdownOption<T>[]
    currentOption: T
    onOptionChange: (option: T) => void;
    className?: string
    icon?: boolean;
}

export function DropdownChip<T>({
                                    options,
                                    currentOption,
                                    onOptionChange,
                                    className,
                                    icon = true
} : DropdownChipProps<T>) {
    const [isOpen, setIsOpen] = useState(false);
    const {
        ref,
        getReferenceProps,
        menuContext
    } = useFloatingMenu(isOpen, setIsOpen);
    const currentLabel = useMemo(() => {
        for(let option of options)
            if(option.value === currentOption)
                return option.label

        return '오류!'
    }, [currentOption]);

    // TODO: Changes span icon to svg later
    return (
        <div className={style.dropdownChipContainer}>
            <button
                className={`${style.dropdownChip} ${isOpen ? style.open : ''} ${className??''}`}
                ref={ref}
                {...getReferenceProps()}
                type="button"
            >
                <span className={style.label}>{currentLabel}</span>
                {icon && <span className={style.icon}></span>}
            </button>
            {isOpen && <FloatingMenu context={menuContext}>
                <div className={style.optionList}>
                    <RadioButtonList
                        buttons={options}
                        currentOption={currentOption}
                        onOptionChange={onOptionChange}
                        variant={'none'}
                    />
                </div>
            </FloatingMenu>}
        </div>

    )
}