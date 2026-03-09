import { useState } from "react";

import api from "../services/api";

function MarketInsights() {
  const [topic, setTopic] = useState("job market");
  const [baseCurrency, setBaseCurrency] = useState("USD");
  const [symbols, setSymbols] = useState("INR,EUR");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [news, setNews] = useState([]);
  const [exchange, setExchange] = useState(null);

  const fetchInsights = async (event) => {
    event.preventDefault();

    if (!topic.trim()) {
      setError("Please enter a topic.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const { data } = await api.get("/resources/market", {
        params: {
          topic: topic.trim(),
          base_currency: baseCurrency.trim().toUpperCase(),
          symbols: symbols.trim().toUpperCase()
        }
      });

      setNews(data?.news || []);
      setExchange(data?.exchange || null);
    } catch (err) {
      setError(err?.response?.data?.detail || "Failed to fetch market insights.");
      setNews([]);
      setExchange(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="space-y-5">
      <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
        <h2 className="text-xl font-semibold text-slate-900">Market Insights</h2>
        <p className="mt-1 text-sm text-slate-600">
          Get latest role-related market news and quick currency updates.
        </p>

        <form onSubmit={fetchInsights} className="mt-4 grid grid-cols-1 gap-3 md:grid-cols-3">
          <input
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder="Topic (e.g. cybersecurity jobs)"
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm md:col-span-3"
          />
          <input
            value={baseCurrency}
            onChange={(e) => setBaseCurrency(e.target.value)}
            placeholder="Base currency"
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
          />
          <input
            value={symbols}
            onChange={(e) => setSymbols(e.target.value)}
            placeholder="Symbols (INR,EUR,GBP)"
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm md:col-span-2"
          />
          <div className="md:col-span-3">
            <button
              type="submit"
              disabled={loading}
              className="rounded-md bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-60"
            >
              {loading ? "Loading..." : "Fetch Insights"}
            </button>
          </div>
        </form>

        {error && <p className="mt-3 text-sm text-rose-700">{error}</p>}
      </div>

      {loading && (
        <div className="rounded-xl border border-slate-200 bg-white p-8 shadow-sm">
          <div className="flex items-center justify-center gap-3 text-slate-600">
            <span className="h-5 w-5 animate-spin rounded-full border-2 border-slate-400 border-t-transparent" />
            <span className="text-sm">Loading market data...</span>
          </div>
        </div>
      )}

      {!loading && (
        <>
          <article className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
            <h3 className="text-lg font-semibold text-slate-900">Exchange Rates</h3>
            {!exchange?.rates || Object.keys(exchange.rates).length === 0 ? (
              <p className="mt-2 text-sm text-slate-500">No exchange rate data yet.</p>
            ) : (
              <div className="mt-3 grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5">
                {Object.entries(exchange.rates).map(([code, value]) => (
                  <div key={code} className="rounded-lg border border-slate-200 bg-slate-50 p-3">
                    <p className="text-xs text-slate-500">
                      {exchange.base_currency}/{code}
                    </p>
                    <p className="mt-1 text-lg font-semibold text-slate-900">{String(value)}</p>
                  </div>
                ))}
              </div>
            )}
          </article>

          <article className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="mb-4 flex items-center justify-between">
              <h3 className="text-lg font-semibold text-slate-900">Latest News</h3>
              <span className="text-xs text-slate-500">{news.length} items</span>
            </div>

            {news.length === 0 ? (
              <p className="text-sm text-slate-500">No news results yet. Search with a topic.</p>
            ) : (
              <div className="grid grid-cols-1 gap-3 md:grid-cols-2 xl:grid-cols-3">
                {news.map((item, idx) => (
                  <a
                    key={`${item.url || item.title}-${idx}`}
                    href={item.url}
                    target="_blank"
                    rel="noreferrer"
                    className="block rounded-lg border border-slate-200 bg-slate-50 p-4 transition hover:border-brand-200 hover:bg-brand-50"
                  >
                    <p className="line-clamp-2 text-sm font-semibold text-slate-900">{item.title || "Untitled"}</p>
                    <p className="mt-1 text-xs text-slate-500">{item.source || "Source"}</p>
                    <p className="mt-2 text-xs text-slate-600">{item.published_at ? new Date(item.published_at).toLocaleString() : ""}</p>
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

export default MarketInsights;
