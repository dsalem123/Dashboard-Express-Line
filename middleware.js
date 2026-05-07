export const config = { matcher: ['/((?!_next|api/).*)'] }

export default function middleware(request) {
  const auth = request.headers.get('authorization')
  const user = process.env.CRM_USER || 'admin'
  const pass = process.env.CRM_PASS || 'changeme'

  if (auth) {
    const [type, credentials] = auth.split(' ')
    if (type === 'Basic') {
      const decoded  = atob(credentials)
      const colonIdx = decoded.indexOf(':')
      const u = decoded.substring(0, colonIdx)
      const p = decoded.substring(colonIdx + 1)
      if (u === user && p === pass) return
    }
  }

  return new Response('Acceso restringido — CRM ExpressLine', {
    status: 401,
    headers: { 'WWW-Authenticate': 'Basic realm="CRM ExpressLine"' },
  })
}
