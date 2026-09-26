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

    if (showEma) {
      const emaSeries = chart.addSeries(LineSeries, {
        color: "#5aa9ff",
        lineWidth: 2,
        priceLineVisible: false,
        lastValueVisible: false,
      });
      emaSeries.setData(exponentialMovingAverage(visible, 50, "close"));
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
  }, [visible, showSma, showEma, showVolume, forecast]);

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
          <button className={showVolume ? "active" : ""} onClick={() => setShowVolume(!showVolume)}>Volume</button>
        </div>
      </div>
      <div ref={containerRef} className="chart-host" />
    </div>
  );
}
