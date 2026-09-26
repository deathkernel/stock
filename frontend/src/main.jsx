import React,{useMemo,useState} from "react";
import {createRoot} from "react-dom/client";
import "./styles.css";

function Metric({label,value,help}){return <div className="metric"><div className="label">{label}<span title={help}>ⓘ</span></div><strong>{value}</strong></div>}

function PriceChart({history,forecast}){
  const points=history||[];
  const values=points.map(x=>Number(x.close)).filter(Number.isFinite);
  if(values.length<2)return <div className="chart-empty">Not enough historical data for a chart.</div>;
  const width=900,height=300,pad=28;
  const min=Math.min(...values,Number(forecast?.lower)||Infinity);
  const max=Math.max(...values,Number(forecast?.upper)||-Infinity);
  const span=Math.max(max-min,1e-9);
  const xy=(v,i,n=values.length)=>({x:pad+(i/(n-1))*(width-pad*2),y:height-pad-((v-min)/span)*(height-pad*2)});
  const line=values.map((v,i)=>{const p=xy(v,i);return (i?"L":"M")+p.x.toFixed(1)+" "+p.y.toFixed(1)}).join(" ");
  const last=xy(values.at(-1),values.length-1);
  const future=forecast?.point?xy(Number(forecast.point),values.length):null;
  const lower=forecast?.lower?xy(Number(forecast.lower),values.length):null;
  const upper=forecast?.upper?xy(Number(forecast.upper),values.length):null;
  return <div className="chart-wrap"><svg viewBox={"0 0 "+width+" "+height} role="img" aria-label="Historical price and forecast chart">
    <line x1={pad} x2={width-pad} y1={height-pad} y2={height-pad} className="gridline"/>
    <line x1={pad} x2={pad} y1={pad} y2={height-pad} className="gridline"/>
    <path d={line} className="price-line" fill="none"/>
    {future&&<><line x1={last.x} x2={future.x} y1={last.y} y2={future.y} className="forecast-line"/><line x1={future.x} x2={future.x} y1={upper.y} y2={lower.y} className="forecast-band"/><circle cx={future.x} cy={future.y} r="5" className="forecast-dot"/></>}
  </svg><div className="chart-legend"><span>Historical close</span><span>Forecast estimate</span><span>Forecast uncertainty range</span></div></div>
}

function RiskBars({risk}){
  if(!risk)return null;
  const items=Object.entries(risk.risk_contribution||{});
  return <div className="risk-bars">{items.map(([symbol,value])=><div className="risk-row" key={symbol}><div><strong>{symbol}</strong><span>{(value*100).toFixed(1)}%</span></div><div className="bar"><i style={{width:Math.min(100,value*100)+"%"}}/></div></div>)}</div>
}

