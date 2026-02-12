import { useNavigate } from "react-router-dom";
import { customHeader } from "../utils/authUtils";

function UserDashboard({user,setUser}){
    // navigate hook
    const navigateObject = useNavigate();
    // Logout function
    async function handleLogout(e){
            e.preventDefault();
            try {
                await fetch("http://localhost:5000/logout", // Cookie invalid, inform the server 
                    {
                    method: "GET",
                    headers:{   "Content-Type": "application/json",
                                [customHeader.CUSTOM_HEADER_FRONTEND]:customHeader.CUSTOM_HEADER_FRONTEND_RESPONSE
                            },
                    credentials: "include" 
                });
            } 
            catch {console.log("Server logout failed, but clearing local state anyway.");} 
            finally {
                setUser(null);
                navigateObject("/", { replace: true });
            }
        }
    return(
        <div id="dashboard-container">
        <h1>Dashboard</h1>
            <p>Login was successful, User {user.user_name}</p>
            {/* Logout button*/}
            <div id="logout-container">
                <button onClick={handleLogout}>Logout</button>
            </div>
        </div>
    )
}

export default UserDashboard;