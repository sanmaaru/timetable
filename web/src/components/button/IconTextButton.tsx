import style from './IconTextButton.module.css';
import {FC, SVGProps} from "react";

export interface IconTextButtonProps {
    icon: FC<SVGProps<SVGSVGElement>>;
    text: string;
    onClick?: () => void;
    color?: string;
    className?: string;
}

export const IconTextButton = ({
    icon: Icon,
    text,
    onClick,
    color,
    className,
}: IconTextButtonProps) => {
    return (
        <button
            className={`${style.iconTextButton} ${className??''}`}
            onClick={onClick}
        >
            <Icon style={{ fill: color }}/>
            <span style={{ color: color }}>{text}</span>
        </button>
    )
}