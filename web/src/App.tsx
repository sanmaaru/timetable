import React from 'react';
import {createBrowserRouter, RouterProvider} from 'react-router-dom';

import Login from './pages/auth/Login';
import SignUp from './pages/auth/SignUp';
import Home from './pages/Home';
import Themes from './pages/theme/Themes';
import ThemeView from './pages/theme/ThemeView';
import ThemeEdit from './pages/theme/ThemeEdit';
import Account from './pages/Account';
import ProtectedRoute from './auth/ProtectedRoute';
import Layout from './layouts/Layout';
import {recentUsedColor} from "./util/storage";
import ContextProvidingLayout from "./layouts/ContextProvidingLayout";

const router = createBrowserRouter([
    {
        element: <ContextProvidingLayout/>,
        children: [
            {
                path: "/login",
                element: <Login />,
            },
            {
                path: "/signup",
                element: <SignUp />,
            },
            {
                element: <ProtectedRoute/>,
                children: [
                    {
                        element: <Layout/>,
                        children: [
                            {
                                path: "/",
                                element: <Home />,
                            },
                            {
                                path: "/theme",
                                element: <Themes />,
                            },
                            {
                                path: "/theme/:themeId",
                                element: <ThemeView />,
                            },
                            {
                                path: "/theme/:themeId/edit",
                                element: <ThemeEdit />,
                            },
                            {
                                path: "/account",
                                element: <Account />,
                            },
                        ],
                    },
                ],
            }
        ]
    }
]);

function App() {
    recentUsedColor.init()
    return <RouterProvider router={router} />;
}

export default App;

