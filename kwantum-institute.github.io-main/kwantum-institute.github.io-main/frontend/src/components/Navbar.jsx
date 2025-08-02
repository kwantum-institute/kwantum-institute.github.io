import { Link } from "react-router-dom";
import { useAuth } from "./AuthContext";
import { useState } from "react";

const Navbar = () => {
  const { isAuthenticated, user, logout } = useAuth();
  const [showUserMenu, setShowUserMenu] = useState(false);

  const handleLogout = async () => {
    await logout();
    setShowUserMenu(false);
  };

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
        
        {/* Authentication Section */}
        {isAuthenticated ? (
          <div className="relative">
            <button
              onClick={() => setShowUserMenu(!showUserMenu)}
              className="flex items-center gap-2 text-white hover:text-blue-200 transition-colors"
            >
              <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-white font-semibold">
                {user?.first_name?.charAt(0) || user?.username?.charAt(0) || 'U'}
              </div>
              <span className="hidden md:inline">
                {user?.first_name || user?.username}
              </span>
              <svg
                className={`w-4 h-4 transition-transform ${showUserMenu ? 'rotate-180' : ''}`}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>
            
            {showUserMenu && (
              <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-20">
                <Link
                  to="/profile"
                  className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  onClick={() => setShowUserMenu(false)}
                >
                  Profile Settings
                </Link>
                <button
                  onClick={handleLogout}
                  className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                >
                  Sign Out
                </button>
              </div>
            )}
          </div>
        ) : (
          <Link
            to="/login"
            className="px-5 py-2 rounded-full bg-blue-500 text-white hover:bg-blue-600 transition-colors"
          >
            Sign In
          </Link>
        )}
      </div>
    </nav>
  );
};

export default Navbar;
