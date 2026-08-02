import { useState } from "react";
import "./ScienceSearch.css";

const API_BASE_URL = "http://127.0.0.1:8000/api";

const badgeClass = (badge) => {
  const map = {
    "Peer Reviewed": "badge peer",
    "Open Access PDF": "badge oa",
    "Highly Cited": "badge cited",
    Retracted: "badge retracted",
    Preprint: "badge preprint",
  };
  return map[badge] || "badge";
};

function ResultCard({ item }) {
  const [openTldr, setOpenTldr] = useState(false);
  const [openAbstract, setOpenAbstract] = useState(false);

  return (
    <article className="science-result">
      <div className="science-result-badges">
        {(item.badges || []).map((badge) => (
          <span key={badge} className={badgeClass(badge)}>
            {badge}
          </span>
        ))}
      </div>

      <h3 className="science-result-title">
        {item.url ? (
          <a href={item.url} target="_blank" rel="noopener noreferrer">
            {item.title}
          </a>
        ) : (
          item.title
        )}
      </h3>

      <p className="science-result-meta">
        <span>{item.journal || item.source}</span>
        {item.year ? <span> · {item.year}</span> : null}
        {typeof item.citation_count === "number" ? (
          <span> · {item.citation_count} citations</span>
        ) : null}
        {item.doi ? <span> · DOI {item.doi}</span> : null}
      </p>

      {item.authors?.length ? (
        <p className="science-result-authors">{item.authors.slice(0, 6).join(", ")}</p>
      ) : null}

      <div className="science-result-actions">
        <button type="button" onClick={() => setOpenTldr((v) => !v)}>
          {openTldr ? "Hide TL;DR" : "TL;DR"}
        </button>
        {item.abstract ? (
          <button type="button" onClick={() => setOpenAbstract((v) => !v)}>
            {openAbstract ? "Hide abstract" : "Abstract"}
          </button>
        ) : null}
        {item.oa_url ? (
          <a className="science-pdf-link" href={item.oa_url} target="_blank" rel="noopener noreferrer">
            PDF
          </a>
        ) : null}
      </div>

      {openTldr && item.tldr ? <p className="science-tldr">{item.tldr}</p> : null}
      {openAbstract && item.abstract ? (
        <p className="science-abstract">{item.abstract}</p>
      ) : null}
    </article>
  );
}

const ScienceSearch = () => {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [payload, setPayload] = useState(null);

  const onSubmit = async (event) => {
    event.preventDefault();
    const trimmed = query.trim();
    if (!trimmed) {
      setError("Enter a science question, DOI, PMID, or arXiv ID.");
      return;
    }

    setLoading(true);
    setError("");
    setPayload(null);

    try {
      const response = await fetch(`${API_BASE_URL}/search/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: trimmed }),
      });
      const data = await response.json();
      if (!response.ok || !data.success) {
        throw new Error(data.error || data.detail || "Search failed");
      }
      setPayload(data);
    } catch (err) {
      setError(err.message || "Could not reach the search service.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="science-search" aria-label="Credible science source search">
      <div className="science-search-inner">
        <p className="science-search-kicker">Source finder</p>
        <h2 className="science-search-heading">Search credible literature</h2>
        <p className="science-search-sub">
          Ask a science question. We return peer-reviewed and preprint sources
          only — no AI-written answers.
        </p>

        <form className="science-search-form" onSubmit={onSubmit}>
          <input
            type="search"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="e.g. caffeine adenosine receptor antagonism, or 10.1038/..."
            aria-label="Science search query"
            disabled={loading}
          />
          <button type="submit" disabled={loading}>
            {loading ? "Searching…" : "Search sources"}
          </button>
        </form>

        {error ? <p className="science-search-error">{error}</p> : null}

        {payload ? (
          <div className="science-search-results">
            <div className="science-search-status">
              <span>
                {payload.result_count} source{payload.result_count === 1 ? "" : "s"}
              </span>
              {payload.cache_hit ? <span className="cache-pill">cached</span> : null}
              {payload.structured_query?.rewriter ? (
                <span className="rewriter-pill">via {payload.structured_query.rewriter}</span>
              ) : null}
            </div>
            {payload.note ? <p className="science-search-note">{payload.note}</p> : null}
            {(payload.results || []).map((item) => (
              <ResultCard key={`${item.doi || item.url || item.title}`} item={item} />
            ))}
            {!payload.results?.length ? (
              <p className="science-search-empty">No matching sources found. Try different keywords.</p>
            ) : null}
          </div>
        ) : null}
      </div>
    </section>
  );
};

export default ScienceSearch;