function App(){
  const API_BASE_URL=(import.meta.env.VITE_API_BASE_URL||"http://127.0.0.1:8000").replace(/\/$/,"");\n  const [symbol,setSymbol]=useState(""); const [data,setData]=useState(null);
  const [loading,setLoading]=useState(false); const [error,setError]=useState(""); const [advanced,setAdvanced]=useState(false);
  const [portfolioInput,setPortfolioInput]=useState("AAPL:60, MSFT:40"); const [portfolio,setPortfolio]=useState(null); const [portfolioLoading,setPortfolioLoading]=useState(false);

  async function analyze(){
    const s=symbol.trim().toUpperCase(); if(!s)return;
    setLoading(true);setError("");setData(null);
    try{const r=await fetch(API_BASE_URL+"/api/market/"+encodeURIComponent(s)+"/research?horizon=5&outputsize=500");if(!r.ok)throw new Error((await r.json()).detail||"Analysis failed");setData(await r.json())}
    catch(e){setError(e.message)}finally{setLoading(false)}
  }

  async function analyzePortfolio(){
    const positions=portfolioInput.split(",").map(x=>x.trim()).filter(Boolean).map(x=>{const [symbol,weight]=x.split(":");return {symbol:symbol.trim(),weight:Number(weight)}});
    if(!positions.length||positions.some(x=>!x.symbol||!Number.isFinite(x.weight))){setError("Use AAPL:60, MSFT:40");return}
    setPortfolioLoading(true);setError("");
    try{const r=await fetch(API_BASE_URL+"/api/portfolio/analyze-symbols",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({positions,confidence:0.95})});if(!r.ok)throw new Error((await r.json()).detail||"Portfolio analysis failed");setPortfolio(await r.json())}
    catch(e){setError(e.message)}finally{setPortfolioLoading(false)}
  }

  const f=data?.forecast,b=data?.backtest,risk=data?.risk,c=data?.confidence;
  const move=f?((f.point/f.last_price-1)*100):0;
  const outlook=move>2?"Positive outlook":move<-2?"Negative outlook":"Mixed / neutral outlook";
  const history=useMemo(()=>data?.history||[],[data]);

  return <main>
    <header><div><div className="eyebrow">RESEARCH & DECISION SUPPORT</div><h1>Stock Intelligence</h1><p>Understand a stock in one screen — forecast, risk, evidence and uncertainty.</p></div></header>
    <section className="search"><input value={symbol} onChange={e=>setSymbol(e.target.value)} onKeyDown={e=>e.key==="Enter"&&analyze()} placeholder="Enter a stock symbol, e.g. AAPL"/><button onClick={analyze} disabled={loading}>{loading?"Analyzing…":"Analyze stock"}</button></section>
    {error&&<div className="error">{error}</div>}
    {!data&&!loading&&<section className="welcome"><h2>Start with a stock symbol</h2><p>You'll get a simple overview first. Technical and model details stay below so the screen doesn't become a cockpit.</p></section>}

    <section className="panel portfolio-box"><div className="panel-title"><h3>Portfolio risk lab</h3><span>Research view</span></div><p className="muted">Enter positions as SYMBOL:WEIGHT. Weights are normalized automatically.</p><div className="search"><input value={portfolioInput} onChange={e=>setPortfolioInput(e.target.value)} placeholder="AAPL:60, MSFT:40"/><button onClick={analyzePortfolio} disabled={portfolioLoading}>{portfolioLoading?"Calculating…":"Analyze portfolio"}</button></div>
      {portfolio&&<><div className="metrics compact"><Metric label="Annualized volatility" value={(portfolio.analysis.annualized_volatility*100).toFixed(1)+"%"} help="Historical portfolio volatility."/><Metric label="Historical VaR" value={(portfolio.analysis.var*100).toFixed(2)+"%"} help="Historical one-day loss threshold."/><Metric label="CVaR" value={(portfolio.analysis.cvar*100).toFixed(2)+"%"} help="Average loss beyond VaR."/><Metric label="Max drawdown" value={(portfolio.analysis.max_drawdown*100).toFixed(1)+"%"} help="Largest historical peak-to-trough decline."/></div><div className="panel-inner"><h4>Risk contribution</h4><RiskBars risk={portfolio.analysis}/></div></>}
    </section>

    {data&&<div className="results">
      <section className="hero"><div><div className="eyebrow">{data.symbol}</div><h2>{outlook}</h2><p>5-day model estimate based on available market history.</p></div><div className="hero-number">{move>=0?"+":""}{move.toFixed(2)}%</div></section>
      <section className="metrics"><Metric label="Estimated price" value={f.point.toFixed(2)} help="Model estimate, not a guaranteed future price."/><Metric label="Model confidence" value={c?.label||"—"} help="Combines data quality, model agreement and historical validation."/><Metric label="Market regime" value={(data.regime?.regime||"—").replaceAll("_"," ")} help="Current trend and volatility classification."/><Metric label="Annualized risk" value={risk?((risk.annualized_volatility*100).toFixed(1)+"%"):"—"} help="Historical annualized volatility."/></section>
      <section className="panel"><div className="panel-title"><h3>Price & forecast</h3><span>{history.length} historical observations</span></div><PriceChart history={history} forecast={f}/><p className="muted">The line shows historical closing prices. The forecast marker is a model estimate; the vertical range represents forecast uncertainty.</p></section>
      <section className="panel"><div className="panel-title"><h3>What the model is saying</h3><span>Research view</span></div><div className="range"><span>Estimated range</span><strong>{f.lower.toFixed(2)} — {f.upper.toFixed(2)}</strong></div><p className="muted">Wider ranges mean less precise forecasts. Historical validation is shown below.</p></section>
      <section className="panel"><div className="panel-title"><h3>Evidence</h3><span>Historical validation</span></div><div className="metrics compact"><Metric label="Directional accuracy" value={b?((b.directional_accuracy*100).toFixed(1)+"%"):"—"} help="Share of historical walk-forward forecasts that got direction right."/><Metric label="Baseline improvement" value={b?((b.improvement_vs_baseline*100).toFixed(1)+"%"):"—"} help="Relative MAE improvement versus a last-price baseline."/><Metric label="Return correlation" value={b?b.return_correlation.toFixed(2):"—"} help="Correlation between predicted and realized returns in validation."/><Metric label="Validation samples" value={b?.observations??"—"} help="Number of walk-forward validation observations."/></div></section>
      <section className="panel"><div className="panel-title"><h3>Risk & scenarios</h3><span>Historical + modeled scenarios</span></div><div className="metrics compact"><Metric label="Max drawdown" value={risk?((risk.max_drawdown*100).toFixed(1)+"%"):"—"} help="Largest historical peak-to-trough decline."/><Metric label="Sharpe" value={risk?.sharpe?.toFixed(2)||"—"} help="Historical risk-adjusted return ratio."/><Metric label="Annual return" value={risk?((risk.annualized_return*100).toFixed(1)+"%"):"—"} help="Annualized historical return, not a forecast."/><Metric label="Data quality" value={data.data_quality?.score!=null?(data.data_quality.score*100).toFixed(0)+"%":"—"} help="Quality score for the fetched historical dataset."/></div></section>
      <button className="details-toggle" onClick={()=>setAdvanced(!advanced)}>{advanced?"Hide":"Show"} technical details</button>
      {advanced&&<section className="panel advanced"><pre>{JSON.stringify({forecast:f,ml:data.ml_forecast,fused_ml:data.fused_ml_forecast,risk,regime:data.regime,backtest:b,scenarios:data.scenarios,data_quality:data.data_quality},null,2)}</pre></section>}
    </div>}
    <footer>Research outputs are probabilistic and can be wrong. They are not guaranteed returns or personalized financial advice.</footer>
  </main>
}
createRoot(document.getElementById("root")).render(<App/>);
