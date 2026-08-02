import React, { useState, useEffect } from "react";
import ReactQuill from "react-quill";
import "react-quill/dist/quill.snow.css";
import "./Editor.css";

function Editor() {
  const [value, setValue] = useState("");
  const [autoSaveEnabled, setAutoSaveEnabled] = useState(() => {
    // Check if the autosave toggle state is stored in localStorage
    const storedAutoSaveEnabled = localStorage.getItem("autoSaveEnabled");
    return storedAutoSaveEnabled ? JSON.parse(storedAutoSaveEnabled) : true;
  });
  const [isReset, setIsReset] = useState(false);
  const [articleTitle, setArticleTitle] = useState("");
  const [articleSubtitle, setArticleSubtitle] = useState("");
  const [selectedTopic, setSelectedTopic] = useState("");
  const [writerName, setWriterName] = useState("");
  const [writerEmail, setWriterEmail] = useState("");

  const topics = [
    "Educational Blogs",
    "Nutshell Knowledge",
    "History Celebration",
  ];

  useEffect(() => {
    // Load initial value from localStorage
    loadInitialData();
  }, []);

  useEffect(() => {
    // Save the current value to localStorage on every change
    saveDataToLocalStorage();

    // Save the autosave toggle state to localStorage
    localStorage.setItem("autoSaveEnabled", JSON.stringify(autoSaveEnabled));
  }, [
    value,
    articleTitle,
    articleSubtitle,
    selectedTopic,
    writerName,
    writerEmail,
    autoSaveEnabled,
  ]);

  const loadInitialData = () => {
    const savedValue = localStorage.getItem("editorValue");
    const savedTitle = localStorage.getItem("articleTitle");
    const savedSubtitle = localStorage.getItem("articleSubtitle");
    const savedTopic = localStorage.getItem("selectedTopic");
    const savedWriterName = localStorage.getItem("writerName");
    const savedWriterEmail = localStorage.getItem("writerEmail");

    if (savedValue) setValue(savedValue);
    if (savedTitle) setArticleTitle(savedTitle);
    if (savedSubtitle) setArticleSubtitle(savedSubtitle);
    if (savedTopic) setSelectedTopic(savedTopic);
    if (savedWriterName) setWriterName(savedWriterName);
    if (savedWriterEmail) setWriterEmail(savedWriterEmail);
  };

  const saveDataToLocalStorage = () => {
    if (autoSaveEnabled) {
      localStorage.setItem("editorValue", value);
      localStorage.setItem("articleTitle", articleTitle);
      localStorage.setItem("articleSubtitle", articleSubtitle);
      localStorage.setItem("selectedTopic", selectedTopic);
      localStorage.setItem("writerName", writerName);
      localStorage.setItem("writerEmail", writerEmail);
    }
  };

  const toggleAutoSave = () => {
    setAutoSaveEnabled((prevState) => {
      const newState = !prevState;
      localStorage.setItem("autoSaveEnabled", JSON.stringify(newState));
      return newState;
    });
  };

  const handleReset = () => {
    setValue("");
    setArticleTitle("");
    setArticleSubtitle("");
    setSelectedTopic("");
    setWriterName("");
    setWriterEmail("");
    setIsReset(true);
  };

  const handleSave = () => {
    localStorage.setItem("editorValue", value);
    localStorage.setItem("articleTitle", articleTitle);
    localStorage.setItem("articleSubtitle", articleSubtitle);
    localStorage.setItem("selectedTopic", selectedTopic);
    localStorage.setItem("writerName", writerName);
    localStorage.setItem("writerEmail", writerEmail);
  };

  const handleTopicChange = (e) => {
    setSelectedTopic(e.target.value);
  };

  return (
    <div className="my-[200px] flex flex-col items-center justify-center w-full">
      <p className="absolute w-full top-[120px] text-red-500 text-center">
        The publish button will not work for now, until we have implemented
        backend functionality.
      </p>
      <div className="flex flex-col w-1/2 gap-5">
        <h1 className="text-3xl font-black">Create Article</h1>
        <section className="w-full">
          <div className="flex items-center gap-3 mb-4 justify-between">
            <div className="flex gap-3 items-center">
              <select
                id="topic-select"
                value={selectedTopic}
                onChange={handleTopicChange}
                className="px-4 py-2 border border-gray-300 focus:outline-none rounded-full appearance-none pr-8 pl-4 custom-select-arrow"
              >
                <option value="">Select a topic</option>
                {topics.map((topic, index) => (
                  <option key={index} value={topic}>
                    {topic}
                  </option>
                ))}
              </select>
            </div>
            <div className="flex gap-3 items-center">
              <label>Auto Save</label>
              <div className="relative inline-block w-10 align-middle select-none">
                <input
                  type="checkbox"
                  name="toggle"
                  id="toggle"
                  className="checked:bg-blue-500 outline-none focus:outline-none right-4 checked:right-0 duration-200 ease-in absolute block w-6 h-6 rounded-full bg-white border-4 appearance-none cursor-pointer"
                  checked={autoSaveEnabled}
                  onChange={toggleAutoSave}
                />
                <label
                  htmlFor="toggle"
                  className="block overflow-hidden h-6 rounded-full bg-gray-300 cursor-pointer"
                ></label>
              </div>
              {!autoSaveEnabled && (
                <button
                  className="bg-green-100 hover:bg-green-200 text-green-500 py-2 px-4 rounded-full border border-green-500"
                  onClick={handleSave}
                >
                  Save
                </button>
              )}
              <button
                className="bg-red-100 hover:bg-red-200 py-2 px-4 rounded-full border text-red-500 border-red-500"
                onClick={handleReset}
              >
                Reset
              </button>
              <button className="bg-blue-500 hover:bg-blue-600 text-white py-2 px-4 rounded-full">
                Publish
              </button>
            </div>
          </div>
          <input
            type="text"
            placeholder="Article Title"
            value={articleTitle}
            onChange={(e) => setArticleTitle(e.target.value)}
            className="article-title w-full px-4 py-2 border border-b-0 border-gray-300 focus:outline-none text-7xl font-black"
          />
          <input
            type="text"
            placeholder="Article Subtitle"
            value={articleSubtitle}
            onChange={(e) => setArticleSubtitle(e.target.value)}
            className="text-3xl text-gray-500 w-full px-4 py-2 border border-gray-300 focus:outline-none"
          />
          <div className="flex">
            <input
              type="text"
              placeholder="Name/Nickname"
              value={writerName}
              onChange={(e) => setWriterName(e.target.value)}
              className="w-1/2 px-4 py-2 border-x border-gray-300 border-r-0 focus:outline-none"
            />
            <input
              type="email"
              placeholder="Email (hidden, for contact purposes)"
              value={writerEmail}
              onChange={(e) => setWriterEmail(e.target.value)}
              className="w-1/2 px-4 py-2 border-x border-[#e5e7eb] focus:outline-none"
            />
          </div>
          <ReactQuill
            theme="snow"
            value={value}
            onChange={setValue}
            placeholder="Add content here..."
          />
        </section>
      </div>
    </div>
  );
}

export default Editor;
