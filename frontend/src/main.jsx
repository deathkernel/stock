import React from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

function App() {
  const cards = [
    ["Forecast", "Probabilistic multi-model forecast"],
    ["Risk", "Volatility, drawdown and Sharpe"],
    ["Fundamentals", "Financial health and valuation"],
    ["Sentiment", "News and event intelligence"],
    ["Backtest", "Walk-forward model validation"],
    ["Explainability", "Why the system reached its result"],
  ];
  return <main>
    <header><h1>Stock Intelligence</h1><p>Research, forecasting and decision support</p></header>
    <section className="search"><input placeholder="Enter ticker e.g. AAPL"/><button>Analyze</button></section>
    <section className="grid">{cards.map(([title, desc]) =>
      <article key={title}><h2>{title}</h2><p>{desc}</p><span>Module ready</span></article>
    )}</section>
    <footer>Forecasts are probabilistic research outputs, not guaranteed returns.</footer>
  </main>;
}
createRoot(document.getElementById("root")).render(<App />);
