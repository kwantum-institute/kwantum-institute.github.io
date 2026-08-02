const Footer = () => {
  return (
    <div className="p-10 w-full flex flex-col bg-black justify-center items-center">
      <p className="text-white text-center">
        Kwantum Institute 2024 - All Rights Reserved.
      </p>
      <div className="flex flex-row gap-2">
        <a
          className="text-white underline"
          href="https://github.com/Kwantum-institute/kwantum-institute.github.io"
        >
          Github
        </a>
        <a
          className="text-white underline"
          href="https://github.com/Kwantum-institute/kwantum-institute.github.io"
        >
          Instagram
        </a>
      </div>
    </div>
  );
};

export default Footer;
