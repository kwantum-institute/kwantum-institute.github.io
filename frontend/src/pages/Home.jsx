import Navbar3D from "../components/Navbar3D";
import Hero from "../components/Hero";

function Home() {
  return (
    <div className="relative flex flex-col items-center">
      <div className="bg bg-black"></div>
      <Navbar3D />
      <Hero />
    </div>
  );
}

export default Home;
