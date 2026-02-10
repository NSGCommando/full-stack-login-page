import { useState } from "react";
import TextInput from "../components/TextInput";
import SubmitButton from "../components/SubmitButton";
import {customHeader} from "../utils/authUtils"
import { useNavigate } from "react-router-dom";

function SignUp(){
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const [signupStage, setSignupStage] = useState(1);
    const navigateObject = useNavigate(); // navigate hook

    async function checkUsernameSignUp(e){
        e.preventDefault();
        try{
            const response = await fetch("http://localhost:5000/check_username", 
                {method:"POST", 
                    headers:{"Content-Type": "application/json",
                            [customHeader.CUSTOM_HEADER_FRONTEND]: customHeader.CUSTOM_HEADER_FRONTEND_RESPONSE}, 
                        body:JSON.stringify({username:username})});
            if(response.status === 409){
                setError("Username is already taken. Please try another!")
            }
            else{setSignupStage(2);}
        }
        catch(err){
            console.error("Network error:", err);
            setError("Network error");
        }
    }

    async function handleFinalSignUp(e){
        e.preventDefault();
        try{
            const response = await fetch("http://localhost:5000/signup", {method:"POST", 
                                            headers:{"Content-Type": "application/json",
                                                    [customHeader.CUSTOM_HEADER_FRONTEND]: customHeader.CUSTOM_HEADER_FRONTEND_RESPONSE},  
                                            body:JSON.stringify({username:username, password:password})});
            const data = await response.json();
            if(response.status===201){
                setError("");
                console.log("Signup successful!");
                navigateObject("/",{replace:true})
            }
            else{
                console.log("Signup failed!");
                setError(data.error);
            }
        }
        catch(err){
            console.error("Network error:", err);
            setError("Network error");
        }
    }

    return (
        // Ensure to use 'className' and not 'classname'
        // tag or attribute mistakes leaves the render to be ignored, and no error warnings either
        // maybe think of making an html parser for this sort of things
        <div className="signup-container">
            <h1>Signup Page</h1>
            {
                signupStage===1? // conditional rendering using signupStage
                (<form id="signup-username-form" onSubmit={checkUsernameSignUp}>
                    <TextInput
                    id = "username_input"
                    label="Username"
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    />
                    <SubmitButton id="submit_button_signup_username">Enter</SubmitButton>
                </form>)
                :(
                    <form id="signup-password-form" onSubmit={handleFinalSignUp}>
                        <TextInput
                        id = "password_input"
                        label="Password"
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        />
                        <SubmitButton id="submit_button_signup_password">Enter</SubmitButton>
                    </form>
                ) 
            }
            
            {error && <p style={{ color: "red", marginTop: "1rem" }}>{error}</p>}
        </div>
    );
}

export default SignUp;