const Section = ({ title, content }) => {
  return (
    <div>
      <div className="mt-20 h-[300px] w-full flex-col justify-center">
        <div className="flex items-center justify-center h-full w-full bg-[url('./assets/earth_background.jpg')] bg-cover bg-center">
          <h1 className="text-7xl font-black text-white text-3d">{title}</h1>
        </div>
      </div>
      <div className="flex flex-col mt-[50px] mb-[190px] lg:mb-[250px] items-center justify-center w-full">
        <div className="flex flex-col w-3/4 lg:w-1/2 gap-7">{content}</div>
      </div>
    </div>
  );
};

export default Section;
