import React, { useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";
import TradingChart from "./TradingChart.jsx";

function Metric({ label, value, help }) {
  return (
    <div className="metric">
      <div className="label">{label}<span title={help}>ⓘ</span></div>
      <strong>{value}</strong>
    </div>
  );
}

function RiskBars({ risk }) {
  if (!risk) return null;
  const items = Object.entries(risk.risk_contribution || {});
  return (
    <div className="risk-bars">
      {items.map(([symbol, value]) => (
        <div className="risk-row" key={symbol}>
          <div><strong>{symbol}</strong><span>{(value * 100).toFixed(1)}%</span></div>
          <div className="bar"><i style={{ width: Math.min(100, value * 100) + "%" }} /></div>
        </div>
      ))}
    </div>
  );
}

function ToolbarButton({ children, active, onClick, title }) {
  return (
    <button className={active ? "tv-btn active" : "tv-btn"} onClick={onClick} title={title}>
      {children}
    </button>
  );
}

function App() {
  const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000").replace(/\/$/, "");
  const [symbol, setSymbol] = useState("AAPL");
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [rightTab, setRightTab] = useState("Watchlist");
  const [bottomTab, setBottomTab] = useState("Overview");
  const [watchlist, setWatchlist] = useState(["AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "RELIANCE", "TCS", "INFY"]);

  async function analyzeSymbol(nextSymbol) {
    const selected = (nextSymbol || symbol).trim().toUpperCase();
    if (!selected) return;
    setSymbol(selected);
    setLoading(true);
    setError("");
    setData(null);
    try {
      const encoded = encodeURIComponent(selected);
      let historyPayload;
      const historyResponse = await fetch(
        API_BASE_URL + "/api/market/" + encoded + "/history?outputsize=500"
      );

      if (historyResponse.ok) {
        historyPayload = await historyResponse.json();
      } else {
        const fallbackResponse = await fetch(
          API_BASE_URL + "/api/market/" + encoded + "/research?horizon=5&outputsize=500"
        );
        const fallbackPayload = await fallbackResponse.json();
        if (!fallbackResponse.ok) {
          throw new Error(
            fallbackPayload.detail || "Market data search failed. Restart the backend and verify the data provider."
          );
        }
        setData(fallbackPayload);
        setWatchlist((items) => Array.from(new Set([selected, ...items])));
        return;
      }

      const fastData = {
        symbol: selected,
        provider: historyPayload.provider,
        history: historyPayload.history || [],
      };
      setData(fastData);
      setWatchlist((items) => Array.from(new Set([selected, ...items])));

      try {
        const researchResponse = await fetch(
          API_BASE_URL + "/api/market/" + encoded + "/research?horizon=5&outputsize=500"
        );
        const researchPayload = await researchResponse.json();
        if (researchResponse.ok) {
          setData(researchPayload);
        } else {
          setError(researchPayload.detail || "Research calculation failed. Price chart is available.");
        }
      } catch (researchError) {
        setError(researchError.message || "Research calculation failed. Price chart is available.");
      }
    } catch (err) {
      setError(err.message || "Market data search failed");
    } finally {
      setLoading(false);
    }
  }

  const forecast = data?.forecast;
  const backtest = data?.backtest;
  const risk = data?.risk;
  const confidence = data?.confidence;
  const decision = data?.decision;
  const history = data?.history || [];
  const lastPrice = Number(forecast?.last_price || history.at(-1)?.close || 0);
  const move = forecast && lastPrice ? ((Number(forecast.point) / lastPrice) - 1) * 100 : 0;
  const outlook = decision?.signal || (move > 2 ? "Positive" : move < -2 ? "Negative" : "Neutral");

  return (
    <main className="terminal-shell">
      <header className="tv-header">
        <div className="tv-brand">
          <div className="tv-logo">S</div>
          <div>
            <strong>Stock Intelligence</strong>
            <span>Supercharts</span>
          </div>
        </div>
        <nav className="tv-nav">
          <button>Products</button>
          <button>Markets</button>
          <button>News</button>
          <button>Community</button>
        </nav>
        <div className="tv-header-actions">
          <span className="live-pill"><i /> Data</span>
          <button className="icon-button">⌁</button>
          <button className="icon-button">⚙</button>
        </div>
      </header>

      <section className="tv-top-toolbar">
        <div className="symbol-search">
          <span>⌕</span>
          <input
            value={symbol}
            onChange={(event) => setSymbol(event.target.value.toUpperCase())}
            onKeyDown={(event) => event.key === "Enter" && analyzeSymbol()}
            placeholder="Search symbol"
          />
          <button onClick={() => analyzeSymbol()} disabled={loading}>{loading ? "..." : "Search"}</button>
        </div>
        <div className="toolbar-separator" />
        <ToolbarButton active>1D</ToolbarButton>
        <ToolbarButton>1W</ToolbarButton>
        <ToolbarButton>1M</ToolbarButton>
        <ToolbarButton>3M</ToolbarButton>
        <ToolbarButton>6M</ToolbarButton>
        <ToolbarButton>1Y</ToolbarButton>
        <div className="toolbar-separator" />
        <ToolbarButton active title="Candlestick chart">◈ Candles</ToolbarButton>
        <ToolbarButton title="Indicators">ƒx Indicators</ToolbarButton>
        <ToolbarButton title="Alert">◉ Alert</ToolbarButton>
        <ToolbarButton title="Compare symbols">＋ Compare</ToolbarButton>
        <div className="toolbar-spacer" />
        <ToolbarButton>Save</ToolbarButton>
        <button className="publish-button">Publish</button>
      </section>

      {error && <div className="terminal-error">{error}</div>}

      <div className="tv-workspace">
        <aside className="drawing-toolbar">
          {["↖", "✚", "╱", "⌁", "□", "○", "T", "⇱", "⌕", "⌂", "☆", "⚙"].map((icon, index) => (
            <button key={index} title="Chart tool">{icon}</button>
          ))}
        </aside>

        <section className="chart-workspace">
          <div className="chart-symbol-head">
            <div>
              <div className="instrument-title">
                <strong>{data?.symbol || symbol}</strong>
                <span>{data?.symbol ? "· Exchange data" : "· Search a symbol"}</span>
              </div>
              <div className="instrument-subtitle">
                {lastPrice ? lastPrice.toFixed(2) : "—"}
                <span className={decision?.score >= 60 ? "change positive" : decision?.score <= 40 ? "change negative" : "change"}>
                  {move >= 0 ? "+" : ""}{move.toFixed(2)}% model horizon
                </span>
              </div>
              {decision ? (
                <div className={decision.signal.includes("BUY") ? "signal-badge buy" : decision.signal.includes("SELL") ? "signal-badge sell" : "signal-badge hold"}>
                  {decision.signal} <strong>{decision.score.toFixed(1)}/100</strong>
                </div>
              ) : null}
            </div>
            <div className="chart-head-actions">
              <button>☰</button><button>⌄</button><button>⛶</button>
            </div>
          </div>

          {!data ? (
            <div className="empty-chart">
              <div className="empty-cross">✦</div>
              <h2>Search a symbol</h2>
              <p>Enter AAPL, RELIANCE, TCS, INFY or another supported ticker above.</p>
              <div className="quick-symbols">
                {["AAPL", "MSFT", "NVDA", "RELIANCE", "TCS", "INFY"].map((item) => (
                  <button key={item} onClick={() => analyzeSymbol(item)}>{item}</button>
                ))}
              </div>
            </div>
          ) : (
            <TradingChart history={history} forecast={forecast} />
          )}

          {data && (
            <div className="chart-underlay-grid">
              <div className="mini-stat"><span>Open</span><strong>{Number(history.at(-1)?.open || 0).toFixed(2)}</strong></div>
              <div className="mini-stat"><span>High</span><strong>{Number(history.at(-1)?.high || 0).toFixed(2)}</strong></div>
              <div className="mini-stat"><span>Low</span><strong>{Number(history.at(-1)?.low || 0).toFixed(2)}</strong></div>
              <div className="mini-stat"><span>Close</span><strong>{lastPrice.toFixed(2)}</strong></div>
              <div className="mini-stat"><span>Forecast</span><strong>{Number(forecast?.point || 0).toFixed(2)}</strong></div>
              <div className="mini-stat"><span>Range</span><strong>{Number(forecast?.lower || 0).toFixed(2)}–{Number(forecast?.upper || 0).toFixed(2)}</strong></div>
            </div>
          )}
        </section>

        <aside className="watchlist-panel">
          <div className="watchlist-tabs">
            {["Watchlist", "Details"].map((tab) => (
              <button key={tab} className={rightTab === tab ? "active" : ""} onClick={() => setRightTab(tab)}>
                {tab}
              </button>
            ))}
            <button className="plus-tab">＋</button>
          </div>

          {rightTab === "Watchlist" ? (
            <div className="watchlist-content">
              <div className="watchlist-title"><strong>My watchlist</strong><span>⋮</span></div>
              <div className="watch-columns"><span>Symbol</span><span>Last</span><span>Chg</span></div>
              {watchlist.map((item) => {
                const active = item === (data?.symbol || symbol);
                return (
                  <button className={active ? "watch-row active" : "watch-row"} key={item} onClick={() => analyzeSymbol(item)}>
                    <span className="watch-symbol"><i />{item}</span>
                    <span>{active && lastPrice ? lastPrice.toFixed(2) : "—"}</span>
                    <span className={active && move < 0 ? "negative" : "positive"}>{active ? (move >= 0 ? "+" : "") + move.toFixed(2) + "%" : "—"}</span>
                  </button>
                );
              })}
            </div>
          ) : (
            <div className="details-content">
              <div className="details-label">{data?.symbol || "No symbol"}</div>
              <div className="details-price">{lastPrice ? lastPrice.toFixed(2) : "—"}</div>
              <div className={move >= 0 ? "detail-change positive" : "detail-change negative"}>
                {move >= 0 ? "+" : ""}{move.toFixed(2)}%
              </div>
              <div className="detail-grid">
                <span>Regime</span><strong>{(data?.regime?.regime || "—").replaceAll("_", " ")}</strong>
                <span>Confidence</span><strong>{confidence?.label || "—"}</strong>
                <span>Annual risk</span><strong>{risk ? (risk.annualized_volatility * 100).toFixed(1) + "%" : "—"}</strong>
                <span>Quality</span><strong>{data?.data_quality?.score != null ? (data.data_quality.score * 100).toFixed(0) + "%" : "—"}</strong>
              </div>
            </div>
          )}
        </aside>
      </div>

      <section className="bottom-panel">
        <div className="bottom-tabs">
          {["Overview", "Forecast", "Technicals", "Models", "Risk", "Portfolio"].map((tab) => (
            <button key={tab} className={bottomTab === tab ? "active" : ""} onClick={() => setBottomTab(tab)}>{tab}</button>
          ))}
          <div className="bottom-spacer" />
          <span className="data-note">Probabilistic research · not financial advice</span>
        </div>

        {bottomTab === "Overview" && (
          <div className="research-grid">
            <Metric label="Signal score" value={decision ? decision.score.toFixed(1) + "/100" : "—"} help="Composite quantitative research score; not a guaranteed outcome." />
            <Metric label="Conviction" value={decision ? (decision.conviction * 100).toFixed(0) + "%" : "—"} help="Signal strength after volatility attenuation." />
            <Metric label="Outlook" value={outlook} help="Composite research classification." />
            <Metric label="Estimated price" value={forecast ? Number(forecast.point).toFixed(2) : "—"} help="Model estimate, not a guarantee." />
            <Metric label="Confidence" value={confidence?.label || "—"} help="Combines data quality, model agreement and validation." />
            <Metric label="Directional accuracy" value={backtest ? (backtest.directional_accuracy * 100).toFixed(1) + "%" : "—"} help="Historical walk-forward direction accuracy." />
          </div>
        )}

        {bottomTab === "Forecast" && data && (
          <div className="research-wide">
            <div className="range-card"><span>Model estimate</span><strong>{Number(forecast.point).toFixed(2)}</strong></div>
            <div className="range-card"><span>Lower bound</span><strong>{Number(forecast.lower).toFixed(2)}</strong></div>
            <div className="range-card"><span>Upper bound</span><strong>{Number(forecast.upper).toFixed(2)}</strong></div>
            <div className="range-card"><span>Validation</span><strong>{backtest?.observations ?? "—"} samples</strong></div>
          </div>
        )}

        {bottomTab === "Technicals" && data && (
          <div className="research-wide">
            {(data.feature_importance?.features || []).slice(0, 6).map((item) => (
              <div className="feature-chip" key={item.feature}><span>{item.feature.replaceAll("_", " ")}</span><strong>{(item.relative_importance * 100).toFixed(1)}%</strong></div>
            ))}
          </div>
        )}

        {bottomTab === "Models" && data && (
          <div className="models-table">
            {(data.model_comparison || []).map((model, index) => (
              <div className="model-row" key={model.model}>
                <strong>{index === 0 ? "Selected · " : ""}{model.model.replaceAll("_", " ")}</strong>
                <span>MAE {model.mae.toFixed(2)}</span>
                <span>RMSE {model.rmse.toFixed(2)}</span>
                <span>Direction {(model.directional_accuracy * 100).toFixed(1)}%</span>
              </div>
            ))}
          </div>
        )}

        {bottomTab === "Risk" && data && (
          <div className="research-grid">
            <Metric label="Max drawdown" value={risk ? (risk.max_drawdown * 100).toFixed(1) + "%" : "—"} help="Largest historical peak-to-trough decline." />
            <Metric label="Sharpe" value={risk?.sharpe?.toFixed(2) || "—"} help="Historical risk-adjusted return ratio." />
            <Metric label="Annual return" value={risk ? (risk.annualized_return * 100).toFixed(1) + "%" : "—"} help="Historical annualized return." />
            <Metric label="Data quality" value={data.data_quality?.score != null ? (data.data_quality.score * 100).toFixed(0) + "%" : "—"} help="Quality score for fetched historical data." />
          </div>
        )}

        {bottomTab === "Portfolio" && (
          <PortfolioPanel API_BASE_URL={API_BASE_URL} />
        )}
      </section>

      <footer className="terminal-footer">
        Stock Intelligence is a research and decision-support tool. Forecasts can be wrong and do not guarantee returns.
      </footer>
    </main>
  );
}

function PortfolioPanel({ API_BASE_URL }) {
  const [input, setInput] = useState("AAPL:60, MSFT:40");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  async function run() {
    const positions = input.split(",").map((item) => item.trim()).filter(Boolean).map((item) => {
      const [symbol, weight] = item.split(":");
      return { symbol: symbol.trim(), weight: Number(weight) };
    });
    if (!positions.length || positions.some((item) => !item.symbol || !Number.isFinite(item.weight))) return;
    setLoading(true);
    try {
      const response = await fetch(API_BASE_URL + "/api/portfolio/analyze-symbols", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ positions, confidence: 0.95 }),
      });
      if (response.ok) setResult(await response.json());
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="portfolio-panel">
      <div className="portfolio-input"><input value={input} onChange={(event) => setInput(event.target.value)} /><button onClick={run}>{loading ? "..." : "Analyze portfolio"}</button></div>
      {result && (
        <>
          <div className="research-grid">
            <Metric label="Volatility" value={(result.analysis.annualized_volatility * 100).toFixed(1) + "%"} help="Historical portfolio volatility." />
            <Metric label="VaR" value={(result.analysis.var * 100).toFixed(2) + "%"} help="Historical one-day loss threshold." />
            <Metric label="CVaR" value={(result.analysis.cvar * 100).toFixed(2) + "%"} help="Average loss beyond VaR." />
            <Metric label="Max drawdown" value={(result.analysis.max_drawdown * 100).toFixed(1) + "%"} help="Largest historical peak-to-trough decline." />
          </div>
          <RiskBars risk={result.analysis} />
        </>
      )}
    </div>
  );
}

createRoot(document.getElementById("root")).render(<App />);
