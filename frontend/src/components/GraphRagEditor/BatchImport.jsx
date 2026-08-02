import { useState } from "react";

export default function BatchImport({ onImport }) {
  const [csvText, setCsvText] = useState("");
  const [dryRun, setDryRun] = useState(true);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);
    try {
      const payload = { csv: csvText, dry_run: dryRun, replace_existing: false };
      const res = await onImport(payload);
      setResult(res);
    } catch (err) {
      setResult({ error: err.message });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      <h3 className="font-semibold">Batch import</h3>
      <p className="text-sm text-gray-600">
        Upload CSV with a <code>kind</code> column set to <code>node</code> or <code>edge</code>.
        Dry run previews changes without saving.
      </p>

      <form onSubmit={handleSubmit} className="space-y-2">
        <textarea
          value={csvText}
          onChange={(e) => setCsvText(e.target.value)}
          rows={10}
          placeholder="kind,id,label,node_type,source_id,target_id,edge_type,confidence"
          className="w-full border rounded p-2 font-mono text-sm"
        />
        <div className="flex items-center gap-2">
          <input
            id="dryRun"
            type="checkbox"
            checked={dryRun}
            onChange={(e) => setDryRun(e.target.checked)}
          />
          <label htmlFor="dryRun" className="text-sm">Dry run only</label>
        </div>
        <button
          type="submit"
          disabled={loading}
          className="px-4 py-2 bg-blue-600 text-white rounded disabled:opacity-50"
        >
          {loading ? "Processing..." : "Run import"}
        </button>
      </form>

      {result && (
        <div className="border rounded p-3 bg-gray-50 text-sm">
          <pre className="whitespace-pre-wrap">{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
