import { Routes, Route } from "react-router-dom";
import { AuthProvider } from "./components/AuthContext";
import Layout from "./pages/Layout";
import Home from "./pages/Home";
import About from "./pages/About";
import Blogs from "./pages/blogs/Blogs";
import Nutshell from "./pages/nutshell/Nutshell";
import History from "./pages/history/History";
import PhysicsNobelPrize from "./pages/history/PhysicsNobelPrize";
import PythonVsJava from "./pages/nutshell/PythonVsJava";
import NoPage from "./pages/NoPage";
import Editor from "./pages/Editor";
import Login from "./pages/Login";
import Profile from "./pages/Profile";
import "./App.css";

function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Home />} />
          <Route path="about" element={<About />} />
          <Route path="blogs" element={<Blogs />} />
          <Route path="nutshell" element={<Nutshell />} />
          <Route path="history" element={<History />} />
          <Route
            path="history/physics-nobel-prize"
            element={<PhysicsNobelPrize />}
          />
          <Route path="nutshell/python-vs-java" element={<PythonVsJava />} />
          <Route path="editor" element={<Editor />} />
          <Route path="*" element={<NoPage />} />
        </Route>
        {/* Authentication routes outside of Layout */}
        <Route path="/login" element={<Login />} />
        <Route path="/profile" element={<Profile />} />
      </Routes>
    </AuthProvider>
  );
}

export default App;
