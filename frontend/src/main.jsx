import React,{useState} from "react";
import {createRoot} from "react-dom/client";
import "./styles.css";

function Metric({label,value,help}){return <div className="metric"><div className="label">{label}<span title={help}>ⓘ</span></div><strong>{value}</strong></div>}

function App(){
  const [symbol,setSymbol]=useState(""); const [data,setData]=useState(null);
  const [loading,setLoading]=useState(false); const [error,setError]=useState(""); const [advanced,setAdvanced]=useState(false);
  async function analyze(){
    const s=symbol.trim().toUpperCase(); if(!s)return;
    setLoading(true);setError("");setData(null);
    try{
      const r=await fetch("http://localhost:8000/api/market/"+encodeURIComponent(s)+"/research?horizon=5&outputsize=500");
      if(!r.ok)throw new Error((await r.json()).detail||"Analysis failed");
      setData(await r.json());
    }catch(e){setError(e.message)}finally{setLoading(false)}
  }
  const f=data?.forecast,b=data?.backtest,risk=data?.risk,c=data?.confidence;
  const move=f?((f.point/f.last_price-1)*100):0;
  const outlook=move>2?"Positive outlook":move<-2?"Negative outlook":"Mixed / neutral outlook";
  return <main>
    <header><div><div className="eyebrow">RESEARCH & DECISION SUPPORT</div><h1>Stock Intelligence</h1><p>Understand a stock in one screen — forecast, risk, evidence and uncertainty.</p></div></header>
    <section className="search"><input value={symbol} onChange={e=>setSymbol(e.target.value)} onKeyDown={e=>e.key==="Enter"&&analyze()} placeholder="Enter a stock symbol, e.g. AAPL"/><button onClick={analyze} disabled={loading}>{loading?"Analyzing…":"Analyze stock"}</button></section>
    {error&&<div className="error">{error}</div>}
    {!data&&!loading&&<section className="welcome"><h2>Start with a stock symbol</h2><p>You'll get a simple overview first. Technical and model details stay below so the screen doesn't become a cockpit.</p></section>}
    {data&&<div className="results">
      <section className="hero"><div><div className="eyebrow">{data.symbol}</div><h2>{outlook}</h2><p>5-day model estimate based on available market history.</p></div><div className="hero-number">{move>=0?"+":""}{move.toFixed(2)}%</div></section>
      <section className="metrics">
        <Metric label="Estimated price" value={f.point.toFixed(2)} help="Model estimate, not a guaranteed future price."/>
        <Metric label="Model confidence" value={c?.label||"—"} help="Combines data quality, model agreement and historical validation."/>
        <Metric label="Market regime" value={(data.regime?.regime||"—").replaceAll("_"," ")} help="Current trend and volatility classification."/>
        <Metric label="Annualized risk" value={risk?((risk.annualized_volatility*100).toFixed(1)+"%"):"—"} help="Historical annualized volatility."/>
      </section>
      <section className="panel"><div className="panel-title"><h3>What the model is saying</h3><span>Research view</span></div><div className="range"><span>Estimated range</span><strong>{f.lower.toFixed(2)} — {f.upper.toFixed(2)}</strong></div><p className="muted">The range shows uncertainty around the estimate. Wider ranges mean less precise forecasts.</p></section>
      <section className="panel"><div className="panel-title"><h3>Evidence</h3><span>Historical validation</span></div><div className="metrics compact">
        <Metric label="Directional accuracy" value={b?((b.directional_accuracy*100).toFixed(1)+"%"):"—"} help="Share of historical walk-forward forecasts that got direction right."/>
        <Metric label="Baseline improvement" value={b?((b.improvement_vs_baseline*100).toFixed(1)+"%"):"—"} help="Relative MAE improvement versus a last-price baseline."/>
        <Metric label="Return correlation" value={b?b.return_correlation.toFixed(2):"—"} help="Correlation between predicted and realized returns in validation."/>
        <Metric label="Validation samples" value={b?.observations??"—"} help="Number of walk-forward validation observations."/>
      </div></section>
      <button className="details-toggle" onClick={()=>setAdvanced(!advanced)}>{advanced?"Hide":"Show"} technical details</button>
      {advanced&&<section className="panel advanced"><pre>{JSON.stringify({forecast:f,ml:data.ml_forecast,risk,regime:data.regime,backtest:b,scenarios:data.scenarios,data_quality:data.data_quality},null,2)}</pre></section>}
    </div>}
    <footer>Research outputs are probabilistic and can be wrong. They are not guaranteed returns or personalized financial advice.</footer>
  </main>
}
createRoot(document.getElementById("root")).render(<App/>);
