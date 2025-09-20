import { Link } from "react-router-dom";

const BlogPreview = ({ title, description, thumbnail, to }) => {
  return (
    <div className="blog">
      <div></div>
      <Link to={to}>{title}</Link>
      <p>{description}</p>
    </div>
  );
};

export default BlogPreview;
