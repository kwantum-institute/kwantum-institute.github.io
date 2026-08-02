import { Link } from "react-router-dom";

function NoPage() {
  return (
    <div className="h-screen flex flex-col items-center justify-center w-full">
      <div className="flex flex-col w-3/4 lg:w-1/2 gap-7">
        <h1 className="text-6xl font-black">Page not found!</h1>
        <p>
          Unfortunately, the page you're looking for doesn't exist or there was
          an error in the link you followed or typed.
        </p>
        <Link className="button" to="/">
          Return to Homepage
        </Link>
      </div>
    </div>
  );
}

export default NoPage;
