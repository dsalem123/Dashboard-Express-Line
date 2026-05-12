export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  const { t } = req.query;
  if (!t) return res.status(400).json({ error: 'tickers required' });

  const symbols = t.split(',').slice(0, 50);
  const UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36';

  const results = await Promise.allSettled(
    symbols.map(sym =>
      fetch(
        `https://query2.finance.yahoo.com/v8/finance/chart/${encodeURIComponent(sym)}?interval=1d&range=5d&includePrePost=false`,
        { headers: { 'User-Agent': UA, 'Accept': 'application/json', 'Accept-Language': 'en-US,en;q=0.9' } }
      ).then(r => r.json())
    )
  );

  const quotes = [];
  results.forEach((r, i) => {
    if (r.status !== 'fulfilled') return;
    const result = r.value?.chart?.result?.[0];
    const meta = result?.meta;
    if (!meta || meta.regularMarketPrice == null) return;

    // Previous close: use meta.previousClose if present, otherwise
    // extract from the closes array (second-to-last non-null value)
    let prevClose = meta.previousClose ?? null;
    if (prevClose == null) {
      const closes = (result?.indicators?.quote?.[0]?.close || []).filter(c => c != null);
      if (closes.length >= 2) prevClose = closes[closes.length - 2];
    }
    if (prevClose == null) prevClose = meta.regularMarketPrice;

    const price = meta.regularMarketPrice;
    const change = price - prevClose;
    const changePct = prevClose !== 0 ? (change / prevClose) * 100 : 0;

    quotes.push({
      symbol: symbols[i],
      regularMarketPrice: price,
      regularMarketChange: change,
      regularMarketChangePercent: changePct,
      shortName: meta.shortName || symbols[i],
      longName: meta.longName || meta.shortName || symbols[i],
      regularMarketVolume: meta.regularMarketVolume ?? null,
      fiftyTwoWeekHigh: meta.fiftyTwoWeekHigh ?? null,
      fiftyTwoWeekLow: meta.fiftyTwoWeekLow ?? null,
      marketCap: meta.marketCap ?? null,
      trailingPE: null
    });
  });

  res.setHeader('Cache-Control', 'public, s-maxage=60, stale-while-revalidate=120');
  res.json({ quoteResponse: { result: quotes } });
}
