import React, {FC, SVGProps} from "react";
import './ActionMenu.css'
import {FloatingContext, FloatingFocusManager, FloatingPortal} from "@floating-ui/react";

export interface ActionMenuButton {
    icon: FC<SVGProps<SVGSVGElement>>;
    text: string;
    onClick: () => void;
    color: string | undefined;
}

interface ActionMenuProps {
    context: FloatingContext;
    setFloating: any;
    floatingMenuProps: Record<string, unknown>;
    floatingStyles: React.CSSProperties;
    buttons: ActionMenuButton[];
}

const ActionMenu = ({
                        context,
                        setFloating,
                        floatingMenuProps,
                        floatingStyles,
                        buttons
}: ActionMenuProps) => {
    const menuButtons = buttons.map((value, index) => {
        return <button
            key={index}
            onClick={value.onClick}
        >
            <value.icon style={{ fill: value.color }}/>
            <span style={{ color: value.color }}>{value.text}</span>
        </button>
    })

    return (<FloatingPortal>
        <FloatingFocusManager context={context} modal={false}>
            <div
                className='action-menu'
                ref={setFloating}
                style={floatingStyles}
                {...floatingMenuProps}
            >
                {menuButtons}
            </div>
        </FloatingFocusManager>
    </FloatingPortal>)
}

export default ActionMenu;