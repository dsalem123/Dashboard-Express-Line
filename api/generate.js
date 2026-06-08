export const config = { maxDuration: 60 };

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') return res.status(405).end();

  const key = process.env.GEMINI_API_KEY;
  if (!key) return res.status(500).json({ error: 'GEMINI_API_KEY no configurada en Vercel' });

  const { prompt } = req.body || {};
  if (!prompt) return res.status(400).json({ error: 'prompt requerido' });

  const r = await fetch(
    `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${key}`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        contents: [{ parts: [{ text: prompt }] }],
        generationConfig: {
          temperature: 0.2,
          maxOutputTokens: 8192,
          topP: 0.85,
        },
      }),
      signal: AbortSignal.timeout(55000),
    }
  );

  if (!r.ok) {
    const err = await r.text();
    return res.status(r.status).json({ error: `Gemini error ${r.status}: ${err}` });
  }

  const data  = await r.json();
  const text  = data?.candidates?.[0]?.content?.parts?.[0]?.text || '';
  const block = data?.usageMetadata || {};

  res.setHeader('Cache-Control', 'no-store');
  res.json({ report: text, tokens: { input: block.promptTokenCount, output: block.candidatesTokenCount } });
}
