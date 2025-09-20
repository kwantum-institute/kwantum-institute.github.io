import Section from "./Section";

function About() {
  return (
    <Section
      title="About"
      content={
        <>
          <section>
            <h1 className="text-3xl font-black">Our Origins</h1>
            <p>
              Founded in the summer of 2023 by a group of Hong Kong students, we
              hope to share some of our knowledge on various expertise and
              kickstart exchanges with others across the globe that enhances all
              of our understandings. Hence, our name is a portmanteau of the
              Chinese word "Kwan" (關), meaning care, with the word "Quantum",
              as quantum mechanics is the current best model for the fundamental
              truth of reality.{" "}
            </p>
          </section>
          <section>
            <h1 className="text-3xl font-black">Mission Statement</h1>
            <p>
              "If you want to master something, teach it." ~ Richard Feynman
              <br />
              <br />
              A dedicated and dynamic student-led initiative, the Kwantum
              Institute aims to teach others on various academic topics using
              forms of blogs to more serious planned series of articles. To us
              (Timothy especially), Richard Feynman serves as an inspiration for
              this sharing and exchanging of knowledge. Success is not merely
              about scientific breakthroughs, it is how the breakthrough is
              communicated to the general public so that the body of knowledge
              could be expanded.
              <br />
              <br />
              More importantly, we promote teaching and research as teaching is
              the best form of learning. The institute therefore yearns to
              encourage communities across different countries to explore our
              universe's secrets. Despite our Hongkonger origins and perhaps a
              tad leant towards STEM subjects, we consist of students from
              diverse backgrounds. We are thus unified by our unwavering
              interest in this encompassing knowledge across all disciplines
              that we so passionately explore.
              <br />
              <br />
              From a wide range of subjects such as quantum physics to computer
              science to philosophy to history (more science-y related ones), we
              have articles that tackle both theoretical and practical topics.
              Various writers among our team love applying scientific knowledge
              into creative engineering projects. On the other hand, some of our
              writers are interested on how science affects society and
              politics. And some other crazy maniacs just loves pure mathematics
              with seemingly no impact on society.
              <br />
              <br />
              This website will remain free and public forever because our
              members believe in the right to accessible information. We hope to
              give some alternative perspective and explanations of various
              educational topics, in particular that of sciences.
            </p>
          </section>
          <section>
            <h1 className="text-3xl font-black">What We Do</h1>
            <p>
              As elaborated earlier, the institute is comprised of writers with
              a plethora of talents and interests. Initially, our website will
              primarily be themed around topics related to physical science,
              mathematics, and technology, but we plan on creating articles
              featuring topics from the biological and psychological sciences.
              <br />
              <br />
              Speaking of which, here are some ideas we are currently
              considering:
            </p>
            <ul className="list-disc ml-5">
              <li>
                Numerous technology articles- As you can see on the blog page,
                we're currently writing some articles on various subjects.
              </li>
              <li>
                Challenging homework/test/olympiad questions from maths and
                physics
              </li>
              <li>Databases for certain topics</li>
              <li>Coding tutorials/projects</li>
              <li>And more!</li>
            </ul>
          </section>
          <h1 className="text-3xl font-black">
            Please do contact us if you want to contribute in any way! We would
            love to have you!
          </h1>
        </>
      }
    />
  );
}

export default About;
