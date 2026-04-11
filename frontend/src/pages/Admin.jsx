import React, { useEffect, useMemo, useState } from 'react'

export default function Admin() {
  const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null
  const role = typeof window !== 'undefined' ? localStorage.getItem('role') : null

  const [templates, setTemplates] = useState([])
  const [targets, setTargets] = useState([])
  const [campaigns, setCampaigns] = useState([])
  const [message, setMessage] = useState('')

  const [targetForm, setTargetForm] = useState({ name: '', email: '', department: '', role: '' })
  const [campaignForm, setCampaignForm] = useState({
    name: '',
    template_id: '',
    notes: '',
    state: 'draft',
    scheduled_at: '',
    target_ids: [],
    segment_department: '',
    segment_role: '',
  })

  const authHeaders = useMemo(() => ({ 'X-Admin-Token': token || '' }), [token])

  async function refreshAll() {
    const [tRes, trgRes, cRes] = await Promise.all([
      fetch('/api/templates', { headers: authHeaders }),
      fetch('/api/targets', { headers: authHeaders }),
      fetch('/api/campaigns', { headers: authHeaders }),
    ])
    setTemplates(await tRes.json())
    setTargets(await trgRes.json())
    setCampaigns(await cRes.json())
  }

  useEffect(() => {
    if (token && role === 'admin') {
      refreshAll().catch(() => setMessage('Failed to load admin data'))
    }
  }, [token, role])

  if (!token || role !== 'admin') {
    return (
      <div className="p-6">
        <h2 className="text-xl font-semibold">Admin</h2>
        <p className="mt-4">You must log in as admin.</p>
      </div>
    )
  }

  function toggleTarget(id) {
    setCampaignForm((prev) => {
      const exists = prev.target_ids.includes(id)
      return {
        ...prev,
        target_ids: exists ? prev.target_ids.filter((x) => x !== id) : [...prev.target_ids, id],
      }
    })
  }

  async function submitTarget(e) {
    e.preventDefault()
    setMessage('')
    const payload = { targets: [{ ...targetForm }] }
    const res = await fetch('/api/targets', {
      method: 'POST',
      headers: { ...authHeaders, 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      setMessage(err.error || 'Failed to add target')
      return
    }
    setTargetForm({ name: '', email: '', department: '', role: '' })
    setMessage('Target added')
    refreshAll()
  }

  async function submitCampaign(e) {
    e.preventDefault()
    setMessage('')

    const payload = {
      ...campaignForm,
      template_id: Number(campaignForm.template_id),
      target_ids: campaignForm.target_ids,
      scheduled_at: campaignForm.scheduled_at || null,
      segment_department: campaignForm.segment_department || null,
      segment_role: campaignForm.segment_role || null,
    }

    const hasExplicitTargets = payload.target_ids.length > 0
    const hasSegmentation = payload.segment_department || payload.segment_role
    if (!hasExplicitTargets && !hasSegmentation) {
      setMessage('Select targets or provide segment filters')
      return
    }

    const res = await fetch('/api/campaigns', {
      method: 'POST',
      headers: { ...authHeaders, 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })

    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      setMessage(err.error || 'Failed to create campaign')
      return
    }

    setCampaignForm({
      name: '',
      template_id: '',
      notes: '',
      state: 'draft',
      scheduled_at: '',
      target_ids: [],
      segment_department: '',
      segment_role: '',
    })
    setMessage('Campaign created')
    refreshAll()
  }

  async function transitionCampaign(campaignId, action, body = null) {
    const res = await fetch(`/api/campaigns/${campaignId}/${action}`, {
      method: 'POST',
      headers: { ...authHeaders, 'Content-Type': 'application/json' },
      body: body ? JSON.stringify(body) : null,
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      setMessage(err.error || `Failed to ${action} campaign`)
      return
    }
    refreshAll()
  }

  return (
    <div className="p-6 space-y-8">
      <div>
        <h2 className="text-2xl font-semibold">Campaign Management</h2>
        <p className="text-sm text-slate-600 mt-1">Draft, schedule, activate, complete, and archive phishing campaigns.</p>
        {message && <p className="mt-2 text-sm text-slate-700">{message}</p>}
      </div>

      <div className="bg-white rounded-xl shadow p-6">
        <h3 className="text-lg font-semibold">Add Target</h3>
        <form className="mt-4 grid grid-cols-1 md:grid-cols-4 gap-3" onSubmit={submitTarget}>
          <input className="p-3 border rounded-lg" placeholder="Name" value={targetForm.name} onChange={(e) => setTargetForm({ ...targetForm, name: e.target.value })} />
          <input className="p-3 border rounded-lg" placeholder="Email" value={targetForm.email} onChange={(e) => setTargetForm({ ...targetForm, email: e.target.value })} />
          <input className="p-3 border rounded-lg" placeholder="Department" value={targetForm.department} onChange={(e) => setTargetForm({ ...targetForm, department: e.target.value })} />
          <input className="p-3 border rounded-lg" placeholder="Role" value={targetForm.role} onChange={(e) => setTargetForm({ ...targetForm, role: e.target.value })} />
          <button className="md:col-span-4 px-4 py-2 bg-slate-900 text-white rounded-lg">Save Target</button>
        </form>
      </div>

      <div className="bg-white rounded-xl shadow p-6">
        <h3 className="text-lg font-semibold">Create Campaign</h3>
        <form className="mt-4 space-y-3" onSubmit={submitCampaign}>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <input className="p-3 border rounded-lg" placeholder="Campaign name" value={campaignForm.name} onChange={(e) => setCampaignForm({ ...campaignForm, name: e.target.value })} />
            <select className="p-3 border rounded-lg" value={campaignForm.template_id} onChange={(e) => setCampaignForm({ ...campaignForm, template_id: e.target.value })}>
              <option value="">Select template</option>
              {templates.map((t) => <option key={t.id} value={t.id}>{t.name}</option>)}
            </select>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <select className="p-3 border rounded-lg" value={campaignForm.state} onChange={(e) => setCampaignForm({ ...campaignForm, state: e.target.value })}>
              <option value="draft">draft</option>
              <option value="scheduled">scheduled</option>
              <option value="active">active</option>
            </select>
            <input type="datetime-local" className="p-3 border rounded-lg" value={campaignForm.scheduled_at} onChange={(e) => setCampaignForm({ ...campaignForm, scheduled_at: e.target.value })} />
            <input className="p-3 border rounded-lg" placeholder="Notes" value={campaignForm.notes} onChange={(e) => setCampaignForm({ ...campaignForm, notes: e.target.value })} />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <input className="p-3 border rounded-lg" placeholder="Segment Department (optional)" value={campaignForm.segment_department} onChange={(e) => setCampaignForm({ ...campaignForm, segment_department: e.target.value })} />
            <input className="p-3 border rounded-lg" placeholder="Segment Role (optional)" value={campaignForm.segment_role} onChange={(e) => setCampaignForm({ ...campaignForm, segment_role: e.target.value })} />
          </div>

          <div className="border rounded-lg p-3 max-h-44 overflow-auto">
            <div className="text-sm font-medium mb-2">Optional explicit targets</div>
            {targets.map((t) => (
              <label key={t.id} className="flex items-center gap-2 mb-1 text-sm">
                <input type="checkbox" checked={campaignForm.target_ids.includes(t.id)} onChange={() => toggleTarget(t.id)} />
                <span>{t.name} ({t.email}) - {t.department || 'n/a'} / {t.role || 'n/a'}</span>
              </label>
            ))}
          </div>

          <button className="px-4 py-2 bg-slate-900 text-white rounded-lg">Create Campaign</button>
        </form>
      </div>

      <div className="bg-white rounded-xl shadow p-6">
        <h3 className="text-lg font-semibold">Campaign Lifecycle Monitor</h3>
        <div className="mt-4 overflow-auto">
          <table className="w-full text-sm">
            <thead className="bg-slate-50">
              <tr>
                <th className="p-2 text-left">Name</th>
                <th className="p-2 text-left">State</th>
                <th className="p-2 text-left">Targets</th>
                <th className="p-2 text-left">Segment</th>
                <th className="p-2 text-left">Snapshot Subject</th>
                <th className="p-2 text-left">Actions</th>
              </tr>
            </thead>
            <tbody>
              {campaigns.map((c) => (
                <tr key={c.id} className="border-t align-top">
                  <td className="p-2">{c.name}</td>
                  <td className="p-2">{c.state}</td>
                  <td className="p-2">{c.total_targets || 0}</td>
                  <td className="p-2">{c.segment_department || '-'} / {c.segment_role || '-'}</td>
                  <td className="p-2 max-w-xs truncate" title={c.snapshot_subject || ''}>{c.snapshot_subject || '-'}</td>
                  <td className="p-2 space-x-2 whitespace-nowrap">
                    <button className="text-blue-700" onClick={() => transitionCampaign(c.id, 'activate')}>Activate</button>
                    <button className="text-emerald-700" onClick={() => transitionCampaign(c.id, 'complete')}>Complete</button>
                    <button className="text-amber-700" onClick={() => transitionCampaign(c.id, 'archive')}>Archive</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
