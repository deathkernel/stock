import React, { useEffect, useMemo, useRef } from "react";
import {
  CandlestickSeries,
  ColorType,
  CrosshairMode,
  HistogramSeries,
  LineSeries,
  LineStyle,
  createChart,
} from "lightweight-charts";

function dayKey(value) {
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? null : date.toISOString().slice(0, 10);
}

function businessDaysAfter(value, count) {
  const date = new Date(value);
  let remaining = count;
  while (remaining > 0) {
    date.setUTCDate(date.getUTCDate() + 1);
    const day = date.getUTCDay();
    if (day !== 0 && day !== 6) remaining -= 1;
  }
  return date.toISOString().slice(0, 10);
}

function bollingerBands(values, period = 20, multiplier = 2) {
  const output = [];
  for (let i = period - 1; i < values.length; i += 1) {
    const slice = values.slice(i - period + 1, i + 1).map((row) => row.close);
    const middle = slice.reduce((sum, value) => sum + value, 0) / period;
    const variance = slice.reduce((sum, value) => sum + (value - middle) ** 2, 0) / period;
    const std = Math.sqrt(variance);
    output.push({
      time: values[i].time,
      upper: middle + multiplier * std,
      middle,
      lower: middle - multiplier * std,
    });
  }
  return output;
}

function relativeStrengthIndex(values, period = 14) {
  if (values.length <= period) return [];
  const output = [];
  let gains = 0;
  let losses = 0;

  for (let i = 1; i <= period; i += 1) {
    const change = values[i].close - values[i - 1].close;
    gains += Math.max(change, 0);
    losses += Math.max(-change, 0);
  }

  let avgGain = gains / period;
  let avgLoss = losses / period;

  for (let i = period; i < values.length; i += 1) {
    if (i > period) {
      const change = values[i].close - values[i - 1].close;
      avgGain = ((avgGain * (period - 1)) + Math.max(change, 0)) / period;
      avgLoss = ((avgLoss * (period - 1)) + Math.max(-change, 0)) / period;
    }
    const rs = avgLoss === 0 ? Infinity : avgGain / avgLoss;
    output.push({
      time: values[i].time,
      value: avgLoss === 0 ? 100 : 100 - 100 / (1 + rs),
    });
  }
  return output;
}

function macd(values) {
  const fast = exponentialMovingAverage(values, 12);
  const slow = exponentialMovingAverage(values, 26);
  if (!fast.length || !slow.length) return { line: [], signal: [], histogram: [] };

  const slowMap = new Map(slow.map((row) => [row.time, row.value]));
  const line = fast
    .filter((row) => slowMap.has(row.time))
    .map((row) => ({ time: row.time, value: row.value - slowMap.get(row.time) }));

  const signal = exponentialMovingAverage(
    line.map((row) => ({ ...row, close: row.value })),
    9,
  );
  const signalMap = new Map(signal.map((row) => [row.time, row.value]));
  const histogram = line
    .filter((row) => signalMap.has(row.time))
    .map((row) => ({
      time: row.time,
      value: row.value - signalMap.get(row.time),
      color: row.value >= signalMap.get(row.time) ? "#26a69a99" : "#ef535099",
    }));

  return { line, signal, histogram };
}

function movingAverage(values, period, key) {
  const output = [];
  for (let i = period - 1; i < values.length; i += 1) {
    const slice = values.slice(i - period + 1, i + 1);
    output.push({
      time: values[i].time,
      value: slice.reduce((sum, row) => sum + Number(row[key]), 0) / period,
    });
  }
  return output;
}

function exponentialMovingAverage(values, period, key) {
  if (values.length < period) return [];
  const multiplier = 2 / (period + 1);
  let ema = values.slice(0, period).reduce((sum, row) => sum + Number(row[key]), 0) / period;
  const output = [{ time: values[period - 1].time, value: ema }];
  for (let i = period; i < values.length; i += 1) {
    ema = (Number(values[i][key]) - ema) * multiplier + ema;
    output.push({ time: values[i].time, value: ema });
  }
  return output;
}

