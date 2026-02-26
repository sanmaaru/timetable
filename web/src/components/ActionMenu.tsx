import React, {FC, SVGProps} from "react";
import style from './ActionMenu.module.css'
import {FloatingContext, FloatingFocusManager, FloatingPortal, useTransitionStyles} from "@floating-ui/react";
import {FloatingMenuContext} from "../hooks/useFloatingMenu";
import FloatingMenu from "./menu/FloatingMenu";

export interface ActionMenuButton {
    icon: FC<SVGProps<SVGSVGElement>>;
    text: string;
    onClick: () => void;
    color?: string | undefined;
}

interface ActionMenuProps {
    buttons: ActionMenuButton[];
    context: FloatingMenuContext;
}

const ActionMenu = ({
                        buttons, context
}: ActionMenuProps) => {
    const menuButtons = buttons.map((value, index) => {
        return <button
            className={style.button}
            key={index}
            onClick={value.onClick}
        >
            <value.icon style={{ fill: value.color }}/>
            <span style={{ color: value.color }}>{value.text}</span>
        </button>
    })

    if(!context.isMounted) return null;

    return (
        <FloatingMenu context={context}>
            <div className={style.actionMenu}>
                {menuButtons}
            </div>
        </FloatingMenu>
    )
}

export default ActionMenu;