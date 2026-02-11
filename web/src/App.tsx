import './App.css';
import React from 'react';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import  Home from './pages/Home';
import Login from "./pages/auth/Login";
import SignUp from "./pages/auth/SignUp";
import ProtectedRoute from "./auth/ProtectedRoute";
import Layout from "./pages/Layout";
import Theme from "./pages/theme/Theme";
import Account from "./pages/Account";
import ThemeView from "./pages/theme/ThemeView";
import ThemeEdit from "./pages/theme/ThemeEdit";

function App() {
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/login" element={<Login/>} />
                <Route path="/signup" element={<SignUp/>} />

                <Route element={<ProtectedRoute/>}>
                    <Route element={<Layout/>}>
                        <Route path="/" element={<Home/>}/>
                        <Route path="/theme" element={<Theme/>}/>
                        <Route path="/theme/:themeId" element={<ThemeView/>}></Route>
                        <Route path="/theme/:themeId/edit" element={<ThemeEdit/>}></Route>
                        <Route path="/account" element={<Account/>}/>
                    </Route>
                </Route>
            </Routes>
        </BrowserRouter>
    );
}

export default App
