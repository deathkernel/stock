import React,{useMemo,useState} from "react";
import {createRoot} from "react-dom/client";
import "./styles.css";

function Metric({label,value,help}){return <div className="metric"><div className="label">{label}<span title={help}>ⓘ</span></div><strong>{value}</strong></div>}

function PriceChart({history,forecast}){
  const points=(history||[]).filter(x=>Number.isFinite(Number(x.close))).slice(-120);
  const [mode,setMode]=useState("Candles");
  const [indicator,setIndicator]=useState("SMA 20");
  if(points.length<2)return <div className="chart-empty">Not enough historical data for a chart.</div>;
  const width=1100,height=430,pad={l:62,r:18,t:22,b:38};
  const closes=points.map(x=>Number(x.close));
  const highs=points.map(x=>Number(x.high)||Number(x.close));
  const lows=points.map(x=>Number(x.low)||Number(x.close));
  const future=[Number(forecast?.lower),Number(forecast?.upper),Number(forecast?.point)].filter(Number.isFinite);
  const min=Math.min(...lows,...future),max=Math.max(...highs,...future),span=Math.max(max-min,1e-9);
  const x=i=>pad.l+(i/(points.length-1))*(width-pad.l-pad.r);
  const y=v=>pad.t+(1-(v-min)/span)*(height-pad.t-pad.b);
  const candleW=Math.max(2,Math.min(9,(width-pad.l-pad.r)/points.length*.62));
  const sma=(n,i)=>i<n-1?null:closes.slice(i-n+1,i+1).reduce((a,b)=>a+b,0)/n;
  const linePath=points.map((_,i)=>{const v=sma(20,i);return v==null?"":(i?"L":"M")+x(i).toFixed(1)+" "+y(v).toFixed(1)}).filter(Boolean).join(" ");
  const last=points.length-1, lastClose=closes[last], fx=x(last)+55;
  const fy=forecast?.point?y(Number(forecast.point)):y(lastClose);
  return <div className="tv-chart">
    <div className="chart-toolbar">
      <div className="chart-tabs"><button className="active">{points.length}D</button><button>1W</button><button>1M</button><button>1Y</button></div>
      <div className="chart-tabs"><button className={mode==="Candles"?"active":""} onClick={()=>setMode("Candles")}>Candles</button><button className={mode==="Line"?"active":""} onClick={()=>setMode("Line")}>Line</button><button className={indicator?"active":""} onClick={()=>setIndicator(indicator?"":"SMA 20")}>{indicator||"Indicators"}</button></div>
    </div>
    <div className="chart-canvas"><svg viewBox={`0 0 ${width} ${height}`} role="img" aria-label="Trading chart">
      {[0,1,2,3,4].map(i=><line key={i} x1={pad.l} x2={width-pad.r} y1={pad.t+i*(height-pad.t-pad.b)/4} y2={pad.t+i*(height-pad.t-pad.b)/4} className="tv-grid"/>)}
      {[0,1,2,3,4,5].map(i=><line key={i} x1={pad.l+i*(width-pad.l-pad.r)/5} x2={pad.l+i*(width-pad.l-pad.r)/5} y1={pad.t} y2={height-pad.b} className="tv-grid"/>)}
      {mode==="Line" ? <path d={closes.map((v,i)=>(i?"L":"M")+x(i)+" "+y(v)).join(" ")} className="tv-line" fill="none"/> : points.map((p,i)=>{const o=Number(p.open)||closes[i],h=highs[i],l=lows[i],cl=closes[i],up=cl>=o;return <g key={i} className={up?"candle up":"candle down"}><line x1={x(i)} x2={x(i)} y1={y(h)} y2={y(l)}/><rect x={x(i)-candleW/2} y={Math.min(y(o),y(cl))} width={candleW} height={Math.max(1,Math.abs(y(cl)-y(o)))}/></g>})}
      {indicator&&<path d={linePath} className="sma-line" fill="none"/>}
      {forecast?.point&&<><line x1={x(last)} x2={fx} y1={y(lastClose)} y2={fy} className="forecast-line"/><line x1={fx} x2={fx} y1={y(Number(forecast.upper))} y2={y(Number(forecast.lower))} className="forecast-band"/><circle cx={fx} cy={fy} r="5" className="forecast-dot"/></>}
      <text x={width-pad.r-8} y={y(lastClose)-7} className="price-tag">{lastClose.toFixed(2)}</text>
      {forecast?.point&&<text x={Math.min(fx+8,width-105)} y={fy-8} className="forecast-tag">Forecast</text>}
    </svg></div>
    <div className="chart-footer"><span>O {Number(points[last].open||lastClose).toFixed(2)}</span><span>H {highs[last].toFixed(2)}</span><span>L {lows[last].toFixed(2)}</span><span>C {lastClose.toFixed(2)}</span><span className="legend-sma">SMA 20</span><span className="legend-forecast">Model forecast</span></div>
  </div>
}


