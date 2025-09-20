import { Link } from "react-router-dom";
import { useAuth } from "./AuthContext";
import { useState, useEffect } from "react";

const Navbar = () => {
  const { isAuthenticated, user, logout } = useAuth();
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isMobile, setIsMobile] = useState(window.innerWidth < 1250);

  const handleLogout = async () => {
    await logout();
    setShowUserMenu(false);
  };

  // Handle window resize to detect mobile/desktop
  useEffect(() => {
    const handleResize = () => {
      const mobile = window.innerWidth < 1250;
      setIsMobile(mobile);

      // Close mobile menu when switching to desktop view
      if (!mobile && isMobileMenuOpen) {
        setIsMobileMenuOpen(false);
      }
    };

    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, [isMobileMenuOpen]);

  // Close menus when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      // Close user menu if clicked outside
      if (showUserMenu && !event.target.closest(".user-menu-container")) {
        setShowUserMenu(false);
      }

      // Close mobile menu if clicked outside
      if (isMobileMenuOpen && !event.target.closest(".mobile-menu-container")) {
        setIsMobileMenuOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [showUserMenu, isMobileMenuOpen]);

  return (
    <nav className="fixed top-0 z-50 w-full p-4 bg-black flex flex-row items-center justify-between">
      <div className="flex items-center">
        <Link
          to="/"
          className="text-white text-xl md:text-2xl lg:text-3xl font-black"
          onClick={() => setIsMobileMenuOpen(false)}
        >
          <h1 className="text-[#faeed0] inline">Kwan</h1>
          <h1 className="text-blue-200 inline">tum</h1>
          <h1 className="inline"> Institute</h1>
        </Link>
      </div>

      {/* Desktop Navigation */}
      {!isMobile && (
        <div className="flex gap-5 items-center">
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
      )}

      <div className="flex gap-4 items-center">
        {!isMobile && (
          <>
            <a href="#" className="text-white hidden md:block">
              Support Us
            </a>
            <Link
              to="/editor"
              className="px-4 py-2 rounded-full bg-[#faeed0] hidden md:block"
            >
              Create Article
            </Link>
          </>
        )}

        {/* Authentication Section */}
        {isAuthenticated ? (
          <div className="user-menu-container relative">
            <button
              onClick={() => setShowUserMenu(!showUserMenu)}
              className="flex items-center gap-2 text-white hover:text-blue-200 transition-colors"
            >
              <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-white font-semibold">
                {user?.first_name?.charAt(0) ||
                  user?.username?.charAt(0) ||
                  "U"}
              </div>
              {!isMobile && (
                <span className="hidden md:inline">
                  {user?.first_name || user?.username}
                </span>
              )}
              <svg
                className={`w-4 h-4 transition-transform ${
                  showUserMenu ? "rotate-180" : ""
                }`}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M19 9l-7 7-7-7"
                />
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
        ) : !isMobile ? (
          <Link
            to="/login"
            className="px-4 py-2 rounded-full bg-blue-500 text-white hover:bg-blue-600 transition-colors"
          >
            Sign In
          </Link>
        ) : null}

        {/* Mobile Menu Button */}
        {isMobile && (
          <div className="mobile-menu-container ml-2">
            <button
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="text-white focus:outline-none"
              aria-label="Toggle menu"
            >
              {isMobileMenuOpen ? (
                <svg
                  className="w-6 h-6"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              ) : (
                <svg
                  className="w-6 h-6"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M4 6h16M4 12h16M4 18h16"
                  />
                </svg>
              )}
            </button>
          </div>
        )}
      </div>

      {/* Mobile Menu Overlay */}
      {isMobile && isMobileMenuOpen && (
        <div className="fixed top-16 left-0 w-full h-full bg-black bg-opacity-90 z-40">
          <div className="p-5 flex flex-col space-y-6 text-white">
            <ul className="flex flex-col gap-6 text-lg">
              <li>
                <Link to="/" onClick={() => setIsMobileMenuOpen(false)}>
                  Home
                </Link>
              </li>
              <li>
                <Link to="/about" onClick={() => setIsMobileMenuOpen(false)}>
                  About
                </Link>
              </li>
              <li>
                <Link to="/blogs" onClick={() => setIsMobileMenuOpen(false)}>
                  Educational Blogs
                </Link>
              </li>
              <li>
                <Link to="/nutshell" onClick={() => setIsMobileMenuOpen(false)}>
                  Nutshell Knowledge
                </Link>
              </li>
              <li>
                <Link to="/history" onClick={() => setIsMobileMenuOpen(false)}>
                  History Celebration
                </Link>
              </li>
            </ul>

            <div className="pt-4 border-t border-gray-700">
              <a href="#" className="block py-2">
                Support Us
              </a>
              <Link
                to="/editor"
                className="block my-4 px-5 py-3 rounded-full bg-[#faeed0] text-black text-center"
                onClick={() => setIsMobileMenuOpen(false)}
              >
                Create Article
              </Link>

              {!isAuthenticated ? (
                <Link
                  to="/login"
                  className="block my-4 px-5 py-3 rounded-full bg-blue-500 text-white text-center"
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  Sign In
                </Link>
              ) : (
                <div className="mt-4">
                  <div className="flex items-center gap-3 py-3">
                    <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center text-white font-semibold">
                      {user?.first_name?.charAt(0) ||
                        user?.username?.charAt(0) ||
                        "U"}
                    </div>
                    <span>{user?.first_name || user?.username}</span>
                  </div>
                  <Link
                    to="/profile"
                    className="block py-3 mt-2 text-blue-300"
                    onClick={() => setIsMobileMenuOpen(false)}
                  >
                    Profile Settings
                  </Link>
                  <button
                    onClick={() => {
                      handleLogout();
                      setIsMobileMenuOpen(false);
                    }}
                    className="block py-3 text-red-400"
                  >
                    Sign Out
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </nav>
  );
};

export default Navbar;
