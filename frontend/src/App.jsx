import { Routes, Route, Outlet, Link } from "react-router-dom";
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
import "./App.css";

function App() {
  return (
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
    </Routes>
  );
}

export default App;
