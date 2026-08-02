const Article = ({ topic, title, name, date, subtitle, content }) => {
  return (
    <div className="my-[200px] flex flex-col items-center justify-center w-full">
      <div className="flex flex-col w-3/4 lg:w-1/2 gap-7">
        <div className="flex flex-col gap-2">
          <h1 className="text-xl text-gray-400 uppercase">{topic}</h1>
          <h1 className="text-7xl font-black">{title}</h1>
          <h1 className="text-3xl text-gray-500">{subtitle}</h1>
          <h1>
            Written by {name} · Published {date}
          </h1>
        </div>
        <div className="flex h-[600px] w-full bg-black text-white items-center justify-center">
          Banner
        </div>
        {content}
      </div>
    </div>
  );
};

export default Article;
