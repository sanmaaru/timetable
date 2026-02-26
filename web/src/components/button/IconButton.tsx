import {ReactNode} from "react";
import style from './IconButton.module.css'

export interface IconButtonProps {
    children: ReactNode;
    onClick?: () => void;
    className?: string;
    title?: string;
    props?: Record<string, unknown>;
}

const IconButton = ({ children, onClick, className, title, props }: IconButtonProps) => {
    return (
        <button
            className={`${className} ${style.iconButton}`}
            onClick={onClick}
            title={title}
            {...props}
        >
            {children}
        </button>
    )
}

export default IconButton;