import { useEffect, useRef } from "react";
import mermaid from "mermaid";

mermaid.initialize({ startOnLoad: false, securityLevel: "strict" });

export default function MermaidPreview({ mermaidText }) {
  const containerRef = useRef(null);

  useEffect(() => {
    if (!containerRef.current || !mermaidText) return;

    const id = `mermaid-${Math.random().toString(36).slice(2, 9)}`;
    containerRef.current.innerHTML = "";
    const el = document.createElement("div");
    el.className = id;
    el.textContent = mermaidText;
    containerRef.current.appendChild(el);

    mermaid.run({ querySelector: `.${id}` }).catch((err) => {
      containerRef.current.innerHTML = `<pre class="text-red-500">${err.message}</pre>`;
    });
  }, [mermaidText]);

  return (
    <div className="border rounded p-4 bg-white overflow-auto">
      <div ref={containerRef} className="mermaid-preview" />
    </div>
  );
}
