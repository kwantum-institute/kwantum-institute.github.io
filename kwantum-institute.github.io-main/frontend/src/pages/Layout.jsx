import { Outlet } from "react-router-dom";
import Banner from "../components/Banner";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import { useAuth } from "../components/AuthContext";

const Layout = () => {
  const { isAuthenticated, user, logout } = useAuth();

  return (
    <>
      <Banner />
      <Navbar />
      <div className="flex flex-col h-screen justify-between">
        <Outlet />
        <Footer />
      </div>
    </>
  );
};

export default Layout;
