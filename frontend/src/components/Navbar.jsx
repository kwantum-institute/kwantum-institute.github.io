import { Link } from "react-router-dom";

const Navbar = () => {
  return (
    <nav className="fixed top-0 z-10 w-full p-5 bg-black flex flex-row items-center justify-between">
      <div className="flex gap-5 items-center">
        <Link to="/" className="text-white text-3xl font-black">
          <h1 className="text-[#faeed0] inline">Kwan</h1>
          <h1 className="text-blue-200 inline">tum</h1>
          <h1 className="inline"> Institute</h1>
        </Link>
        <ul className="flex flex-row gap-4 text-white">
          <li className="text-gray-400">
            <Link to="/">Home</Link>
          </li>
          <li className="text-gray-400">
            <Link to="/about">About</Link>
          </li>
          <li>
            <Link to="/blogs">Educational Blogs</Link>
          </li>
          <li>
            <Link to="/nutshell">Nutshell Knowledge</Link>
          </li>
          <li>
            <Link to="/history">History Celebration</Link>
          </li>
        </ul>
      </div>
      <div className="flex gap-5 items-center">
        <a href="" className="text-white">
          Support Us
        </a>
        <Link to="/editor" className="px-5 py-2 rounded-full bg-[#faeed0]">
          Create Article
        </Link>
      </div>
    </nav>
  );
};

export default Navbar;
