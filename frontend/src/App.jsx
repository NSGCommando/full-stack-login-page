import './App.css';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import UserDashboard from './pages/UserDashboard';
import AdminDashboard from './pages/AdminDashboard';
import SignUp from './pages/SignUp';

function App() {
  return(
    <Router>  
      <Routes>  
        <Route path="/" element = {<LoginPage/>}/>
        <Route path="/admin/dashboard" element = {<AdminDashboard/>}/>
        <Route path="/user/dashboard" element = {<UserDashboard/>}/>
        <Route path="/signup" element = {<SignUp/>}/>
      </Routes>
    </Router>
  )
 }

export default App;