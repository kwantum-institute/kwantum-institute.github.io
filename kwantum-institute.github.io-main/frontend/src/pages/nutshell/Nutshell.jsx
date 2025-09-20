import Section from "../Section";
import BlogPreview from "../BlogPreview";

function Nutshell() {
  return (
    <Section
      title="Nutshell Knowledge"
      content={
        <>
          <section>
            <h1 className="text-3xl font-black">Heading</h1>
            <p>Text</p>
          </section>
          <section className="grid sm:grid-cols-2 gap-3 lg:gap-4">
            <BlogPreview
              title="Python vs Java: A Brief Comparison"
              description="Documentation comparing Java and Python programming languages."
              thumbnail=""
              to="python-vs-java"
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

export default Nutshell;
