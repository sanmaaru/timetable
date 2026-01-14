import './App.css';
import React from 'react';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import  Home from './pages/Home';
import Login from "./pages/Login";
import SignUp from "./pages/SignUp";
import ProtectedRoute from "./auth/ProtectedRoute";

function App() {
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/login" element={<Login/>} />
                <Route path="/signup" element={<SignUp/>} />

                <Route element={<ProtectedRoute/>}>
                    <Route path="/" element={<Home/>}/>
                </Route>
            </Routes>
        </BrowserRouter>
    );
}

export default App
