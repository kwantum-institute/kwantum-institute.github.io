import Navbar3D from "../components/Navbar3D";
import Hero from "../components/Hero";
import ScienceSearch from "../components/ScienceSearch";

function Home() {
  return (
    <div className="relative flex flex-col items-center">
      <div className="bg bg-black"></div>
      <Navbar3D />
      <ScienceSearch />
      <Hero />
    </div>
  );
}

export default Home;