export default function TradingChart({ history = [], forecast = null }) {
  const containerRef = useRef(null);
  const [range, setRange] = React.useState("3M");
  const [showSma, setShowSma] = React.useState(true);
  const [showEma, setShowEma] = React.useState(false);
  const [showVolume, setShowVolume] = React.useState(true);

  const candles = useMemo(
    () =>
      history
        .map((row) => ({
          time: dayKey(row.date),
          open: Number(row.open),
          high: Number(row.high),
          low: Number(row.low),
          close: Number(row.close),
          volume: Number(row.volume || 0),
        }))
        .filter(
          (row) =>
            row.time &&
            Number.isFinite(row.open) &&
            Number.isFinite(row.high) &&
            Number.isFinite(row.low) &&
            Number.isFinite(row.close)
        )
        .sort((a, b) => String(a.time).localeCompare(String(b.time))),
    [history]
  );

  const visible = useMemo(() => {
    const sizes = { "1D": 1, "5D": 5, "1M": 22, "3M": 66, "6M": 132, "1Y": 252, ALL: candles.length };
    return candles.slice(-Math.min(sizes[range] || candles.length, candles.length));
  }, [candles, range]);

  useEffect(() => {
    if (!containerRef.current || visible.length < 2) return undefined;

    const chart = createChart(containerRef.current, {
      autoSize: true,
      layout: {
        background: { type: ColorType.Solid, color: "#0b0f14" },
        textColor: "#8792a2",
        attributionLogo: true,
      },
      grid: {
        vertLines: { color: "#161c24" },
        horzLines: { color: "#161c24" },
      },
      crosshair: {
        mode: CrosshairMode.Magnet,
        vertLine: {
          color: "#596273",
          width: 1,
          style: LineStyle.Dashed,
          labelBackgroundColor: "#2a3342",
        },
        horzLine: {
          color: "#596273",
          width: 1,
          style: LineStyle.Dashed,
          labelBackgroundColor: "#2a3342",
        },
      },
      rightPriceScale: {
        borderColor: "#252d38",
        scaleMargins: { top: 0.08, bottom: 0.22 },
      },
      timeScale: {
        borderColor: "#252d38",
        timeVisible: false,
        secondsVisible: false,
        rightOffset: 6,
        barSpacing: visible.length > 100 ? 5 : 9,
      },
      handleScroll: true,
      handleScale: true,
    });

    const candleSeries = chart.addSeries(CandlestickSeries, {
      upColor: "#26a69a",
      downColor: "#ef5350",
      borderUpColor: "#26a69a",
      borderDownColor: "#ef5350",
      wickUpColor: "#26a69a",
      wickDownColor: "#ef5350",
      priceLineVisible: true,
      lastValueVisible: true,
    });
    candleSeries.setData(visible);

    if (showVolume) {
      const volumeSeries = chart.addSeries(HistogramSeries, {
        priceFormat: { type: "volume" },
        priceScaleId: "volume",
        base: 0,
      });
      volumeSeries.priceScale().applyOptions({
        scaleMargins: { top: 0.78, bottom: 0 },
      });
      volumeSeries.setData(
        visible.map((row) => ({
          time: row.time,
          value: row.volume || 0,
          color: row.close >= row.open ? "#26a69a66" : "#ef535066",
        }))
      );
    }

    if (showSma) {
      const smaSeries = chart.addSeries(LineSeries, {
        color: "#f6c453",
        lineWidth: 2,
        priceLineVisible: false,
        lastValueVisible: false,
      });
      smaSeries.setData(movingAverage(visible, 20, "close"));
    }


    if (showBbands && visible.length >= 20) {
      const bands = bollingerBands(visible, 20, 2);
      const upper = chart.addSeries(LineSeries, { color: "#9b87f5", lineWidth: 1, priceLineVisible: false, lastValueVisible: false, title: "BB Upper" });
      const middle = chart.addSeries(LineSeries, { color: "#777f8d", lineWidth: 1, priceLineVisible: false, lastValueVisible: false, title: "BB Mid" });
      const lower = chart.addSeries(LineSeries, { color: "#9b87f5", lineWidth: 1, priceLineVisible: false, lastValueVisible: false, title: "BB Lower" });
      upper.setData(bands.map((row) => ({ time: row.time, value: row.upper })));
      middle.setData(bands.map((row) => ({ time: row.time, value: row.middle })));
      lower.setData(bands.map((row) => ({ time: row.time, value: row.lower })));
    }

    if (showEma) {
      const emaSeries = chart.addSeries(LineSeries, {
        color: "#5aa9ff",
        lineWidth: 2,
        priceLineVisible: false,
        lastValueVisible: false,
      });
      emaSeries.setData(exponentialMovingAverage(visible, 50, "close"));
    }


    if (showRsi && visible.length >= 15) {
      const rsi = chart.addSeries(LineSeries, {
        color: "#c084fc",
        lineWidth: 2,
        priceLineVisible: false,
        lastValueVisible: true,
        title: "RSI 14",
      }, 1);
      rsi.setData(relativeStrengthIndex(visible, 14));
      rsi.createPriceLine({ price: 70, color: "#ef535077", lineWidth: 1, lineStyle: LineStyle.Dashed, axisLabelVisible: true, title: "70" });
      rsi.createPriceLine({ price: 30, color: "#26a69a77", lineWidth: 1, lineStyle: LineStyle.Dashed, axisLabelVisible: true, title: "30" });
    }

    if (showMacd && visible.length >= 35) {
      const values = macd(visible);
      const histogram = chart.addSeries(HistogramSeries, { priceFormat: { type: "price", precision: 3, minMove: 0.001 }, base: 0 }, 2);
      const line = chart.addSeries(LineSeries, { color: "#4da3ff", lineWidth: 2, priceLineVisible: false, lastValueVisible: true, title: "MACD" }, 2);
      const signal = chart.addSeries(LineSeries, { color: "#f6c453", lineWidth: 2, priceLineVisible: false, lastValueVisible: true, title: "Signal" }, 2);
      histogram.setData(values.histogram);
      line.setData(values.line);
      signal.setData(values.signal);
    }

    if (forecast && Number.isFinite(Number(forecast.point))) {
      const last = visible[visible.length - 1];
      const futureTime = businessDaysAfter(last.time, 5);
      const forecastSeries = chart.addSeries(LineSeries, {
        color: "#b18cff",
        lineWidth: 2,
        lineStyle: LineStyle.Dashed,
        priceLineVisible: false,
        lastValueVisible: true,
        title: "Forecast",
      });
      forecastSeries.setData([
        { time: last.time, value: last.close },
        { time: futureTime, value: Number(forecast.point) },
      ]);

      const point = Number(forecast.point);
      candleSeries.createPriceLine({
        price: point,
        color: "#b18cff",
        lineWidth: 1,
        lineStyle: LineStyle.Dashed,
        axisLabelVisible: true,
        title: "Forecast",
      });

      if (Number.isFinite(Number(forecast.lower))) {
        candleSeries.createPriceLine({
          price: Number(forecast.lower),
          color: "#7259a8",
          lineWidth: 1,
          lineStyle: LineStyle.Dotted,
          axisLabelVisible: true,
          title: "Lower",
        });
      }
      if (Number.isFinite(Number(forecast.upper))) {
        candleSeries.createPriceLine({
          price: Number(forecast.upper),
          color: "#7259a8",
          lineWidth: 1,
          lineStyle: LineStyle.Dotted,
          axisLabelVisible: true,
          title: "Upper",
        });
      }
    }

    chart.timeScale().fitContent();

    const resizeObserver = new ResizeObserver(() => chart.resize(containerRef.current.clientWidth, 520));
    resizeObserver.observe(containerRef.current);

    return () => {
      resizeObserver.disconnect();
      chart.remove();
    };
  }, [visible, showSma, showEma, showVolume, showBbands, showRsi, showMacd, forecast]);

  if (visible.length < 2) {
    return <div className="chart-empty">Not enough historical data for an interactive chart.</div>;
  }

  return (
    <div className="trading-chart">
      <div className="chart-toolbar">
        <div className="toolbar-group">
          {["1D", "5D", "1M", "3M", "6M", "1Y", "ALL"].map((item) => (
            <button
              key={item}
              className={range === item ? "active" : ""}
              onClick={() => setRange(item)}
            >
              {item}
            </button>
          ))}
        </div>
        <div className="toolbar-group indicators">
          <button className={showSma ? "active" : ""} onClick={() => setShowSma(!showSma)}>SMA 20</button>
          <button className={showEma ? "active" : ""} onClick={() => setShowEma(!showEma)}>EMA 50</button>
          <button className={showBbands ? "active" : ""} onClick={() => setShowBbands(!showBbands)}>BB</button>
          <button className={showRsi ? "active" : ""} onClick={() => setShowRsi(!showRsi)}>RSI 14</button>
          <button className={showMacd ? "active" : ""} onClick={() => setShowMacd(!showMacd)}>MACD</button>
          <button className={showVolume ? "active" : ""} onClick={() => setShowVolume(!showVolume)}>Volume</button>
        </div>
      </div>
      <div ref={containerRef} className="chart-host" />
    </div>
  );
}
