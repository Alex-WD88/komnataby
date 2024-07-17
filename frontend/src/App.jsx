import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import {BrowserRouter, Routes, Route} from 'react-router-dom'
import Home from './components/home';
import Login from "./components/login";
import Logout from './components/logout';
import Navigate from './components/navigate'
import Register from './components/register'

function App() {
  return (
    <BrowserRouter>
        <Navigate></Navigate>
        <Routes>
          <Route path="/" element={<Home/>}/>
          <Route path="/login" element={<Login/>}/>
          <Route path="/logout" element={<Logout/>}/>
          <Route path="/register" element={<Register/>}/>
        </Routes>
      </BrowserRouter>
  )
}

export default App