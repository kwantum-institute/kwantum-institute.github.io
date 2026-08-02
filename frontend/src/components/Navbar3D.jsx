import React from "react";
import "./Navbar3D.css";
import { Link } from "react-router-dom";

const Navbar3D = () => {
  const navLinks = [
    { text: "Educational Blogs", to: "/blogs", index: 3 },
    { text: "Nutshell Knowledge", to: "/nutshell", index: 2 },
    { text: "History Celebration", to: "/history", index: 1 },
  ];

  return (
    <div className="h-[600px] lg:h-[700px] mt-[145px] lg:mt-5 w-full flex flex-col relative justify-center items-center">
      <div className="relative lg:right-5 w-2/3 flex flex-col items-center">
        <Link
          to="/"
          className="relative gap-5 flex flex-col lg:flex-row mb-20 text-6xl lg:text-8xl text-center"
        >
          <div className="text-3d-right lg:hidden">
            <h1 className="text-[#faeed0] inline">Kwan</h1>
            <h1 className="text-blue-200 inline">tum</h1>
          </div>
          <div className="text-3d-left hidden lg:inline">
            <h1 className="text-[#faeed0] inline">Kwan</h1>
            <h1 className="text-blue-200 inline">tum</h1>
          </div>
          <div className="text-3d-right lg:hidden">Institute</div>
          <div className="text-3d-left hidden lg:inline">Institute</div>
        </Link>
        <ul className="navbar-3d">
          {navLinks.map(({ text, to, index }) => (
            <li key={index} style={{ "--i": index }}>
              <Link to={to}>
                <span>
                  <div>{text}</div>
                </span>
              </Link>
            </li>
          ))}
        </ul>
        <div className="absolute hidden-on-sm translate-x-[155px] translate-y-[150px] leading-[75px] text-3d-s text-6xl skew-y-[-15deg]">
          We
          <br />
          <p className="text-[#faeed0] inline">Write</p>
          <br />
          About
          <br />
          <p className="text-blue-200 inline">Science</p>
          <p className="absolute bottom-3 left-[250px] w-full text-xl inline text-red-100">
            and more!
          </p>
        </div>
      </div>
    </div>
  );
};

export default Navbar3D;
