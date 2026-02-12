import {ReactNode} from "react";
import './IconButton.css'

export interface IconButtonProps {
    children: ReactNode;
    onClick?: () => void;
}

const IconButton = ({ children, onClick }: IconButtonProps) => {
    return (
        <button
            className='IconButton'
            onClick={onClick}
        >
            {children}
        </button>
    )
}

export default IconButton;