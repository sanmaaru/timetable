import { FloatingFocusManager, FloatingPortal } from "@floating-ui/react";
import React from "react";
import {FloatingMenuContext} from "../../hooks/useFloatingMenu";

interface FloatingMenuProps {
    children?: React.ReactNode;
    context: FloatingMenuContext;
}

const FloatingMenu = ({ children, context }: FloatingMenuProps) => {
    if (!context.isMounted)
        return

     return (<FloatingPortal>
           <FloatingFocusManager context={context.context} modal={false}>
               <div ref={context.ref}
                style={context.styles}
                {...context.floatingProps()}
           >
               {children}
           </div>
       </FloatingFocusManager>
   </FloatingPortal>)
}

export default FloatingMenu;