import {useState} from "react";
import {useNavigate} from "react-router-dom";
import TextInput from "../components/TextInput";
import SubmitButton from "../components/SubmitButton";
import "../styles/LoginPage.css"

function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("")
  const navigateObject = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();

    // call API here
    try {
      const response = await fetch("http://localhost:5000/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username: username, password: password }) // match Flask expected values
      });

      const data = await response.json(); // convert json string to object via parsing; assumes that backend ALWAYS RETURNS JSON

      if (response.ok) {
        setError("");
        console.log("Login successful!", data);
        navigateObject("/dashboard",{state:{
                            username: data.username, 
                            is_admin: data.is_admin
                            }});
      } else {
        setError(data.error || "Login failed");
      }
    } catch (err) {
      console.error("Network error:", err);
      setError("Network error");
    }
  }

  // Handle signup button click
  function handleSignUp(e){
    e.preventDefault();
    navigateObject("/signup");
  }

  return (
    <div className="login-container">
      <h2>Login Page</h2>

      <form onSubmit={handleSubmit}>
        <TextInput
          id = "username_input"
          label="Username"
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />

        <TextInput
          id = "password_input"
          label="Password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        <SubmitButton id="submit_button_login">Login</SubmitButton>
      </form>
      {/*If error has been set (truthy value) '&&' makes the expression default to the <p> element, making react render the error text
      If error is not set (falsy value), '&&' defaults to the preceding expression 'error' so react will not render the <p>*/}
      {error && <p style={{ color: "red", marginTop: "1rem" }}>{error}</p>}
      <div  className="signup-container">
        <button className="submit-button" onClick={handleSignUp}>Sign Up</button>
      </div>
    </div>
  );
}

export default LoginPage;