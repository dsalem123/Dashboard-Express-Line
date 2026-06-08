const SOURCES = [
  { id: 'bbc',       name: 'BBC Business',      url: 'https://feeds.bbci.co.uk/news/business/rss.xml' },
  { id: 'cnbc',      name: 'CNBC',              url: 'https://www.cnbc.com/id/100003114/device/rss/rss.html' },
  { id: 'guardian',  name: 'The Guardian',       url: 'https://www.theguardian.com/business/rss' },
  { id: 'mwatch',    name: 'MarketWatch',        url: 'https://feeds.marketwatch.com/marketwatch/topstories/' },
  { id: 'reuters',   name: 'Reuters',            url: 'https://feeds.reuters.com/reuters/businessNews' },
  { id: 'ap',        name: 'AP News',            url: 'https://apnews.com/apf-business' },
  { id: 'infobae',   name: 'Infobae Economía',   url: 'https://www.infobae.com/feeds/rss/economia/' },
  { id: 'fed',       name: 'Federal Reserve',    url: 'https://www.federalreserve.gov/feeds/press_all.xml' },
  { id: 'imf',       name: 'IMF',               url: 'https://www.imf.org/en/News/rss?language=ENG' },
  { id: 'investing', name: 'Investing.com',      url: 'https://www.investing.com/rss/news_25.rss' },
];

function extractTag(block, tag) {
  const re = new RegExp(`<${tag}[^>]*>(?:<!\\[CDATA\\[)?([\\s\\S]*?)(?:\\]\\]>)?<\\/${tag}>`, 'i');
  const m = block.match(re);
  return m ? m[1].trim() : null;
}

function parseRSS(xml) {
  const items = [];
  const re = /<item[^>]*>([\s\S]*?)<\/item>/gi;
  let m;
  while ((m = re.exec(xml)) !== null) {
    const b = m[1];
    const title = extractTag(b, 'title');
    if (!title) continue;
    const link  = extractTag(b, 'link') || extractTag(b, 'guid') || '';
    const desc  = (extractTag(b, 'description') || '').replace(/<[^>]+>/g, '').replace(/&[a-z]+;/gi, ' ').trim().slice(0, 350);
    const pub   = extractTag(b, 'pubDate') || extractTag(b, 'published') || extractTag(b, 'dc:date') || '';
    const pubDate = pub ? new Date(pub) : null;
    items.push({
      title: title.replace(/<[^>]+>/g, '').replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>').trim(),
      link,
      desc,
      pubDate: (pubDate && !isNaN(pubDate)) ? pubDate.toISOString() : null,
    });
  }
  return items;
}

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Cache-Control', 'no-store');

  const { from, to, sources: srcParam } = req.query;
  const fromDate = from ? new Date(from + 'T00:00:00') : new Date(Date.now() - 7 * 86400000);
  const toDate   = to   ? new Date(to   + 'T23:59:59') : new Date();

  if (isNaN(fromDate) || isNaN(toDate)) {
    return res.status(400).json({ error: 'Fechas inválidas' });
  }

  const enabledIds  = srcParam ? srcParam.split(',') : SOURCES.map(s => s.id);
  const active      = SOURCES.filter(s => enabledIds.includes(s.id));
  const UA          = 'Mozilla/5.0 (compatible; ExpressLine-CRM/1.0)';

  const fetches = active.map(src =>
    fetch(src.url, {
      headers: { 'User-Agent': UA, 'Accept': 'application/rss+xml, application/xml, text/xml, */*' },
      signal: AbortSignal.timeout(10000),
    })
      .then(r => { if (!r.ok) throw new Error(`HTTP ${r.status}`); return r.text(); })
      .then(xml => {
        const all      = parseRSS(xml);
        const filtered = all.filter(i => {
          if (!i.pubDate) return true;
          const d = new Date(i.pubDate);
          return d >= fromDate && d <= toDate;
        });
        return { id: src.id, name: src.name, ok: true, count: filtered.length, items: filtered };
      })
      .catch(err => ({ id: src.id, name: src.name, ok: false, count: 0, items: [], error: err.message }))
  );

  const results = await Promise.all(fetches);
  const total   = results.reduce((s, r) => s + r.count, 0);

  res.json({
    from: fromDate.toISOString().split('T')[0],
    to:   toDate.toISOString().split('T')[0],
    total,
    sources: results,
  });
}
