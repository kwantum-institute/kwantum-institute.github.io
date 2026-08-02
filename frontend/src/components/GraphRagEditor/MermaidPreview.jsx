import { useEffect, useRef } from "react";
import mermaid from "mermaid";

mermaid.initialize({ startOnLoad: false, securityLevel: "strict" });

export default function MermaidPreview({ mermaidText }) {
  const containerRef = useRef(null);

  useEffect(() => {
    if (!containerRef.current || !mermaidText) return;

    const container = containerRef.current;
    const id = `mermaid-${Math.random().toString(36).slice(2, 9)}`;
    container.replaceChildren();
    const el = document.createElement("div");
    el.className = id;
    el.textContent = mermaidText;
    container.appendChild(el);

    mermaid.run({ querySelector: `.${id}` }).catch((err) => {
      const errorElement = document.createElement("pre");
      errorElement.className = "text-red-500";
      errorElement.textContent =
        err instanceof Error ? err.message : "Unable to render diagram";
      container.replaceChildren(errorElement);
    });
  }, [mermaidText]);

  return (
    <div className="border rounded p-4 bg-white overflow-auto">
      <div ref={containerRef} className="mermaid-preview" />
    </div>
  );
}
