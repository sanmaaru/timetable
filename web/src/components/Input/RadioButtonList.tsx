import React, {ReactNode} from 'react';
import style from './RadioButtonList.module.css';

export interface RadioButton<T> {
    icon?: ReactNode;
    label: string;
    value: T;
}

type Variant = 'circle' | 'icon' | 'none';
interface RadioButtonListProps<T> {
    buttons: RadioButton<T>[]
    currentOption?: T;
    onOptionChange: (newOption: T) => void;
    className?: string;
    variant?: Variant;
}

export function RadioButtonList<T>({
    buttons,
    currentOption,
    onOptionChange,
    className,
    variant = 'circle',
} : RadioButtonListProps<T>){
    return (
        <div className={`${style.radioButtonList} ${className}`}>
            {buttons.map((button, index) => {
                const isChecked = currentOption === button.value;
                const labelClass = variant === 'circle'
                    ? style.circleLabel
                    : `${style.iconLabel} ${isChecked ? style.checkedIconLabel : ''}`

                return (
                    <label key={index} className={labelClass}>
                        <input
                            type="radio"
                            checked={isChecked}
                            onChange={() => onOptionChange(button.value)}
                            className={variant === 'circle' ? style.visibleRadio : style.hiddenRadio}
                        />
                        {variant === 'icon' && button.icon && <span className={style.icon}>{button.icon}</span>}
                        {button.label}
                    </label>
                )
            })}
        </div>
    )
}