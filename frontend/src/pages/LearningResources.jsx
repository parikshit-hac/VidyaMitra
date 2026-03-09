import { useState } from "react";

import api from "../services/api";

function LearningResources() {
  const [topic, setTopic] = useState("data analysis");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [youtubeResults, setYoutubeResults] = useState([]);
  const [pexelsResults, setPexelsResults] = useState([]);

  const handleSearch = async (event) => {
    event.preventDefault();
    const query = topic.trim();
    if (!query) {
      setError("Please enter a topic to search.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const [learningResp, visualsResp] = await Promise.all([
        api.get("/resources/learning", { params: { topic: query } }),
        api.get("/resources/visuals", { params: { query } })
      ]);

      const youtube = learningResp?.data?.youtube || [];
      const pexels = visualsResp?.data?.images || [];

      setYoutubeResults(youtube);
      setPexelsResults(pexels);
    } catch (err) {
      setError(err?.response?.data?.detail || "Failed to fetch resources.");
      setYoutubeResults([]);
      setPexelsResults([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="space-y-5">
      <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
        <h2 className="text-xl font-semibold text-slate-900">Learning Resources</h2>
        <p className="mt-1 text-sm text-slate-600">
          Search by topic to get curated YouTube resources and visual learning references.
        </p>

        <form onSubmit={handleSearch} className="mt-4 flex flex-col gap-3 sm:flex-row">
          <input
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder="e.g. Cyber security fundamentals"
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none"
          />
          <button
            type="submit"
            disabled={loading}
            className="rounded-md bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-60"
          >
            {loading ? "Searching..." : "Search"}
          </button>
        </form>

        {error && <p className="mt-3 text-sm text-rose-700">{error}</p>}
      </div>

      {loading && (
        <div className="rounded-xl border border-slate-200 bg-white p-8 shadow-sm">
          <div className="flex items-center justify-center gap-3 text-slate-600">
            <span className="h-5 w-5 animate-spin rounded-full border-2 border-slate-400 border-t-transparent" />
            <span className="text-sm">Loading resources...</span>
          </div>
        </div>
      )}

      {!loading && (
        <>
          <article className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="mb-4 flex items-center justify-between">
              <h3 className="text-lg font-semibold text-slate-900">YouTube Learning Results</h3>
              <span className="text-xs text-slate-500">{youtubeResults.length} items</span>
            </div>

            {youtubeResults.length === 0 ? (
              <p className="text-sm text-slate-500">No YouTube results yet. Search a topic.</p>
            ) : (
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
                {youtubeResults.map((item, idx) => (
                  <a
                    key={`${item.url || item.title}-${idx}`}
                    href={item.url}
                    target="_blank"
                    rel="noreferrer"
                    className="block rounded-lg border border-slate-200 bg-slate-50 p-4 transition hover:border-brand-200 hover:bg-brand-50"
                  >
                    <p className="line-clamp-2 text-sm font-semibold text-slate-900">{item.title || "Untitled video"}</p>
                    <p className="mt-2 text-xs text-slate-500">{item.channel || "YouTube"}</p>
                    <p className="mt-2 line-clamp-3 text-xs text-slate-600">{item.description || "No description available."}</p>
                  </a>
                ))}
              </div>
            )}
          </article>

          <article className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="mb-4 flex items-center justify-between">
              <h3 className="text-lg font-semibold text-slate-900">Pexels Visual Resources</h3>
              <span className="text-xs text-slate-500">{pexelsResults.length} images</span>
            </div>

            {pexelsResults.length === 0 ? (
              <p className="text-sm text-slate-500">No visual results yet. Search a topic.</p>
            ) : (
              <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5">
                {pexelsResults.map((img, idx) => (
                  <a
                    key={`${img.id || img.page_url || idx}`}
                    href={img.page_url || img.image_url}
                    target="_blank"
                    rel="noreferrer"
                    className="group block overflow-hidden rounded-lg border border-slate-200"
                  >
                    <img
                      src={img.thumb_url || img.image_url}
                      alt={img.photographer || "Pexels image"}
                      className="h-32 w-full object-cover transition duration-300 group-hover:scale-105 sm:h-36"
                      loading="lazy"
                    />
                    <div className="p-2">
                      <p className="truncate text-xs text-slate-600">{img.photographer || "Pexels"}</p>
                    </div>
                  </a>
                ))}
              </div>
            )}
          </article>
        </>
      )}
    </section>
  );
}

export default LearningResources;
