export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  const { t } = req.query;
  if (!t) return res.status(400).json({ error: 'tickers required' });
  const symbols = t.split(',').slice(0, 50).join(',');
  const fields = 'regularMarketPrice,regularMarketChange,regularMarketChangePercent,shortName,longName,regularMarketVolume,fiftyTwoWeekHigh,fiftyTwoWeekLow,marketCap,trailingPE';
  const url = `https://query1.finance.yahoo.com/v7/finance/quote?symbols=${encodeURIComponent(symbols)}&fields=${fields}`;
  try {
    const r = await fetch(url, {
      headers: { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36' }
    });
    const data = await r.json();
    res.setHeader('Cache-Control', 'public, s-maxage=60, stale-while-revalidate=120');
    res.json(data);
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
}
