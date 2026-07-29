import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'
// @ts-ignore
import webpush from 'npm:web-push'

const VAPID_PUBLIC  = Deno.env.get('VAPID_PUBLIC_KEY') ?? ''
const VAPID_PRIVATE = Deno.env.get('VAPID_PRIVATE_KEY') ?? ''
const VAPID_SUB     = Deno.env.get('VAPID_CLAIMS_SUB') ?? 'mailto:admin@jarvis'

webpush.setVapidDetails(VAPID_SUB, VAPID_PUBLIC, VAPID_PRIVATE)

Deno.serve(async (req: Request) => {
  if (req.method === 'OPTIONS') {
    return new Response(null, { headers: { 'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Headers': 'authorization, content-type' } })
  }

  let payload: Record<string, unknown> = {}
  try { payload = await req.json() } catch { return new Response('bad request', { status: 400 }) }

  // Determine title/body — supports both direct calls and DB webhook format
  let title = (payload.title as string) ?? ''
  let body  = (payload.body  as string) ?? ''

  if (!title && payload.record) {
    const rec    = payload.record as Record<string, string>
    const action = rec.action ?? ''
    const status = rec.status ?? ''
    if (action.startsWith('PROMETHEUS:')) {
      title = `PROMETHEUS — ${action.slice(11, 55).trim()}`
      body  = action.slice(0, 80)
    } else if (status === 'failed') {
      title = 'JARVIS ALERT'
      body  = action.slice(0, 80)
    } else {
      return new Response(JSON.stringify({ skip: true }), { headers: { 'Content-Type': 'application/json' } })
    }
  }

  if (!title) return new Response(JSON.stringify({ skip: true }), { headers: { 'Content-Type': 'application/json' } })

  const sb = createClient(
    Deno.env.get('SUPABASE_URL') ?? '',
    Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? ''
  )

  const { data: subs } = await sb.from('push_subscriptions').select('id, endpoint, subscription_info')
  if (!subs?.length) return new Response(JSON.stringify({ sent: 0 }), { headers: { 'Content-Type': 'application/json' } })

  const notifPayload = JSON.stringify({ title, body, url: '/' })

  const results = await Promise.allSettled(
    subs.map(async (row) => {
      try {
        await webpush.sendNotification(row.subscription_info, notifPayload)
      } catch (err: unknown) {
        const status = (err as { statusCode?: number }).statusCode
        if (status === 410) {
          await sb.from('push_subscriptions').delete().eq('endpoint', row.endpoint)
        }
        throw err
      }
    })
  )

  const sent = results.filter(r => r.status === 'fulfilled').length
  return new Response(JSON.stringify({ sent, total: subs.length }), { headers: { 'Content-Type': 'application/json' } })
})
