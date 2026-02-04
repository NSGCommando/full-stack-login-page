import './App.css';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import Dashboard from './pages/Dashboard';
import SignUp from './pages/SignUp';

function App() {
  return(
    <Router>  
      <Routes>  
        <Route path="/" element = {<LoginPage/>}/>
        <Route path="/dashboard" element = {<Dashboard/>}/>
        <Route path="/signup" element = {<SignUp/>}/>
      </Routes>
    </Router>
  )
 }

export default App;