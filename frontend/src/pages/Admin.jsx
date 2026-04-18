import React, { useEffect, useMemo, useState } from 'react'

export default function Admin() {
  const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null
  const role = typeof window !== 'undefined' ? localStorage.getItem('role') : null

  const [templates, setTemplates] = useState([])
  const [targets, setTargets] = useState([])
  const [campaigns, setCampaigns] = useState([])
  const [message, setMessage] = useState('')
  const [messageType, setMessageType] = useState('info')

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
    try {
      const [tRes, trgRes, cRes] = await Promise.all([
        fetch('/api/templates', { headers: authHeaders }),
        fetch('/api/targets', { headers: authHeaders }),
        fetch('/api/campaigns', { headers: authHeaders }),
      ])

      if (!tRes.ok) throw new Error('Failed to load templates')
      if (!trgRes.ok) throw new Error('Failed to load targets')
      if (!cRes.ok) throw new Error('Failed to load campaigns')

      const templates = await tRes.json()
      const targets = await trgRes.json()
      const campaigns = await cRes.json()

      setTemplates(Array.isArray(templates) ? templates : [])
      setTargets(Array.isArray(targets) ? targets : [])
      setCampaigns(Array.isArray(campaigns) ? campaigns : [])
    } catch (err) {
      console.error('Admin data refresh error:', err)
      setMessage(`Error loading data: ${err.message}`)
      setMessageType('error')
    }
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
      setMessageType('error')
      return
    }
    setTargetForm({ name: '', email: '', department: '', role: '' })
    setMessage('Target added')
    setMessageType('success')
    refreshAll()
  }

  async function submitCampaign(e) {
    e.preventDefault()
    setMessage('')

    if (!campaignForm.template_id) {
      setMessage('Please select a template')
      setMessageType('error')
      return
    }

    const parsedTemplateId = Number(campaignForm.template_id)
    if (!Number.isInteger(parsedTemplateId) || parsedTemplateId <= 0) {
      setMessage('Invalid template selection')
      setMessageType('error')
      return
    }

    const payload = {
      ...campaignForm,
      template_id: parsedTemplateId,
      target_ids: campaignForm.target_ids,
      scheduled_at: campaignForm.scheduled_at || null,
      segment_department: campaignForm.segment_department || null,
      segment_role: campaignForm.segment_role || null,
    }

    const hasExplicitTargets = payload.target_ids.length > 0
    const hasSegmentation = payload.segment_department || payload.segment_role
    if (!hasExplicitTargets && !hasSegmentation) {
      setMessage('Select targets or provide segment filters')
      setMessageType('error')
      return
    }

    if (payload.state === 'scheduled' && !payload.scheduled_at) {
      setMessage('Scheduled campaigns require a date/time')
      setMessageType('error')
      return
    }

    console.log('Submitting campaign:', payload)
    const res = await fetch('/api/campaigns', {
      method: 'POST',
      headers: { ...authHeaders, 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })

    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      console.error('Campaign creation error:', err, 'Status:', res.status)
      setMessage(`Error (${res.status}): ${err.error || 'Failed to create campaign'}`)
      setMessageType('error')
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
    setMessageType('success')
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
      setMessage(`Error (${res.status}): ${err.error || `Failed to ${action} campaign`}`)
      setMessageType('error')
      return
    }
    setMessage(`Campaign ${action} successful`)
    setMessageType('success')
    refreshAll()
  }

  function getStateBadgeColor(state) {
    const colors = {
      draft: 'bg-yellow-100 text-yellow-800 border border-yellow-200',
      scheduled: 'bg-purple-100 text-purple-800',
      active: 'bg-green-100 text-green-800 border border-green-200',
      completed: 'bg-blue-100 text-blue-800 border border-blue-200',
      archived: 'bg-slate-100 text-slate-800 border border-slate-200',
    }
    return colors[state] || colors.draft
  }

  function formatStateLabel(state) {
    if (!state) return 'Draft'
    return state.charAt(0).toUpperCase() + state.slice(1)
  }

  function getSegmentDisplay(campaign) {
    if (campaign.segment_department || campaign.segment_role) {
      const dept = campaign.segment_department || '(any)'
      const role = campaign.segment_role || '(any)'
      return `${dept} / ${role}`
    }
    return campaign.total_targets > 0 ? 'No segmentation' : 'All users'
  }

  function renderCampaignActions(campaign) {
    if (campaign.state === 'active') {
      return (
        <>
          <button
            type="button"
            className="px-2 py-1 rounded text-xs font-medium text-emerald-700 hover:bg-emerald-50"
            onClick={() => transitionCampaign(campaign.id, 'complete')}
          >
            Complete
          </button>
          <button
            type="button"
            className="px-2 py-1 rounded text-xs font-medium text-amber-700 hover:bg-amber-50"
            onClick={() => transitionCampaign(campaign.id, 'archive')}
          >
            Archive
          </button>
          <a
            href={`/campaign-results/${campaign.id}`}
            className="px-2 py-1 rounded text-xs font-medium text-slate-700 hover:bg-slate-100 inline-block"
          >
            View Results
          </a>
        </>
      )
    }

    if (campaign.state === 'completed') {
      return (
        <>
          <button
            type="button"
            className="px-2 py-1 rounded text-xs font-medium text-amber-700 hover:bg-amber-50"
            onClick={() => transitionCampaign(campaign.id, 'archive')}
          >
            Archive
          </button>
          <a
            href={`/campaign-results/${campaign.id}`}
            className="px-2 py-1 rounded text-xs font-medium text-slate-700 hover:bg-slate-100 inline-block"
          >
            View Results
          </a>
        </>
      )
    }

    if (campaign.state === 'draft' || campaign.state === 'scheduled') {
      return (
        <button
          type="button"
          className="px-2 py-1 rounded text-xs font-medium text-blue-700 hover:bg-blue-50"
          onClick={() => transitionCampaign(campaign.id, 'activate')}
        >
          Activate
        </button>
      )
    }

    return <span className="text-xs text-slate-500">No actions</span>
  }

  return (
    <div className="p-6 space-y-8">
      <div>
        <h2 className="text-2xl font-semibold">Campaign Management</h2>
        <p className="text-sm text-slate-600 mt-1">Draft, schedule, activate, complete, and archive phishing campaigns.</p>
        {message && (
          <p className={"mt-2 text-sm " + (messageType === 'error' ? 'text-red-700' : messageType === 'success' ? 'text-emerald-700' : 'text-slate-700')}>
            {message}
          </p>
        )}
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
        <p className="text-sm text-slate-600 mt-2 mb-4">This section allows administrators to monitor and manage phishing campaigns throughout their lifecycle.</p>
        <div className="overflow-auto">
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
              {campaigns.length === 0 && (
                <tr>
                  <td className="p-3 text-slate-500" colSpan={6}>No campaigns yet. Create one above.</td>
                </tr>
              )}
              {campaigns.map((c) => (
                <tr key={c.id} className="border-t align-top">
                  <td className="p-2 font-medium">{c.name}</td>
                  <td className="p-2">
                    <span className={"px-2 py-1 rounded-full text-xs font-semibold uppercase tracking-wide " + getStateBadgeColor(c.state)}>
                      {formatStateLabel(c.state)}
                    </span>
                  </td>
                  <td className="p-2">{c.total_targets || 0}</td>
                  <td className="p-2 text-slate-600">{getSegmentDisplay(c)}</td>
                  <td className="p-2 max-w-xs truncate text-slate-600" title={c.snapshot_subject || ''}>{c.snapshot_subject || '(no subject)'}</td>
                  <td className="p-2 space-x-2 whitespace-nowrap">
                    {renderCampaignActions(c)}
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
