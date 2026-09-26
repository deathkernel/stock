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

