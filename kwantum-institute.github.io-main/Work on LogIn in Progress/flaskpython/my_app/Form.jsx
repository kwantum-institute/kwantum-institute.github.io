import { useState } from "react";
import api from "../api";
import { useNavigate } from "react-router-dom";
import { ACCESS_TOKEN, REFRESH_TOKEN } from "../constants";
import "../styles/Form.css"
import LoadingIndicator from "./LoadingIndicator";

function Form({ route, method }) {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const name = method === "login" ? "Login" : "Register";

    const handleSubmit = async (e) => {
        setLoading(true);
        e.preventDefault();

        try {
            const res = await api.post(route, { username, password })
            if (method === "login") {
                localStorage.setItem(ACCESS_TOKEN, res.data.access);
                localStorage.setItem(REFRESH_TOKEN, res.data.refresh);
                navigate("/")
            } else {
                navigate("/login")
            }
        } catch (error) {
            alert(error)
        } finally {
            setLoading(false)
        }
    };

    return (
        <form onSubmit={handleSubmit} className="form-container">
            <h1>{name}</h1>
            <input
                className="form-input"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Username"
            />
            <input
                className="form-input"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Password"
            />
            {loading && <LoadingIndicator />}
            <button className="form-button" type="submit">
                {name}
            </button>
        </form>
    );
}
const [passwordValid, setPasswordValid] = useState(false);
const [passwordError, setPasswordError] = useState('');
const validatePassword = (password) => {
  const minLength = 8;
  const hasUpperCase = /[A-Z]/.test(password);
  const hasLowerCase = /[a-z]/.test(password);
  const hasNumber = /\d/.test(password);
  const hasSpecialChar = /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]+/.test(password);

  if (password.length < minLength) {
    setPasswordError('Password must be at least 8 characters long');
    return false;
  }

  if (!(hasUpperCase && hasLowerCase && hasNumber && hasSpecialChar)) {
    setPasswordError('Password must contain uppercase, lowercase, number, and special character');
    return false;
  }

  setPasswordError('');
  return true;
};
const handleChange = (e) => {
  const { name, value } = e.target;
  setFormData({ ...formData, [name]: value });

  if (name === 'password') {
    const isValid = validatePassword(value);
    setPasswordValid(isValid);
  }
};
<input
  type="password"
  name="password"
  value={formData.password}
  onChange={handleChange}
  required
/>
{passwordError && <p className="error">{passwordError}</p>}
const handleSubmit = (e) => {
  e.preventDefault();
  if (!passwordValid) {
    alert('Please enter a valid password');
    return;
  }
  // Rest of other submission logic
};
export default Form