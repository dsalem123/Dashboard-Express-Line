export const config = { api: { bodyParser: { sizeLimit: '10mb' } } };

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') return res.status(405).end();

  const token = process.env.GITHUB_TOKEN;
  if (!token) return res.status(500).json({ error: 'GITHUB_TOKEN no configurado' });

  try {
    const state  = req.body;
    const hgRaw  = state._hgData || null;
    delete state._hgData;
    const stateJson = JSON.stringify(state);

    const apiBase = 'https://api.github.com/repos/dsalem123/Dashboard-Express-Line/contents';
    const headers = {
      'Authorization': `Bearer ${token}`,
      'Accept': 'application/vnd.github+json',
      'X-GitHub-Api-Version': '2022-11-28',
    };

    const getRes = await fetch(`${apiBase}/index.html`, { headers });
    if (!getRes.ok) throw new Error('Error leyendo index.html: ' + getRes.status);
    const { content: b64, sha } = await getRes.json();
    let html = Buffer.from(b64, 'base64').toString('utf-8');

    html = html.replace(
      /<script type="application\/json" id="crm-snapshot">[\s\S]*?<\/script>/,
      `<script type="application/json" id="crm-snapshot">${stateJson}</script>`
    );
    if (hgRaw) {
      html = html.replace(
        /const HG_STATIC_DATA = (?:null|\{[\s\S]*?\});/,
        `const HG_STATIC_DATA = ${JSON.stringify(hgRaw)};`
      );
    }

    const now = new Date().toISOString().slice(0, 16).replace('T', ' ');
    const putRes = await fetch(`${apiBase}/index.html`, {
      method: 'PUT',
      headers: { ...headers, 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: `CRM snapshot ${now}`,
        content: Buffer.from(html).toString('base64'),
        sha,
      }),
    });
    if (!putRes.ok) throw new Error('Error actualizando: ' + putRes.status + ' ' + await putRes.text());

    return res.status(200).json({ ok: true });
  } catch (e) {
    return res.status(500).json({ error: e.message });
  }
}
