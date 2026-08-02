const Banner = () => {
  return (
    <div className="hidden z-10 lg:flex flex-row fixed bottom-2 right-2 p-5 bg-[#faeed0] h-[75px] gap-3 justify-center items-center rounded-xl opacity-50 hover:opacity-100 duration-[500ms]">
      <p className="text-3xl">❗️ </p>
      <p className="">
        We are looking for contributors,
        <br /> please contact us if interested!
      </p>
      <a href="mailto:kwanstitution@gmail.com" className="underline">
        Email
      </a>
    </div>
  );
};

export default Banner;