function RiskBars({risk}){
  if(!risk)return null;
  const items=Object.entries(risk.risk_contribution||{});
  return <div className="risk-bars">{items.map(([symbol,value])=><div className="risk-row" key={symbol}><div><strong>{symbol}</strong><span>{(value*100).toFixed(1)}%</span></div><div className="bar"><i style={{width:Math.min(100,value*100)+"%"}}/></div>)}</div>
}

function App(){
  const API_BASE_URL=(import.meta.env.VITE_API_BASE_URL||"http://127.0.0.1:8000").replace(/\/$/,"");
  const [symbol,setSymbol]=useState("");
  const [data,setData]=useState(null);
  const [loading,setLoading]=useState(false);
  const [error,setError]=useState("");
  const [advanced,setAdvanced]=useState(false);
  const [portfolioInput,setPortfolioInput]=useState("AAPL:60, MSFT:40");
  const [portfolio,setPortfolio]=useState(null);
  const [portfolioLoading,setPortfolioLoading]=useState(false);

  async function analyze(){
    const s=symbol.trim().toUpperCase();
    if(!s)return;
    setLoading(true);setError("");setData(null);
    try{
      const r=await fetch(API_BASE_URL+"/api/market/"+encodeURIComponent(s)+"/research?horizon=5&outputsize=500");
      if(!r.ok)throw new Error((await r.json()).detail||"Analysis failed");
      setData(await r.json());
    }catch(e){setError(e.message)}finally{setLoading(false)}
  }

  async function analyzePortfolio(){
    const positions=portfolioInput.split(",").map(x=>x.trim()).filter(Boolean).map(x=>{
      const [symbol,weight]=x.split(":");
      return {symbol:symbol.trim(),weight:Number(weight)}
    });
    if(!positions.length||positions.some(x=>!x.symbol||!Number.isFinite(x.weight))){
      setError("Use AAPL:60, MSFT:40");return;
    }
    setPortfolioLoading(true);setError("");
    try{
      const r=await fetch(API_BASE_URL+"/api/portfolio/analyze-symbols",{
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({positions,confidence:0.95})
      });
      if(!r.ok)throw new Error((await r.json()).detail||"Portfolio analysis failed");
      setPortfolio(await r.json());
    }catch(e){setError(e.message)}finally{setPortfolioLoading(false)}
  }

  const f=data?.forecast,b=data?.backtest,risk=data?.risk,c=data?.confidence;
  const move=f&&f.last_price?((f.point/f.last_price-1)*100):0;
  const outlook=move>2?"Positive outlook":move<-2?"Negative outlook":"Mixed / neutral outlook";
  const history=useMemo(()=>data?.history||[],[data]);

  return <main>
    <header className="topbar">
      <div className="brand">
        <div className="logo-mark">S</div>
        <div><strong>Stock Intelligence</strong><span>Markets · Research</span></div>
      </div>
      <div className="market-status"><span className="status-dot"></span> Market data</div>
    </header>

    <section className="search tv-search">
      <span className="search-icon">⌕</span>
      <input value={symbol} onChange={e=>setSymbol(e.target.value)} onKeyDown={e=>e.key==="Enter"&&analyze()} placeholder="Search symbol, e.g. AAPL or RELIANCE"/>
      <button onClick={analyze} disabled={loading}>{loading?"Analyzing…":"Analyze"}</button>
    </section>

    {error&&<div className="error">{error}</div>}

    {!data&&!loading&&<section className="welcome">
      <div className="eyebrow">MARKET RESEARCH TERMINAL</div>
      <h2>Search a stock to begin</h2>
      <p>TradingView-inspired charting with forecasts, model validation, technical evidence and risk analytics.</p>
    </section>}

    <section className="panel portfolio-box">
      <div className="panel-title"><h3>Portfolio risk lab</h3><span>Research view</span></div>
      <p className="muted">Enter positions as SYMBOL:WEIGHT. Weights are normalized automatically.</p>
      <div className="search">
        <input value={portfolioInput} onChange={e=>setPortfolioInput(e.target.value)} placeholder="AAPL:60, MSFT:40"/>
        <button onClick={analyzePortfolio} disabled={portfolioLoading}>{portfolioLoading?"Calculating…":"Analyze portfolio"}</button>
      </div>
      {portfolio&&<><div className="metrics compact">
        <Metric label="Annualized volatility" value={(portfolio.analysis.annualized_volatility*100).toFixed(1)+"%"} help="Historical portfolio volatility."/>
        <Metric label="Historical VaR" value={(portfolio.analysis.var*100).toFixed(2)+"%"} help="Historical one-day loss threshold."/>
        <Metric label="CVaR" value={(portfolio.analysis.cvar*100).toFixed(2)+"%"} help="Average loss beyond VaR."/>
        <Metric label="Max drawdown" value={(portfolio.analysis.max_drawdown*100).toFixed(1)+"%"} help="Largest historical peak-to-trough decline."/>
      </div><div className="panel-inner"><h4>Risk contribution</h4><RiskBars risk={portfolio.analysis}/></div></>}
    </section>

    {data&&<div className="results">
      <section className="hero">
        <div><div className="eyebrow">{data.symbol}</div><h2>{outlook}</h2><p>5-day model estimate based on available market history.</p></div>
        <div className="hero-number">{move>=0?"+":""}{move.toFixed(2)}%</div>
      </section>

      <section className="metrics">
        <Metric label="Estimated price" value={f.point.toFixed(2)} help="Model estimate, not a guaranteed future price."/>
        <Metric label="Model confidence" value={c?.label||"—"} help="Combines data quality, model agreement and historical validation."/>
        <Metric label="Market regime" value={(data.regime?.regime||"—").replaceAll("_"," ")} help="Current trend and volatility classification."/>
        <Metric label="Annualized risk" value={risk?((risk.annualized_volatility*100).toFixed(1)+"%"):"—"} help="Historical annualized volatility."/>
      </section>

      <section className="panel chart-panel">
        <div className="panel-title"><h3>{data.symbol} <small>· Daily</small></h3><span>{history.length} observations</span></div>
        <PriceChart history={history} forecast={f}/>
        <p className="muted">Candles show OHLC history. SMA 20 is a technical overlay. The forecast marker is a model estimate with an uncertainty range.</p>
      </section>

      <section className="panel">
        <div className="panel-title"><h3>Forecast</h3><span>5-day horizon</span></div>
        <div className="range"><span>Estimated range</span><strong>{f.lower.toFixed(2)} — {f.upper.toFixed(2)}</strong></div>
        <p className="muted">Wider ranges indicate less precise forecasts. Forecasts are probabilistic research outputs.</p>
      </section>

      <section className="panel">
        <div className="panel-title"><h3>Validation evidence</h3><span>Historical walk-forward</span></div>
        <div className="metrics compact">
          <Metric label="Directional accuracy" value={b?((b.directional_accuracy*100).toFixed(1)+"%"):"—"} help="Share of historical forecasts that got direction right."/>
          <Metric label="Baseline improvement" value={b?((b.improvement_vs_baseline*100).toFixed(1)+"%"):"—"} help="Relative MAE improvement versus a last-price baseline."/>
          <Metric label="Return correlation" value={b?b.return_correlation.toFixed(2):"—"} help="Correlation between predicted and realized returns."/>
          <Metric label="Validation samples" value={b?.observations??"—"} help="Number of validation observations."/>
        </div>
      </section>

      <section className="panel">
        <div className="panel-title"><h3>Model comparison</h3><span>Out-of-sample test</span></div>
        <div className="model-list">{(data.model_comparison||[]).map((m,i)=><div className="model-row" key={m.model}>
          <div><strong>{i===0?"Selected: ":""}{m.model.replaceAll("_"," ")}</strong><span>Direction {(m.directional_accuracy*100).toFixed(1)}%</span></div>
          <div><span>MAE {m.mae.toFixed(2)}</span><span>RMSE {m.rmse.toFixed(2)}</span></div>
        </div>)}</div>
      </section>

      <section className="panel">
        <div className="panel-title"><h3>Feature importance</h3><span>Model diagnostics</span></div>
        <div className="model-list">{(data.feature_importance?.features||[]).slice(0,6).map(x=><div className="model-row" key={x.feature}>
          <div><strong>{x.feature.replaceAll("_"," ")}</strong></div><div><span>{(x.relative_importance*100).toFixed(1)}%</span></div>
        </div>)}</div>
        <p className="muted">Permutation importance is diagnostic and does not prove causation.</p>
      </section>

      <section className="panel">
        <div className="panel-title"><h3>Risk & scenarios</h3><span>Historical + modeled</span></div>
        <div className="metrics compact">
          <Metric label="Max drawdown" value={risk?((risk.max_drawdown*100).toFixed(1)+"%"):"—"} help="Largest historical peak-to-trough decline."/>
          <Metric label="Sharpe" value={risk?.sharpe?.toFixed(2)||"—"} help="Historical risk-adjusted return ratio."/>
          <Metric label="Annual return" value={risk?((risk.annualized_return*100).toFixed(1)+"%"):"—"} help="Annualized historical return, not a forecast."/>
          <Metric label="Data quality" value={data.data_quality?.score!=null?(data.data_quality.score*100).toFixed(0)+"%":"—"} help="Quality score for fetched historical data."/>
        </div>
      </section>

      <button className="details-toggle" onClick={()=>setAdvanced(!advanced)}>{advanced?"Hide":"Show"} technical details</button>
      {advanced&&<section className="panel advanced"><pre>{JSON.stringify({
        forecast:f,ml:data.ml_forecast,fused_ml:data.fused_ml_forecast,risk,
        regime:data.regime,backtest:b,scenarios:data.scenarios,data_quality:data.data_quality
      },null,2)}</pre></section>}
    </div>}

    <footer>Research outputs are probabilistic and can be wrong. They are not guaranteed returns or personalized financial advice.</footer>
  </main>
}

createRoot(document.getElementById("root")).render(<App/>);
