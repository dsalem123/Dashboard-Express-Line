export const config = { api: { bodyParser: { sizeLimit: '10mb' } } };

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') return res.status(405).end();

  // Verificar sesión Supabase
  const authHeader = req.headers['authorization'] || '';
  const userToken = authHeader.startsWith('Bearer ') ? authHeader.slice(7) : '';
  if (!userToken) return res.status(401).json({ error: 'No autenticado' });
  const sbVerify = await fetch('https://mgbjvbwqspeumpwprbbt.supabase.co/auth/v1/user', {
    headers: {
      'Authorization': `Bearer ${userToken}`,
      'apikey': process.env.SUPABASE_ANON_KEY || 'sb_publishable_q4-FOP1jGSrEiu06LMfnDA_Q6q8sxh8',
    }
  });
  if (!sbVerify.ok) return res.status(401).json({ error: 'Sesión inválida o expirada' });

  const token = process.env.GITHUB_TOKEN;
  if (!token) return res.status(500).json({ error: 'GITHUB_TOKEN no configurado' });

  try {
    const state  = req.body;
    const hgRaw  = state._hgData || null;
    delete state._hgData;

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

    // ── Merge clients/leads: never lose records ──────────────────────────────
    try {
      const snapMatch = html.match(/<script type="application\/json" id="crm-snapshot">([\s\S]*?)<\/script>/);
      if (snapMatch) {
        const existing = JSON.parse(snapMatch[1]);
        const deletedIds = new Set(JSON.parse(state._deletedClientIds || '[]'));

        // Merge crm_clients: incoming takes precedence; restore existing records not in incoming
        const incomingClients = JSON.parse(state.crm_clients || '[]');
        const existingClients = JSON.parse(existing.crm_clients || '[]');
        const merged = {};
        incomingClients.forEach(c => { merged[c.id] = c; });
        existingClients.forEach(c => {
          if (!merged[c.id] && !deletedIds.has(c.id)) merged[c.id] = c;
        });
        state.crm_clients = JSON.stringify(
          Object.values(merged).sort((a, b) => a.id - b.id)
        );

        // Merge crm_leads similarly
        const deletedLeadIds = new Set(JSON.parse(state._deletedLeadIds || '[]'));
        const incomingLeads = JSON.parse(state.crm_leads || '[]');
        const existingLeads = JSON.parse(existing.crm_leads || '[]');
        const mergedLeads = {};
        incomingLeads.forEach(l => { mergedLeads[l.id] = l; });
        existingLeads.forEach(l => {
          if (!mergedLeads[l.id] && !deletedLeadIds.has(l.id)) mergedLeads[l.id] = l;
        });
        state.crm_leads = JSON.stringify(
          Object.values(mergedLeads).sort((a, b) => a.id - b.id)
        );
      }
    } catch (mergeErr) {
      // merge failed — use incoming as-is
    }

    delete state._deletedClientIds;
    delete state._deletedLeadIds;
    const stateJson = JSON.stringify(state);

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

    return res.status(200).json({ ok: true, crm_clients: state.crm_clients, crm_leads: state.crm_leads });
  } catch (e) {
    return res.status(500).json({ error: e.message });
  }
}
