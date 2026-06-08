export const config = { maxDuration: 60 };

const TICKERS = [
  { sym: '^GSPC',   label: 'S&P 500' },
  { sym: '^IXIC',   label: 'Nasdaq Composite' },
  { sym: '^RUT',    label: 'Russell 2000' },
  { sym: '^GDAXI',  label: 'DAX' },
  { sym: '^FCHI',   label: 'CAC 40' },
  { sym: '^N225',   label: 'Nikkei 225' },
  { sym: '^HSI',    label: 'Hang Seng' },
  { sym: 'GC=F',    label: 'Oro (USD/oz)' },
  { sym: 'SI=F',    label: 'Plata (USD/oz)' },
  { sym: 'CL=F',    label: 'WTI (USD/bbl)' },
  { sym: 'BZ=F',    label: 'Brent (USD/bbl)' },
  { sym: 'NG=F',    label: 'Gas Natural (USD/MMBtu)' },
  { sym: 'HG=F',    label: 'Cobre (USD/lb)' },
  { sym: 'BTC-USD', label: 'Bitcoin (USD)' },
  { sym: 'ETH-USD', label: 'Ethereum (USD)' },
];

async function fetchMarketData() {
  const UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36';
  const results = await Promise.allSettled(
    TICKERS.map(t =>
      fetch(
        `https://query2.finance.yahoo.com/v8/finance/chart/${encodeURIComponent(t.sym)}?interval=1d&range=7d`,
        { headers: { 'User-Agent': UA, 'Accept': 'application/json' }, signal: AbortSignal.timeout(6000) }
      ).then(r => r.json()).then(d => ({ t, d }))
    )
  );

  const lines = ['## DATOS DE MERCADO (tiempo real al momento de generación)', ''];
  results.forEach(r => {
    if (r.status !== 'fulfilled') return;
    const { t, d } = r.value;
    const result = d?.chart?.result?.[0];
    const meta   = result?.meta;
    if (!meta || meta.regularMarketPrice == null) return;

    const price = meta.regularMarketPrice;
    const closes = (result?.indicators?.quote?.[0]?.close || []).filter(c => c != null);
    const prevClose = meta.previousClose ?? (closes.length >= 2 ? closes[closes.length - 2] : price);
    const weekOpen  = closes.length >= 5 ? closes[closes.length - 5] : (closes[0] ?? price);

    const dailyPct  = prevClose ? ((price - prevClose) / prevClose * 100).toFixed(2) : '?';
    const weeklyPct = weekOpen  ? ((price - weekOpen)  / weekOpen  * 100).toFixed(2) : '?';

    const fmt = (n) => n >= 1000 ? n.toLocaleString('en-US', { maximumFractionDigits: 2 }) : n.toFixed(2);
    lines.push(`- **${t.label}**: ${fmt(price)} | Diaria: ${dailyPct > 0 ? '+' : ''}${dailyPct}% | Semanal: ${weeklyPct > 0 ? '+' : ''}${weeklyPct}%`);
  });

  lines.push('');
  lines.push('> INSTRUCCIÓN CRÍTICA: Estos son los únicos precios y variaciones reales. Usá EXCLUSIVAMENTE estos valores en el reporte. NO uses otros números para precios o variaciones de mercado.');
  lines.push('');
  return lines.join('\n');
}

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') return res.status(405).end();

  const { prompt: rawPrompt } = req.body || {};
  if (!rawPrompt) return res.status(400).json({ error: 'prompt requerido' });

  const key = process.env.GROQ_API_KEY;
  if (!key) return res.status(500).json({ error: 'GROQ_API_KEY no configurada en Vercel' });

  // Separar prompt del sistema y bloque de noticias
  const splitIdx = rawPrompt.indexOf('---\n## NOTICIAS RECOPILADAS');
  const sysPrompt = splitIdx > -1 ? rawPrompt.slice(0, splitIdx) : rawPrompt;
  let   newsBlock = splitIdx > -1 ? rawPrompt.slice(splitIdx)    : '';

  // Limitar noticias: max 3 por fuente, título + descripción 90 chars
  if (newsBlock) {
    newsBlock = newsBlock
      .split(/(?=### [A-Z])/g)
      .map(section => {
        const lines   = section.split('\n');
        const items   = lines.filter(l => l.startsWith('- ['));
        const rest    = lines.filter(l => !l.startsWith('- ['));
        const trimmed = items.slice(0, 3).map(l => {
          const m = l.match(/^- \[.*?\] \*\*(.*?)\*\*(?:: (.+))?$/);
          if (m) {
            const desc = m[2] ? ': ' + m[2].slice(0, 90) : '';
            return `- ${m[1]}${desc}`;
          }
          return l.slice(0, 150);
        });
        return [...rest, ...trimmed].join('\n');
      })
      .join('');
  }

  // Fetch market data en paralelo mientras preparamos el prompt
  const marketBlock = await fetchMarketData().catch(() => '');

  const antiHallucination = `REGLAS ABSOLUTAS — VIOLACIÓN = REPORTE INVÁLIDO:
1. PROHIBIDO inventar, estimar o extrapolar precios, porcentajes, fechas o nombres que no estén explícitamente en los bloques DATOS DE MERCADO o NOTICIAS RECOPILADAS.
2. Si un dato no está disponible en los bloques provistos, escribí exactamente: [VERIFICAR].
3. PROHIBIDO mezclar datos de diferentes períodos o fuentes no proporcionadas.
4. PROHIBIDO usar los valores de los ejemplos del prompt (XXXX, X,X%) — son placeholders.
5. Cada párrafo debe referenciar datos REALES de los bloques provistos.
6. No repitas la misma estructura de oración en párrafos consecutivos.

FORMATO DE SALIDA — OBLIGATORIO:
- La primera línea del documento debe ser el título: "BRIEFING SEMANAL OFFSHORE" seguido de una línea en blanco y la fecha en formato "08 de junio de 2026".
- PROHIBIDO usar # ## ### para títulos. Los títulos de sección van en MAYÚSCULAS, solos en su línea, seguidos de una línea en blanco.
- Los subtítulos (ej: Estados Unidos, Europa) van en Mayúscula Inicial, solos en su línea, con dos guiones antes: "— Estados Unidos".
- PROHIBIDO usar * para listas. El Resumen Ejecutivo usa numeración simple: "1.", "2.", etc. El resto del documento son párrafos corridos.
- Reservá el uso de negrita (**texto**) ÚNICAMENTE para nombres de activos financieros o índices la primera vez que aparecen en cada sección. Máximo 2 negritas por párrafo.
- Separá cada sección principal con una línea de guiones: "────────────────────────────────"
- Párrafos de mínimo 4 oraciones, fluidos, sin viñetas ni sub-listas dentro del cuerpo.
- Tono: documento institucional de banca privada. Sin exclamaciones ni lenguaje coloquial.\n\n`;

  const prompt = (antiHallucination + sysPrompt + '\n\n' + marketBlock + newsBlock).slice(0, 30000);

  const r = await fetch('https://api.groq.com/openai/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${key}`,
    },
    body: JSON.stringify({
      model: 'llama-3.3-70b-versatile',
      messages: [{ role: 'user', content: prompt }],
      temperature: 0.15,
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
