import { useEffect, useState } from "react";
import { fetchArchitecture, runTune } from "../GraphRagEditor/api";
import MermaidPreview from "../GraphRagEditor/MermaidPreview";

const REACT_COLORS = {
  blue: "#61DAFB",
  dark: "#20232A",
  gray: "#282C34",
  text: "#F7F7F7",
  accent: "#FB61DA",
  success: "#61FB8A",
  warning: "#FB8A61",
};

export default function ArchitectureDashboard() {
  const [architecture, setArchitecture] = useState(null);
  const [tuneResult, setTuneResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [config, setConfig] = useState({
    learning_rate: 0.01,
    grad_clip: 1.0,
    epochs: 5,
    hidden_dims: [16, 8],
    seed: 42,
  });

  useEffect(() => {
    fetchArchitecture()
      .then(setArchitecture)
      .catch((err) => setError(err.message));
  }, []);

  const handleTune = async (baselineOnly) => {
    setLoading(true);
    setError(null);
    try {
      const result = await runTune(config, baselineOnly);
      setTuneResult(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      className="p-6 max-w-6xl mx-auto space-y-6"
      style={{ backgroundColor: REACT_COLORS.dark, color: REACT_COLORS.text, minHeight: "100vh" }}
    >
      <header className="border-b pb-4" style={{ borderColor: REACT_COLORS.blue }}>
        <h1 className="text-3xl font-bold" style={{ color: REACT_COLORS.blue }}>
          Architecture Dashboard
        </h1>
        <p className="text-sm opacity-80">
          Asymmetric retrieval + hook chain + manual fine-tuning
        </p>
      </header>

      {error && (
        <div className="p-3 rounded" style={{ backgroundColor: REACT_COLORS.warning, color: REACT_COLORS.dark }}>
          {error}
        </div>
      )}

      <section className="space-y-3">
        <h2 className="text-xl font-semibold" style={{ color: REACT_COLORS.blue }}>
          Architecture Principles
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {architecture?.principles.map((principle, idx) => (
            <div
              key={idx}
              className="p-4 rounded border"
              style={{ backgroundColor: REACT_COLORS.gray, borderColor: REACT_COLORS.blue }}
            >
              <span
                className="inline-block w-6 h-6 rounded-full text-center text-sm font-bold mr-2"
                style={{ backgroundColor: REACT_COLORS.blue, color: REACT_COLORS.dark }}
              >
                {idx + 1}
              </span>
              {principle}
            </div>
          ))}
        </div>
      </section>

      <section className="space-y-3">
        <h2 className="text-xl font-semibold" style={{ color: REACT_COLORS.blue }}>
          Hook Chain Flow
        </h2>
        {architecture?.mermaid && (
          <div className="rounded overflow-hidden border" style={{ borderColor: REACT_COLORS.blue }}>
            <MermaidPreview mermaidText={architecture.mermaid} />
          </div>
        )}
      </section>

      <section className="space-y-3">
        <h2 className="text-xl font-semibold" style={{ color: REACT_COLORS.blue }}>
          Manual Fine-Tuning
        </h2>
        <div
          className="p-4 rounded border grid grid-cols-2 md:grid-cols-4 gap-3"
          style={{ backgroundColor: REACT_COLORS.gray, borderColor: REACT_COLORS.blue }}
        >
          {Object.entries(config).map(([key, value]) => (
            <div key={key}>
              <label className="block text-xs uppercase opacity-70">{key}</label>
              <input
                value={Array.isArray(value) ? value.join(",") : value}
                onChange={(e) => {
                  const newValue = e.target.value;
                  setConfig((prev) => ({
                    ...prev,
                    [key]: key === "hidden_dims" ? newValue.split(",").map(Number) : Number(newValue),
                  }));
                }}
                className="w-full p-2 rounded border bg-transparent"
                style={{ borderColor: REACT_COLORS.blue, color: REACT_COLORS.text }}
              />
            </div>
          ))}
        </div>
        <div className="flex gap-3">
          <button
            onClick={() => handleTune(true)}
            disabled={loading}
            className="px-4 py-2 rounded font-semibold"
            style={{ backgroundColor: REACT_COLORS.gray, border: `1px solid ${REACT_COLORS.blue}` }}
          >
            {loading ? "Running..." : "Baseline"}
          </button>
          <button
            onClick={() => handleTune(false)}
            disabled={loading}
            className="px-4 py-2 rounded font-semibold"
            style={{ backgroundColor: REACT_COLORS.blue, color: REACT_COLORS.dark }}
          >
            {loading ? "Training..." : "Train"}
          </button>
        </div>
        {tuneResult && (
          <div
            className="p-4 rounded border text-sm overflow-auto max-h-96"
            style={{ backgroundColor: REACT_COLORS.gray, borderColor: REACT_COLORS.blue }}
          >
            <pre className="whitespace-pre-wrap">{JSON.stringify(tuneResult, null, 2)}</pre>
          </div>
        )}
      </section>
    </div>
  );
}
