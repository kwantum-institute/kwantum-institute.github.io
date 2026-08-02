import Section from "../Section";
import BlogPreview from "../BlogPreview";

function History() {
  return (
    <Section
      title="History Celebration"
      content={
        <>
          <section>
            <h1 className="text-3xl font-black">Heading</h1>
            <p>Text</p>
          </section>
          <section className="grid sm:grid-cols-2 gap-3 lg:gap-4">
            <BlogPreview
              title="Physics Nobel Prize"
              description="Documentation comparing Java and Python programming languages."
              thumbnail=""
              to="physics-nobel-prize"
            />
            <BlogPreview
              title="Blog"
              description="Documentation comparing Java and Python programming languages."
              thumbnail=""
              to=""
            />
            <BlogPreview
              title="Blog"
              description="Documentation comparing Java and Python programming languages."
              thumbnail=""
              to=""
            />
            <BlogPreview
              title="Blog"
              description="Documentation comparing Java and Python programming languages."
              thumbnail=""
              to=""
            />
          </section>
        </>
      }
    />
  );
}

export default History;
