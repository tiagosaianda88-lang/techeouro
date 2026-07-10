const MARKET_SERIES = [
  { symbol: "^GSPC", name: "S&P 500", color: "#d4af37" },
  { symbol: "^IXIC", name: "Nasdaq", color: "#35c98f" },
  { symbol: "^DJI", name: "Dow Jones", color: "#e7e7e7" },
  { symbol: "^FTSE", name: "FTSE 100", color: "#4ea1ff" },
  { symbol: "^N225", name: "Nikkei 225", color: "#ef6f6c" },
];

const jsonHeaders = {
  "Content-Type": "application/json; charset=utf-8",
  "Cache-Control": "public, max-age=900, must-revalidate",
  "Netlify-CDN-Cache-Control": "public, durable, max-age=10800, stale-while-revalidate=1800",
};

export default async (request: Request) => {
  if (request.method !== "GET") {
    return new Response(JSON.stringify({ error: "Method not allowed" }), {
      status: 405,
      headers: { "Content-Type": "application/json; charset=utf-8" },
    });
  }

  const symbols = MARKET_SERIES.map((item) => item.symbol).join(",");
  const endpoint = new URL("https://query2.finance.yahoo.com/v7/finance/spark");
  endpoint.searchParams.set("symbols", symbols);
  endpoint.searchParams.set("range", "1mo");
  endpoint.searchParams.set("interval", "1d");

  try {
    const response = await fetch(endpoint, {
      headers: {
        Accept: "application/json",
        "User-Agent": "Mozilla/5.0 (compatible; TechOuroTerminal/1.0)",
      },
    });

    if (!response.ok) throw new Error(`Market source returned ${response.status}`);

    const payload = await response.json();
    const rawResults = payload?.spark?.result;
    if (!Array.isArray(rawResults) || rawResults.length === 0) {
      throw new Error("Market source returned no series");
    }

    const bySymbol = new Map(rawResults.map((item: any) => [item.symbol, item]));
    const prepared = MARKET_SERIES.map((definition) => {
      const raw = bySymbol.get(definition.symbol) as any;
      const chart = raw?.response?.[0];
      const timestamps = Array.isArray(chart?.timestamp) ? chart.timestamp : [];
      const closes = Array.isArray(chart?.indicators?.quote?.[0]?.close)
        ? chart.indicators.quote[0].close
        : [];

      const points = timestamps
        .map((timestamp: number, index: number) => ({
          date: new Date(timestamp * 1000).toISOString().slice(0, 10),
          close: Number(closes[index]),
        }))
        .filter((point: { close: number }) => Number.isFinite(point.close) && point.close > 0);

      if (points.length < 2) throw new Error(`Incomplete series for ${definition.symbol}`);

      const previous = points[points.length - 2].close;
      const latest = points[points.length - 1].close;
      const changePercent = previous ? ((latest - previous) / previous) * 100 : 0;

      return {
        ...definition,
        currency: chart?.meta?.currency || "",
        latest,
        changePercent,
        points,
      };
    });

    const labels = Array.from(
      new Set(prepared.flatMap((series) => series.points.map((point) => point.date))),
    ).sort();

    const series = prepared.map((item) => {
      const first = item.points[0].close;
      const valuesByDate = new Map(
        item.points.map((point) => [point.date, Number(((point.close / first) * 100).toFixed(2))]),
      );

      return {
        symbol: item.symbol,
        name: item.name,
        color: item.color,
        values: labels.map((label) => valuesByDate.get(label) ?? null),
      };
    });

    const quotes = prepared.map((item) => ({
      symbol: item.symbol,
      name: item.name,
      currency: item.currency,
      price: Number(item.latest.toFixed(2)),
      changePercent: Number(item.changePercent.toFixed(2)),
    }));

    return new Response(
      JSON.stringify({
        source: "Yahoo Finance",
        range: "1mo",
        interval: "1d",
        updatedAt: new Date().toISOString(),
        marketDate: labels[labels.length - 1],
        labels,
        series,
        quotes,
      }),
      { headers: jsonHeaders },
    );
  } catch (error) {
    console.error("Market data unavailable", error);
    return new Response(
      JSON.stringify({
        error: "Market data temporarily unavailable",
        updatedAt: new Date().toISOString(),
      }),
      {
        status: 503,
        headers: {
          "Content-Type": "application/json; charset=utf-8",
          "Cache-Control": "no-store",
        },
      },
    );
  }
};

export const config = {
  path: "/api/market-data",
};
