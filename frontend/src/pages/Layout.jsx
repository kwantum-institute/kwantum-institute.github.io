import { Outlet } from "react-router-dom";
import Banner from "../components/Banner";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";

const Layout = () => {
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
