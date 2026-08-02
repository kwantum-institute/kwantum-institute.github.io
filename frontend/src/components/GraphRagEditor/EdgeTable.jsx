import { useState } from "react";

const EDGE_TYPES = [
  "relates_to",
  "depends_on",
  "enables",
  "contradicts",
  "cited_by",
  "part_of",
  "solves",
];

export default function EdgeTable({ edges, nodes, onChange, onDelete }) {
  const [form, setForm] = useState({ id: "", source_id: "", target_id: "", edge_type: "relates_to", label: "", confidence: 0.5 });

  const handleAdd = () => {
    if (!form.id || !form.source_id || !form.target_id) return;
    onChange(form);
    setForm({ id: "", source_id: "", target_id: "", edge_type: "relates_to", label: "", confidence: 0.5 });
  };

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="font-semibold">Relationships</h3>
      </div>

      <div className="grid grid-cols-6 gap-2 items-end border rounded p-4 bg-gray-50">
        <input
          placeholder="ID"
          value={form.id}
          onChange={(e) => setForm({ ...form, id: e.target.value })}
          className="border rounded px-2 py-1"
        />
        <select
          value={form.source_id}
          onChange={(e) => setForm({ ...form, source_id: e.target.value })}
          className="border rounded px-2 py-1"
        >
          <option value="">Source</option>
          {nodes.map((n) => <option key={n.id} value={n.id}>{n.label}</option>)}
        </select>
        <select
          value={form.target_id}
          onChange={(e) => setForm({ ...form, target_id: e.target.value })}
          className="border rounded px-2 py-1"
        >
          <option value="">Target</option>
          {nodes.map((n) => <option key={n.id} value={n.id}>{n.label}</option>)}
        </select>
        <select
          value={form.edge_type}
          onChange={(e) => setForm({ ...form, edge_type: e.target.value })}
          className="border rounded px-2 py-1"
        >
          {EDGE_TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
        </select>
        <input
          type="number"
          min="0"
          max="1"
          step="0.01"
          value={form.confidence}
          onChange={(e) => setForm({ ...form, confidence: parseFloat(e.target.value) })}
          className="border rounded px-2 py-1"
        />
        <button onClick={handleAdd} className="px-3 py-1 bg-blue-600 text-white rounded">Add edge</button>
      </div>

      <div className="overflow-auto border rounded">
        <table className="min-w-full text-sm">
          <thead className="bg-gray-100">
            <tr>
              <th className="px-3 py-2 text-left">Source</th>
              <th className="px-3 py-2 text-left">Type</th>
              <th className="px-3 py-2 text-left">Target</th>
              <th className="px-3 py-2 text-left">Confidence</th>
              <th className="px-3 py-2 text-left">Actions</th>
            </tr>
          </thead>
          <tbody>
            {edges.map((edge) => (
              <tr key={edge.id} className="border-t">
                <td className="px-3 py-2">{edge.source_id}</td>
                <td className="px-3 py-2">{edge.edge_type}</td>
                <td className="px-3 py-2">{edge.target_id}</td>
                <td className="px-3 py-2">{edge.confidence}</td>
                <td className="px-3 py-2">
                  <button onClick={() => onDelete(edge.id)} className="text-red-600">Delete</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
