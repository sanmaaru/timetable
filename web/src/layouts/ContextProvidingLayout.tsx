import {ToastProvider} from "../components/alert/toast/ToastContext";
import {DialogProvider} from "../components/alert/dialog/DialogProvider";
import {Outlet} from "react-router-dom";

const ContextProvidingLayout = () => {
    return (<ToastProvider>
        <DialogProvider>
            <Outlet/>
        </DialogProvider>
    </ToastProvider>)
}

export default ContextProvidingLayout