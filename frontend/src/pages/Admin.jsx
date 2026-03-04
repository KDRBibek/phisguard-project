import React, {useState, useEffect} from 'react'
import ConfirmModal from '../components/ConfirmModal'

export default function Admin(){
  const [form, setForm] = useState({sender:'', subject:'', body:'', is_phishing:false, difficulty:'medium', link_text:'Open link', link_url:'#', feedback:''})
  const [metrics, setMetrics] = useState([])
  const [message, setMessage] = useState('')
  const [templateForm, setTemplateForm] = useState({name:'', sender:'', subject:'', body:'', is_phishing:false, difficulty:'medium', link_text:'Open link', link_url:'#', feedback:''})
  const [templates, setTemplates] = useState([])
  const [targetForm, setTargetForm] = useState({name:'', email:'', department:'', bulk:''})
  const [targets, setTargets] = useState([])
  const [campaignForm, setCampaignForm] = useState({name:'', template_id:'', target_ids:[], notes:'', status:'active'})
  const [campaigns, setCampaigns] = useState([])
  const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null
  const role = typeof window !== 'undefined' ? localStorage.getItem('role') : null

  if(!token || token==='' || role !== 'admin'){
    return (
      <div className="p-6">
        <h2 className="text-xl font-semibold">Admin</h2>
        <p className="mt-4">You must <a className="text-slate-900" href="/login">log in as admin</a> to access admin features.</p>
      </div>
    )
  }

  useEffect(()=>{ fetch('/api/metrics', {headers:{'X-Admin-Token': token}}).then(r=>r.json()).then(setMetrics).catch(()=>setMetrics([])) }, [token])
  const [actions, setActions] = useState([])
  const [userReports, setUserReports] = useState([])
  const [smsMetrics, setSmsMetrics] = useState([])
  const [smsActions, setSmsActions] = useState([])
  const [smsUserReports, setSmsUserReports] = useState([])
  const [emailsAdmin, setEmailsAdmin] = useState([])
  const [confirm, setConfirm] = useState({open:false, title:'', message:'', onConfirm: null})

  useEffect(()=>{ fetch('/api/actions', {headers:{'X-Admin-Token': token}}).then(r=>r.json()).then(setActions).catch(()=>setActions([])) }, [token])
  useEffect(()=>{ fetch('/api/user_reports', {headers:{'X-Admin-Token': token}}).then(r=>r.json()).then(setUserReports).catch(()=>setUserReports([])) }, [token])
  useEffect(()=>{ fetch('/api/sms/metrics', {headers:{'X-Admin-Token': token}}).then(r=>r.json()).then(setSmsMetrics).catch(()=>setSmsMetrics([])) }, [token])
  useEffect(()=>{ fetch('/api/sms/actions', {headers:{'X-Admin-Token': token}}).then(r=>r.json()).then(setSmsActions).catch(()=>setSmsActions([])) }, [token])
  useEffect(()=>{ fetch('/api/sms/user_reports', {headers:{'X-Admin-Token': token}}).then(r=>r.json()).then(setSmsUserReports).catch(()=>setSmsUserReports([])) }, [token])
  useEffect(()=>{ fetch('/api/emails', {headers:{'X-Admin-Token': token}}).then(r=>r.json()).then(setEmailsAdmin).catch(()=>setEmailsAdmin([])) }, [token])
  useEffect(()=>{ fetch('/api/templates', {headers:{'X-Admin-Token': token}}).then(r=>r.json()).then(setTemplates).catch(()=>setTemplates([])) }, [token])
  useEffect(()=>{ fetch('/api/targets', {headers:{'X-Admin-Token': token}}).then(r=>r.json()).then(setTargets).catch(()=>setTargets([])) }, [token])
  useEffect(()=>{ fetch('/api/campaigns', {headers:{'X-Admin-Token': token}}).then(r=>r.json()).then(setCampaigns).catch(()=>setCampaigns([])) }, [token])

  async function submit(e){
    e.preventDefault()
    setMessage('')
    try{
      const r = await fetch('/api/emails', { method:'POST', headers:{'Content-Type':'application/json','X-Admin-Token': token}, body: JSON.stringify(form) })
      if(r.status===201){ setMessage('Created'); setForm({sender:'', subject:'', body:'', is_phishing:false, difficulty:'medium', link_text:'Open link', link_url:'#', feedback:''}) }
      else { const j = await r.json(); setMessage(j.error || 'Error') }
    }catch(err){ setMessage('Network error') }
    // refresh metrics
    fetch('/api/metrics', {headers:{'X-Admin-Token': token}}).then(r=>r.json()).then(setMetrics).catch(()=>{})
    fetch('/api/actions', {headers:{'X-Admin-Token': token}}).then(r=>r.json()).then(setActions).catch(()=>{})
    fetch('/api/user_reports', {headers:{'X-Admin-Token': token}}).then(r=>r.json()).then(setUserReports).catch(()=>{})
    fetch('/api/emails', {headers:{'X-Admin-Token': token}}).then(r=>r.json()).then(setEmailsAdmin).catch(()=>{})
  }

  async function submitTemplate(e){
    e.preventDefault()
    try{
      const r = await fetch('/api/templates', { method:'POST', headers:{'Content-Type':'application/json','X-Admin-Token': token}, body: JSON.stringify(templateForm) })
      if(r.status===201){ setTemplateForm({name:'', sender:'', subject:'', body:'', is_phishing:false, difficulty:'medium', link_text:'Open link', link_url:'#', feedback:''}) }
      const list = await fetch('/api/templates', {headers:{'X-Admin-Token': token}}).then(r=>r.json())
      setTemplates(list)
    }catch(err){ /* ignore */ }
  }

  async function submitTargets(e){
    e.preventDefault()
    const list = []
    if(targetForm.name && targetForm.email){
      list.push({name: targetForm.name, email: targetForm.email, department: targetForm.department})
    }
    if(targetForm.bulk){
      targetForm.bulk.split('\n').map(l=>l.trim()).filter(Boolean).forEach(line=>{
        const parts = line.split(',').map(p=>p.trim())
        if(parts[0] && parts[1]){
          list.push({name: parts[0], email: parts[1], department: parts[2] || ''})
        }
      })
    }
    if(!list.length) return
    try{
      await fetch('/api/targets', { method:'POST', headers:{'Content-Type':'application/json','X-Admin-Token': token}, body: JSON.stringify({targets: list}) })
      setTargetForm({name:'', email:'', department:'', bulk:''})
      const refreshed = await fetch('/api/targets', {headers:{'X-Admin-Token': token}}).then(r=>r.json())
      setTargets(refreshed)
    }catch(err){ /* ignore */ }
  }

  async function submitCampaign(e){
    e.preventDefault()
    if(!campaignForm.name || !campaignForm.template_id || !campaignForm.target_ids.length) return
    try{
      await fetch('/api/campaigns', { method:'POST', headers:{'Content-Type':'application/json','X-Admin-Token': token}, body: JSON.stringify(campaignForm) })
      setCampaignForm({name:'', template_id:'', target_ids:[], notes:'', status:'active'})
      const refreshed = await fetch('/api/campaigns', {headers:{'X-Admin-Token': token}}).then(r=>r.json())
      setCampaigns(refreshed)
      const emailList = await fetch('/api/emails', {headers:{'X-Admin-Token': token}}).then(r=>r.json())
      setEmailsAdmin(emailList)
    }catch(err){ /* ignore */ }
  }

  function toggleTarget(id){
    setCampaignForm(f=>{
      const exists = f.target_ids.includes(id)
      return {...f, target_ids: exists ? f.target_ids.filter(x=>x!==id) : [...f.target_ids, id]}
    })
  }

  const timeline = [...actions]
    .sort((a,b)=> new Date(b.created_at) - new Date(a.created_at))
    .slice(0, 12)

  const actionCounts = actions.reduce((acc,a)=>{
    acc[a.action] = (acc[a.action]||0)+1
    return acc
  }, {})

  const reportStats = {
    total: userReports.reduce((sum,u)=>sum + (u.checked||0), 0),
    correct: userReports.reduce((sum,u)=>sum + (u.correct||0), 0)
  }
  const accuracy = reportStats.total ? (reportStats.correct/reportStats.total*100) : 0

  const barData = [
    {label:'Opened', value: actionCounts.opened || 0, color: '#1f2937'},
    {label:'Clicked', value: actionCounts.clicked || 0, color: '#ef4444'},
    {label:'Reported', value: actionCounts.reported || 0, color: '#10b981'},
  ]
  const maxValue = Math.max(1, ...barData.map(b=>b.value))

  return (
    <div className="p-6">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-xl shadow p-5">
          <div className="text-sm text-slate-500">Total Actions</div>
          <div className="text-3xl font-semibold mt-1">{actions.length}</div>
          <div className="mt-2 text-xs text-slate-400">Opened, clicked, and reported events.</div>
        </div>
        <div className="bg-white rounded-xl shadow p-5">
          <div className="text-sm text-slate-500">User Accuracy</div>
          <div className="text-3xl font-semibold mt-1">{accuracy.toFixed(1)}%</div>
          <div className="mt-2 text-xs text-slate-400">Correct vs checked across users.</div>
        </div>
        <div className="bg-white rounded-xl shadow p-5">
          <div className="text-sm text-slate-500">Active Campaigns</div>
          <div className="text-3xl font-semibold mt-1">{campaigns.filter(c=>c.status==='active').length}</div>
          <div className="mt-2 text-xs text-slate-400">Campaigns currently running.</div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <div className="bg-white rounded-xl shadow p-6">
          <h3 className="text-lg font-semibold">Action Breakdown</h3>
          <div className="mt-4 space-y-3">
            {barData.map(b=> (
              <div key={b.label}>
                <div className="flex items-center justify-between text-sm">
                  <span>{b.label}</span>
                  <span className="text-slate-500">{b.value}</span>
                </div>
                <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                  <div className="h-2 rounded-full" style={{width: `${(b.value/maxValue)*100}%`, backgroundColor: b.color}} />
                </div>
              </div>
            ))}
          </div>
          <div className="mt-4 text-xs text-slate-500">Shows how users interact with simulated emails.</div>
        </div>

        <div className="bg-white rounded-xl shadow p-6">
          <h3 className="text-lg font-semibold">Timeline</h3>
          <div className="mt-4 space-y-4">
            {timeline.length ? timeline.map(item=> (
              <div key={item.id} className="flex gap-3">
                <div className="mt-1 w-2 h-2 rounded-full" style={{backgroundColor: item.action==='clicked' ? '#ef4444' : item.action==='reported' ? '#10b981' : '#1f2937'}} />
                <div>
                  <div className="text-sm font-medium">{item.user_id || 'unknown'} {item.action} email {item.email_id}</div>
                  <div className="text-xs text-slate-500">{new Date(item.created_at).toLocaleString()}</div>
                </div>
              </div>
            )) : (
              <div className="text-sm text-slate-500">No recent activity.</div>
            )}
          </div>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow p-6 max-w-4xl">
        <h2 className="text-xl font-semibold">Templates</h2>
        <form onSubmit={submitTemplate} className="mt-4 space-y-3">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <input className="w-full p-3 border rounded-lg" placeholder="Template name" value={templateForm.name} onChange={e=>setTemplateForm({...templateForm,name:e.target.value})} />
            <input className="w-full p-3 border rounded-lg" placeholder="Sender" value={templateForm.sender} onChange={e=>setTemplateForm({...templateForm,sender:e.target.value})} />
          </div>
          <input className="w-full p-3 border rounded-lg" placeholder="Subject (supports {{name}}, {{email}}, {{department}})" value={templateForm.subject} onChange={e=>setTemplateForm({...templateForm,subject:e.target.value})} />
          <textarea className="w-full p-3 border rounded-lg" placeholder="Body (supports {{name}}, {{email}}, {{department}})" value={templateForm.body} onChange={e=>setTemplateForm({...templateForm,body:e.target.value})} />
          <div className="flex gap-4 items-center">
            <label className="flex items-center gap-2 text-sm"><input type="checkbox" checked={templateForm.is_phishing} onChange={e=>setTemplateForm({...templateForm,is_phishing:e.target.checked})} /> <span>Is phishing</span></label>
            <select className="p-2 border rounded-lg text-sm" value={templateForm.difficulty} onChange={e=>setTemplateForm({...templateForm,difficulty:e.target.value})}>
              <option value="easy">Easy</option>
              <option value="medium">Medium</option>
              <option value="hard">Hard</option>
            </select>
            <input className="flex-1 p-2 border rounded-lg" placeholder="Link text" value={templateForm.link_text} onChange={e=>setTemplateForm({...templateForm,link_text:e.target.value})} />
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <input className="w-full p-3 border rounded-lg" placeholder="Link URL" value={templateForm.link_url} onChange={e=>setTemplateForm({...templateForm,link_url:e.target.value})} />
            <input className="w-full p-3 border rounded-lg" placeholder="Feedback" value={templateForm.feedback} onChange={e=>setTemplateForm({...templateForm,feedback:e.target.value})} />
          </div>
          <div>
            <button className="px-4 py-2 bg-slate-900 text-white rounded-lg shadow">Create template</button>
          </div>
        </form>
        <div className="mt-6 overflow-auto">
          <table className="w-full text-sm">
            <thead className="bg-slate-50"><tr><th className="p-3 text-left">ID</th><th className="p-3 text-left">Name</th><th className="p-3 text-left">Sender</th><th className="p-3 text-left">Subject</th><th className="p-3 text-left">Action</th></tr></thead>
            <tbody>
              {templates.map(t=> (
                <tr key={t.id} className="border-t"><td className="p-3">{t.id}</td><td className="p-3">{t.name}</td><td className="p-3">{t.sender}</td><td className="p-3">{t.subject}</td><td className="p-3"><button onClick={()=>{ setConfirm({open:true, title:'Delete template', message:`Delete template ${t.name}?`, onConfirm: async ()=>{ await fetch(`/api/templates/${t.id}`, {method:'DELETE', headers:{'X-Admin-Token': token}}); setTemplates(templates.filter(x=>x.id!==t.id)); setConfirm({open:false}) }}) }} className="text-sm text-red-600">Delete</button></td></tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="mt-8 bg-white rounded-xl shadow p-6 max-w-4xl">
        <h2 className="text-xl font-semibold">Targets</h2>
        <form onSubmit={submitTargets} className="mt-4 space-y-3">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <input className="w-full p-3 border rounded-lg" placeholder="Name" value={targetForm.name} onChange={e=>setTargetForm({...targetForm,name:e.target.value})} />
            <input className="w-full p-3 border rounded-lg" placeholder="Email" value={targetForm.email} onChange={e=>setTargetForm({...targetForm,email:e.target.value})} />
            <input className="w-full p-3 border rounded-lg" placeholder="Department" value={targetForm.department} onChange={e=>setTargetForm({...targetForm,department:e.target.value})} />
          </div>
          <textarea className="w-full p-3 border rounded-lg" placeholder="Bulk add (one per line: Name, Email, Department)" value={targetForm.bulk} onChange={e=>setTargetForm({...targetForm,bulk:e.target.value})} />
          <div>
            <button className="px-4 py-2 bg-slate-900 text-white rounded-lg shadow">Add targets</button>
          </div>
        </form>
        <div className="mt-6 overflow-auto">
          <table className="w-full text-sm">
            <thead className="bg-slate-50"><tr><th className="p-3 text-left">ID</th><th className="p-3 text-left">Name</th><th className="p-3 text-left">Email</th><th className="p-3 text-left">Department</th><th className="p-3 text-left">Action</th></tr></thead>
            <tbody>
              {targets.map(t=> (
                <tr key={t.id} className="border-t"><td className="p-3">{t.id}</td><td className="p-3">{t.name}</td><td className="p-3">{t.email}</td><td className="p-3">{t.department || '—'}</td><td className="p-3"><button onClick={()=>{ setConfirm({open:true, title:'Delete target', message:`Delete target ${t.name}?`, onConfirm: async ()=>{ await fetch(`/api/targets/${t.id}`, {method:'DELETE', headers:{'X-Admin-Token': token}}); setTargets(targets.filter(x=>x.id!==t.id)); setConfirm({open:false}) }}) }} className="text-sm text-red-600">Delete</button></td></tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="mt-8 bg-white rounded-xl shadow p-6 max-w-4xl">
        <h2 className="text-xl font-semibold">Campaigns</h2>
        <form onSubmit={submitCampaign} className="mt-4 space-y-3">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <input className="w-full p-3 border rounded-lg" placeholder="Campaign name" value={campaignForm.name} onChange={e=>setCampaignForm({...campaignForm,name:e.target.value})} />
            <select className="w-full p-3 border rounded-lg" value={campaignForm.template_id} onChange={e=>setCampaignForm({...campaignForm,template_id: Number(e.target.value) || ''})}>
              <option value="">Select template</option>
              {templates.map(t=> <option key={t.id} value={t.id}>{t.name}</option>)}
            </select>
          </div>
          <textarea className="w-full p-3 border rounded-lg" placeholder="Notes (optional)" value={campaignForm.notes} onChange={e=>setCampaignForm({...campaignForm,notes:e.target.value})} />
          <div className="border rounded-lg p-3 max-h-48 overflow-auto">
            <div className="text-sm font-semibold mb-2">Select targets</div>
            {targets.map(t=> (
              <label key={t.id} className="flex items-center gap-2 text-sm mb-1">
                <input type="checkbox" checked={campaignForm.target_ids.includes(t.id)} onChange={()=>toggleTarget(t.id)} />
                <span>{t.name} ({t.email})</span>
              </label>
            ))}
            {!targets.length && <div className="text-sm text-slate-500">No targets yet.</div>}
          </div>
          <div>
            <button className="px-4 py-2 bg-slate-900 text-white rounded-lg shadow">Create campaign</button>
          </div>
        </form>
        <div className="mt-6 overflow-auto">
          <table className="w-full text-sm">
            <thead className="bg-slate-50"><tr><th className="p-3 text-left">ID</th><th className="p-3 text-left">Name</th><th className="p-3 text-left">Targets</th><th className="p-3 text-left">Opened</th><th className="p-3 text-left">Clicked</th><th className="p-3 text-left">Reported</th><th className="p-3 text-left">Action</th></tr></thead>
            <tbody>
              {campaigns.map(c=> (
                <tr key={c.id} className="border-t"><td className="p-3">{c.id}</td><td className="p-3">{c.name}</td><td className="p-3">{c.total_targets}</td><td className="p-3">{c.opened}</td><td className="p-3">{c.clicked}</td><td className="p-3">{c.reported}</td><td className="p-3"><button onClick={()=>{ setConfirm({open:true, title:'Delete campaign', message:`Delete campaign ${c.name}?`, onConfirm: async ()=>{ await fetch(`/api/campaigns/${c.id}`, {method:'DELETE', headers:{'X-Admin-Token': token}}); setCampaigns(campaigns.filter(x=>x.id!==c.id)); setConfirm({open:false}) }}) }} className="text-sm text-red-600">Delete</button></td></tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow p-6 max-w-3xl">
        <h2 className="text-xl font-semibold">Admin - Create Scenario</h2>
        <form onSubmit={submit} className="mt-4 space-y-3">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <input className="w-full p-3 border rounded-lg" placeholder="Sender" value={form.sender} onChange={e=>setForm({...form,sender:e.target.value})} />
            <input className="w-full p-3 border rounded-lg" placeholder="Subject" value={form.subject} onChange={e=>setForm({...form,subject:e.target.value})} />
          </div>
          <textarea className="w-full p-3 border rounded-lg" placeholder="Body" value={form.body} onChange={e=>setForm({...form,body:e.target.value})} />
          <div className="flex gap-4 items-center">
            <label className="flex items-center gap-2 text-sm"><input type="checkbox" checked={form.is_phishing} onChange={e=>setForm({...form,is_phishing:e.target.checked})} /> <span>Is phishing</span></label>
            <select className="p-2 border rounded-lg text-sm" value={form.difficulty} onChange={e=>setForm({...form,difficulty:e.target.value})}>
              <option value="easy">Easy</option>
              <option value="medium">Medium</option>
              <option value="hard">Hard</option>
            </select>
            <input className="flex-1 p-2 border rounded-lg" placeholder="Link text" value={form.link_text} onChange={e=>setForm({...form,link_text:e.target.value})} />
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <input className="w-full p-3 border rounded-lg" placeholder="Link URL" value={form.link_url} onChange={e=>setForm({...form,link_url:e.target.value})} />
            <input className="w-full p-3 border rounded-lg" placeholder="Feedback" value={form.feedback} onChange={e=>setForm({...form,feedback:e.target.value})} />
          </div>
          <div>
            <button className="px-4 py-2 bg-slate-900 text-white rounded-lg shadow">Create</button>
            <span className="ml-3 text-sm">{message}</span>
          </div>
        </form>
      </div>

      <h3 className="mt-8 text-lg font-semibold">Metrics</h3>
      <div className="mt-2 bg-white rounded-xl shadow overflow-auto">
        <table className="w-full text-sm border-collapse">
          <thead className="bg-slate-50"><tr><th className="p-3 text-left">Email ID</th><th className="p-3 text-left">Clicks</th><th className="p-3 text-left">Reports</th><th className="p-3 text-left">Opens</th></tr></thead>
          <tbody>
            {metrics.map(m=> (
              <tr key={m.email_id} className="border-t"><td className="p-3">{m.email_id}</td><td className="p-3">{m.clicks}</td><td className="p-3">{m.reports}</td><td className="p-3">{m.opens}</td></tr>
            ))}
          </tbody>
        </table>
      </div>
      <h3 className="mt-6 text-lg font-semibold">Recent User Actions</h3>
      <div className="mt-2 bg-white rounded-xl shadow overflow-auto">
        <table className="w-full text-sm">
          <thead className="bg-slate-50"><tr><th className="p-3 text-left">User</th><th className="p-3 text-left">Email ID</th><th className="p-3 text-left">Action</th><th className="p-3 text-left">When</th><th className="p-3 text-left">Action</th></tr></thead>
          <tbody>
            {actions.map(a=> (
              <tr key={a.id} className="border-t"><td className="p-3">{a.user_id || 'unknown'}</td><td className="p-3">{a.email_id}</td><td className="p-3">{a.action}</td><td className="p-3">{new Date(a.created_at).toLocaleString()}</td><td className="p-3"><button onClick={()=>{
                setConfirm({open:true, title:'Delete action', message:`Delete action ${a.id} performed by ${a.user_id || 'unknown'}?`, onConfirm: async ()=>{ await fetch(`/api/actions/${a.id}`, {method:'DELETE', headers:{'X-Admin-Token': token}}); setActions(actions.filter(x=>x.id!==a.id)); setConfirm({open:false}) }})
              }} className="text-sm text-red-600">Delete</button></td></tr>
            ))}
          </tbody>
        </table>
      </div>

      <h3 className="mt-6 text-lg font-semibold">Per-User Reports</h3>
      <div className="mt-2 bg-white rounded-xl shadow overflow-auto">
        <table className="w-full text-sm">
          <thead className="bg-slate-50"><tr><th className="p-3 text-left">User</th><th className="p-3 text-left">Checked</th><th className="p-3 text-left">Correct</th><th className="p-3 text-left">Accuracy</th><th className="p-3 text-left">Actions</th></tr></thead>
          <tbody>
            {userReports.map(u=> (
              <tr key={u.user_id} className="border-t"><td className="p-3">{u.user_id}</td><td className="p-3">{u.checked}</td><td className="p-3">{u.correct}</td><td className="p-3">{u.accuracy_percent? u.accuracy_percent.toFixed(1)+'%':'—'}</td><td className="p-3"><button onClick={()=>{ setConfirm({open:true, title:'Clear user actions', message:`Clear all actions for ${u.user_id}?`, onConfirm: async ()=>{ await fetch('/api/actions/clear_user', {method:'POST', headers:{'Content-Type':'application/json','X-Admin-Token': token}, body: JSON.stringify({user_id: u.user_id})}); setUserReports(userReports.filter(x=>x.user_id!==u.user_id)); setActions(actions.filter(a=>a.user_id !== u.user_id)); setConfirm({open:false}) }}) }} className="text-sm text-red-600">Clear</button></td></tr>
            ))}
          </tbody>
        </table>
      </div>

      <h3 className="mt-8 text-lg font-semibold">SMS Metrics</h3>
      <div className="mt-2 bg-white rounded-xl shadow overflow-auto">
        <table className="w-full text-sm border-collapse">
          <thead className="bg-slate-50"><tr><th className="p-3 text-left">Message ID</th><th className="p-3 text-left">Clicks</th><th className="p-3 text-left">Reports</th><th className="p-3 text-left">Opens</th></tr></thead>
          <tbody>
            {smsMetrics.map(m=> (
              <tr key={m.message_id} className="border-t"><td className="p-3">{m.message_id}</td><td className="p-3">{m.clicks}</td><td className="p-3">{m.reports}</td><td className="p-3">{m.opens}</td></tr>
            ))}
          </tbody>
        </table>
      </div>

      <h3 className="mt-6 text-lg font-semibold">Recent SMS Actions</h3>
      <div className="mt-2 bg-white rounded-xl shadow overflow-auto">
        <table className="w-full text-sm">
          <thead className="bg-slate-50"><tr><th className="p-3 text-left">User</th><th className="p-3 text-left">Message ID</th><th className="p-3 text-left">Action</th><th className="p-3 text-left">Time to action</th><th className="p-3 text-left">When</th></tr></thead>
          <tbody>
            {smsActions.map(a=> (
              <tr key={a.id} className="border-t"><td className="p-3">{a.user_id || 'unknown'}</td><td className="p-3">{a.message_id}</td><td className="p-3">{a.action}</td><td className="p-3">{typeof a.time_to_action_seconds === 'number' ? `${a.time_to_action_seconds.toFixed(1)}s` : '—'}</td><td className="p-3">{new Date(a.created_at).toLocaleString()}</td></tr>
            ))}
          </tbody>
        </table>
      </div>

      <h3 className="mt-6 text-lg font-semibold">SMS Per-User Reports</h3>
      <div className="mt-2 bg-white rounded-xl shadow overflow-auto">
        <table className="w-full text-sm">
          <thead className="bg-slate-50"><tr><th className="p-3 text-left">User</th><th className="p-3 text-left">Checked</th><th className="p-3 text-left">Correct</th><th className="p-3 text-left">Accuracy</th><th className="p-3 text-left">Actions</th></tr></thead>
          <tbody>
            {smsUserReports.map(u=> (
              <tr key={u.user_id} className="border-t"><td className="p-3">{u.user_id}</td><td className="p-3">{u.checked}</td><td className="p-3">{u.correct}</td><td className="p-3">{u.accuracy_percent? u.accuracy_percent.toFixed(1)+'%':'—'}</td><td className="p-3"><button onClick={()=>{ setConfirm({open:true, title:'Clear SMS user actions', message:`Clear all SMS actions for ${u.user_id}?`, onConfirm: async ()=>{ await fetch('/api/sms/actions/clear_user', {method:'POST', headers:{'Content-Type':'application/json','X-Admin-Token': token}, body: JSON.stringify({user_id: u.user_id})}); setSmsUserReports(smsUserReports.filter(x=>x.user_id!==u.user_id)); setSmsActions(smsActions.filter(a=>a.user_id !== u.user_id)); setConfirm({open:false}) }}) }} className="text-sm text-red-600">Clear</button></td></tr>
            ))}
          </tbody>
        </table>
      </div>

      <h3 className="mt-6 text-lg font-semibold">Emails (admin)</h3>
      <div className="mt-2 bg-white rounded-xl shadow overflow-auto">
        <table className="w-full text-sm">
          <thead className="bg-slate-50"><tr><th className="p-3 text-left">ID</th><th className="p-3 text-left">Sender</th><th className="p-3 text-left">Subject</th><th className="p-3 text-left">Actions</th></tr></thead>
          <tbody>
            {emailsAdmin.map(em=> (
              <tr key={em.id} className="border-t"><td className="p-3">{em.id}</td><td className="p-3">{em.sender}</td><td className="p-3">{em.subject}</td><td className="p-3"><button onClick={()=>{ setConfirm({open:true, title:'Delete email', message:`Delete email ${em.id} — ${em.subject}?`, onConfirm: async ()=>{ await fetch(`/api/emails/${em.id}`, {method:'DELETE', headers:{'X-Admin-Token': token}}); setEmailsAdmin(emailsAdmin.filter(x=>x.id!==em.id)); setMetrics(metrics.filter(m=>m.email_id!==em.id)); setConfirm({open:false}) }}) }} className="text-sm text-red-600">Delete</button></td></tr>
            ))}
          </tbody>
        </table>
      </div>
      <ConfirmModal open={confirm.open} title={confirm.title} message={confirm.message} onConfirm={confirm.onConfirm} onCancel={()=>setConfirm({open:false})} />
    </div>
  )
}
