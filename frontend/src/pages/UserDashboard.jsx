import { useLocation,Link,useNavigate } from "react-router-dom";

function UserDashboard(){
    // navigate hook
    const navigateObject = useNavigate();
    // Logout function
    function handleLogout(e){
        e.preventDefault();
        navigateObject("/",{replace:true});
    }
    const location = useLocation()
    // If user tries to return to dashboard without using Login button and login creds, block them
    // Also ensures back button of browser doesn't expose dashboard
    if(!location.state){
        return(
            <div style={{ textAlign: "center", marginTop: "50px" }}>
                <h2>Unauthorized Access</h2>
                <p>Please log in to view your dashboard.</p>
                <Link to="/" replace={true} style={{ color: "blue", textDecoration: "underline" }}>
                    Go to Login
                </Link>
            </div>
        )
    }
    const { username } = location.state || {}
    return(
        <div id="dashboard-container">
        <h1>Dashboard</h1>
            <p>Login was successful, User {username}</p>
            {/* Logout button*/}
            <div id="logout-container">
                <button onClick={handleLogout}>Logout</button>
            </div>
        </div>
        

    )
}

export default UserDashboard;