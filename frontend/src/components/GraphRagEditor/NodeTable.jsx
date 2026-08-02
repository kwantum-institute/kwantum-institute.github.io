import { useState } from "react";

const NODE_TYPES = [
  "concept",
  "person",
  "organization",
  "technology",
  "event",
  "paper",
  "question",
];

export default function NodeTable({ nodes, onChange, onDelete }) {
  const [editingId, setEditingId] = useState(null);
  const [form, setForm] = useState({ id: "", label: "", node_type: "concept", description: "", confidence: 0.5 });

  const startEdit = (node) => {
    setEditingId(node.id);
    setForm({ ...node, confidence: node.confidence ?? 0.5 });
  };

  const save = () => {
    if (!form.id || !form.label) return;
    onChange(form);
    setEditingId(null);
  };

  const addNew = () => {
    setEditingId("new");
    setForm({ id: "", label: "", node_type: "concept", description: "", confidence: 0.5 });
  };

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="font-semibold">Nodes</h3>
        <button onClick={addNew} className="px-3 py-1 bg-blue-600 text-white rounded">Add node</button>
      </div>

      <div className="overflow-auto border rounded">
        <table className="min-w-full text-sm">
          <thead className="bg-gray-100">
            <tr>
              <th className="px-3 py-2 text-left">Label</th>
              <th className="px-3 py-2 text-left">Type</th>
              <th className="px-3 py-2 text-left">Confidence</th>
              <th className="px-3 py-2 text-left">Actions</th>
            </tr>
          </thead>
          <tbody>
            {nodes.map((node) => (
              <tr key={node.id} className="border-t">
                {editingId === node.id ? (
                  <>
                    <td className="px-3 py-2">
                      <input
                        value={form.label}
                        onChange={(e) => setForm({ ...form, label: e.target.value })}
                        className="w-full border rounded px-2 py-1"
                      />
                    </td>
                    <td className="px-3 py-2">
                      <select
                        value={form.node_type}
                        onChange={(e) => setForm({ ...form, node_type: e.target.value })}
                        className="border rounded px-2 py-1"
                      >
                        {NODE_TYPES.map((t) => (
                          <option key={t} value={t}>{t}</option>
                        ))}
                      </select>
                    </td>
                    <td className="px-3 py-2">
                      <input
                        type="number"
                        min="0"
                        max="1"
                        step="0.01"
                        value={form.confidence}
                        onChange={(e) => setForm({ ...form, confidence: parseFloat(e.target.value) })}
                        className="w-24 border rounded px-2 py-1"
                      />
                    </td>
                    <td className="px-3 py-2 space-x-2">
                      <button onClick={save} className="text-green-600">Save</button>
                      <button onClick={() => setEditingId(null)} className="text-gray-600">Cancel</button>
                    </td>
                  </>
                ) : (
                  <>
                    <td className="px-3 py-2">{node.label}</td>
                    <td className="px-3 py-2">{node.node_type}</td>
                    <td className="px-3 py-2">{node.confidence}</td>
                    <td className="px-3 py-2 space-x-2">
                      <button onClick={() => startEdit(node)} className="text-blue-600">Edit</button>
                      <button onClick={() => onDelete(node.id)} className="text-red-600">Delete</button>
                    </td>
                  </>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {editingId === "new" && (
        <div className="border rounded p-4 space-y-2 bg-gray-50">
          <h4 className="font-semibold">New node</h4>
          <input
            placeholder="ID (lowercase, no spaces)"
            value={form.id}
            onChange={(e) => setForm({ ...form, id: e.target.value })}
            className="w-full border rounded px-2 py-1"
          />
          <input
            placeholder="Label"
            value={form.label}
            onChange={(e) => setForm({ ...form, label: e.target.value })}
            className="w-full border rounded px-2 py-1"
          />
          <select
            value={form.node_type}
            onChange={(e) => setForm({ ...form, node_type: e.target.value })}
            className="border rounded px-2 py-1"
          >
            {NODE_TYPES.map((t) => (
              <option key={t} value={t}>{t}</option>
            ))}
          </select>
          <input
            type="number"
            min="0"
            max="1"
            step="0.01"
            value={form.confidence}
            onChange={(e) => setForm({ ...form, confidence: parseFloat(e.target.value) })}
            className="w-24 border rounded px-2 py-1"
          />
          <div className="space-x-2">
            <button onClick={save} className="px-3 py-1 bg-green-600 text-white rounded">Create</button>
            <button onClick={() => setEditingId(null)} className="px-3 py-1 bg-gray-300 rounded">Cancel</button>
          </div>
        </div>
      )}
    </div>
  );
}
