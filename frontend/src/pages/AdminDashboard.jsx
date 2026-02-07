import { useState, useEffect } from "react";
import { useLocation,useNavigate } from "react-router-dom";
import { clearSessionData } from "../utils/authUtils";
import "../styles/AdminDashboard.css"

function AdminDashboard(){
    // navigate(routing) and location(state) hook
    const navigateObject = useNavigate();
    const location = useLocation();
    // admin dashboard states
    const [userList, setUserList] = useState([]) // set initial vaflue to [] so the userList.map() doesn't crash on first render
    const [error, setError] = useState("");
    const [isAdmin] = useState(!!location.state?.is_admin || false);
    const { username:adminUsername } = location.state || {};
    // kick out if page refreshes or url is manually typed or user isn't admin
    useEffect(()=>{
        clearSessionData();
        if(!isAdmin){
            navigateObject("/",{replace:true});
        }
    },[isAdmin,navigateObject])
    
    // Logout function
    function handleLogout(){
        navigateObject("/",{replace:true}); // 'replace' means
    }

    // delete user function
    async function deleteUser(targetName){
        // handle user deletion
        try{
            const response = await fetch("http://localhost:5000/api/users",
                                        {   method:"DELETE", 
                                            headers:{"Content-Type":"application/json"},
                                            body:JSON.stringify({target_name:targetName}),
                                            credentials:"include" // JWT token for verification
                                        })
            if(response.ok){
                setUserList(prevList => prevList.filter(user=>user.user_name!==targetName)) // prevList is declared right here
                // to apply the filter on most recent version of userList stored in RAM
                // we only named prevList so as to apply the filter to the data
            }
            else{setError("deletion failed")}
        }
        catch(err){
            setError("Network error", err)
        }
    }
    
    async function showUsers(){
        try{
                const response = await fetch("http://localhost:5000/api/users",{
                    method:"GET",
                    headers:{"Content-Type":"application/json"},
                    credentials:"include" // JWT token for verification
                })
                const data = await response.json();
                if(response.ok){setUserList(data.users)}
                else{setError(data.error)}
        }
        catch(err){
            setError("Network error", err)
        }
    }
    return(
        <div id="dashboard-container">
            <h1>Admin Dashboard</h1>
            {error && <div className="error-banner">{error}</div>}
                <p>Login was successful, Admin {adminUsername}</p>
                    <button onClick={showUsers}>View Users</button>
                    {/* display user list, giving a style to div is needed to reserve space below the view button, 
                        or the table would be sent below everything else */}
                    <div className = "user-list-container"> 
                        {userList.length>0?
                        (   <table>
                                <thead>
                                    <tr>
                                        <th>User iD</th>
                                        <th>Username</th>
                                        <th>Role</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {userList.map((user)=>(
                                        <tr key={user.id}>
                                            <td>{user.id}</td>
                                            <td>{user.user_name}</td>
                                            <td>{user.is_admin?"Admin":"User"}</td>
                                            <td> 
                                                {/* don't allow admins to delete admins*/}
                                                {!user.is_admin?(
                                                    <button className="user-delete-button" onClick={()=>deleteUser(user.user_name)}>
                                                    Delete
                                                    </button>
                                                ):
                                                (<span>Protected</span>)
                                                }
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        ):
                        (<p>No users loaded</p>)
                        }
                    </div>

            {/* Logout button*/}
            <div id="logout-container">
                <button onClick={handleLogout}>Logout</button>
            </div>
        </div>
        

    )
}

export default AdminDashboard;