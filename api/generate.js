export const config = { maxDuration: 60 };

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') return res.status(405).end();

  const key = process.env.GROQ_API_KEY;
  if (!key) return res.status(500).json({ error: 'GROQ_API_KEY no configurada en Vercel' });

  const { prompt } = req.body || {};
  if (!prompt) return res.status(400).json({ error: 'prompt requerido' });

  const r = await fetch('https://api.groq.com/openai/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${key}`,
    },
    body: JSON.stringify({
      model: 'llama-3.3-70b-versatile',
      messages: [{ role: 'user', content: prompt }],
      temperature: 0.2,
      max_tokens: 8192,
    }),
    signal: AbortSignal.timeout(55000),
  });

  if (!r.ok) {
    const err = await r.text();
    return res.status(r.status).json({ error: `Groq error ${r.status}: ${err}` });
  }

  const data  = await r.json();
  const text  = data?.choices?.[0]?.message?.content || '';
  const usage = data?.usage || {};

  res.setHeader('Cache-Control', 'no-store');
  res.json({ report: text, tokens: { input: usage.prompt_tokens, output: usage.completion_tokens } });
}
