import BlogPreview from "../pages/BlogPreview";

const Hero = () => {
  return (
    <div className="flex sm:w-3/4 mt-10 mb-[200px] items-center">
      <div className="flex flex-col gap-10 w-full pt-10 lg:w-2/3 bg-gray-700 h-[2000px] lg:skew-y-[-15deg] sm:border-8">
        <h1 className="mx-10 lg:mx-20 text-center text-5xl lg:text-6xl text-3d-s skew-y-0 font-black">
          Our Top Picks of the Day
        </h1>
        <section className="mx-20 flex flex-col gap-10 text-white">
          <BlogPreview
            title="Java vs Python"
            description="Documentation comparing Java and Python programming languages."
            thumbnail=""
            to=""
          />
          <BlogPreview
            title="Dragon Repeller RPG"
            description="An interactive RPG game where you must defeat the dragon
              preventing people from leaving the town."
            thumbnail=""
            to=""
          />
          <BlogPreview
            title="Java Platform Game Project"
            description="An interactive platform game where you must avoid obstacles."
            thumbnail=""
            to=""
          />
        </section>
      </div>
      <div className="hidden lg:flex pt-10 w-2/3 bg-gray-600 h-[2000px] skew-y-[15deg] border-8"></div>
    </div>
  );
};

export default Hero;
