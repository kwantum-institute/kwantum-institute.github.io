import { useEffect, useState } from "react";
import {
  batchImport,
  createEdge,
  createNode,
  deleteEdge,
  deleteNode,
  exportMermaid,
  fetchEdges,
  fetchNodes,
  runResearch,
  updateNode,
} from "./api";
import BatchImport from "./BatchImport";
import EdgeTable from "./EdgeTable";
import MermaidPreview from "./MermaidPreview";
import NodeTable from "./NodeTable";

const TABS = ["Graph", "Diagram", "Batch import", "Research"];

export default function GraphRagEditor() {
  const [activeTab, setActiveTab] = useState("Graph");
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);
  const [mermaidText, setMermaidText] = useState("");
  const [markdownText, setMarkdownText] = useState("");
  const [query, setQuery] = useState("");
  const [researchResult, setResearchResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const loadGraph = async () => {
    try {
      const [nodeData, edgeData] = await Promise.all([fetchNodes(), fetchEdges()]);
      setNodes(nodeData.nodes || []);
      setEdges(edgeData.edges || []);
      setError(null);
    } catch (err) {
      setError(err.message);
    }
  };

  const loadMermaid = async () => {
    try {
      const data = await exportMermaid();
      setMermaidText(data.mermaid || "");
      setMarkdownText(data.markdown || "");
    } catch (err) {
      setError(err.message);
    }
  };

  useEffect(() => {
    loadGraph();
  }, []);

  useEffect(() => {
    if (activeTab === "Diagram") {
      loadMermaid();
    }
  }, [activeTab]);

  const handleNodeChange = async (node) => {
    try {
      if (nodes.some((n) => n.id === node.id)) {
        await updateNode(node.id, node);
      } else {
        await createNode(node);
      }
      await loadGraph();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleNodeDelete = async (id) => {
    try {
      await deleteNode(id);
      await loadGraph();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleEdgeChange = async (edge) => {
    try {
      await createEdge(edge);
      await loadGraph();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleEdgeDelete = async (id) => {
    try {
      await deleteEdge(id);
      await loadGraph();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleBatchImport = async (payload) => {
    const result = await batchImport(payload);
    if (!result.dry_run) {
      await loadGraph();
    }
    return result;
  };

  const handleResearch = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResearchResult(null);
    try {
      const result = await runResearch(query);
      setResearchResult(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-4 max-w-6xl mx-auto space-y-4">
      <h2 className="text-2xl font-bold">GraphRAG Editor</h2>
      {error && <div className="p-3 bg-red-100 text-red-800 rounded">{error}</div>}

      <div className="flex gap-2 border-b pb-2">
        {TABS.map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 rounded-t ${
              activeTab === tab ? "bg-blue-600 text-white" : "bg-gray-100"
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      {activeTab === "Graph" && (
        <div className="space-y-6">
          <NodeTable nodes={nodes} onChange={handleNodeChange} onDelete={handleNodeDelete} />
          <EdgeTable edges={edges} nodes={nodes} onChange={handleEdgeChange} onDelete={handleEdgeDelete} />
        </div>
      )}

      {activeTab === "Diagram" && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <div>
            <h3 className="font-semibold mb-2">Mermaid diagram</h3>
            <MermaidPreview mermaidText={mermaidText} />
          </div>
          <div>
            <h3 className="font-semibold mb-2">Markdown view</h3>
            <pre className="border rounded p-4 bg-gray-50 text-sm overflow-auto h-96">{markdownText}</pre>
          </div>
        </div>
      )}

      {activeTab === "Batch import" && <BatchImport onImport={handleBatchImport} />}

      {activeTab === "Research" && (
        <div className="space-y-4">
          <form onSubmit={handleResearch} className="flex gap-2">
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ask a research question..."
              className="flex-1 border rounded px-3 py-2"
            />
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 bg-blue-600 text-white rounded disabled:opacity-50"
            >
              {loading ? "Researching..." : "Research"}
            </button>
          </form>
          {researchResult && (
            <div className="border rounded p-3 bg-gray-50 text-sm">
              <pre className="whitespace-pre-wrap">{JSON.stringify(researchResult, null, 2)}</pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
