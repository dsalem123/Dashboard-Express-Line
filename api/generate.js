export const config = { maxDuration: 60 };

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') return res.status(405).end();

  const { prompt } = req.body || {};
  if (!prompt) return res.status(400).json({ error: 'prompt requerido' });

  const r = await fetch('https://text.pollinations.ai/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      messages: [{ role: 'user', content: prompt }],
      model: 'openai',
      seed: 42,
      private: true,
    }),
    signal: AbortSignal.timeout(55000),
  });

  if (!r.ok) {
    const err = await r.text();
    return res.status(r.status).json({ error: `Error ${r.status}: ${err}` });
  }

  const text = await r.text();
  res.setHeader('Cache-Control', 'no-store');
  res.json({ report: text });
}
