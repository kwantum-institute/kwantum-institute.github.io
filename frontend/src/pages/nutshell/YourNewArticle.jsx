import Section from "../Section";

function Name() {
  return (
    <Section
      title="About"
      content={
        <>
          <section>
            <h1 className="text-3xl font-black">Heading</h1>
            <p>Text</p>
          </section>
        </>
      }
    />
  );
}

export default Name;
