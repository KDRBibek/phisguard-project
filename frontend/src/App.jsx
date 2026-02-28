import React, {useEffect, useState} from 'react'
import EmailList from './components/EmailList'
import EmailView from './components/EmailView'
import InboxTips from './components/InboxTips'
import SmsList from './components/SmsList'
import SmsView from './components/SmsView'
import SmsTips from './components/SmsTips'
import Admin from './pages/Admin'
import Login from './pages/Login'
import Simulation from './pages/Simulation'
import Feedback from './pages/Feedback'
import Awareness from './pages/Awareness'
import Phished from './pages/Phished'
import { Routes, Route, Link, useNavigate, useLocation } from 'react-router-dom'

export default function App(){
  const [emails, setEmails] = useState([])
  const [selected, setSelected] = useState(null)
  const [feedbacks, setFeedbacks] = useState([])
  const [attemptedEmailIds, setAttemptedEmailIds] = useState([])
  const [attemptedSmsIds, setAttemptedSmsIds] = useState([])
  const [selectedSms, setSelectedSms] = useState(null)
  const [simTab, setSimTab] = useState('email')
  const [smsMessages, setSmsMessages] = useState([])

  async function loadEmails(){
    try{
      const r = await fetch('/api/emails')
      const data = await r.json()
      setEmails(data)

      // removed auto-generation to keep a fixed inbox size
    }catch(e){ setEmails([]) }
  }

  useEffect(()=>{ loadEmails() }, [])

  async function loadSms(){
    try{
      const r = await fetch('/api/sms')
      const data = await r.json()
      setSmsMessages(data)
    }catch(e){ setSmsMessages([]) }
  }

  useEffect(()=>{ loadSms() }, [])

  useEffect(()=>{
    try{
      const stored = JSON.parse(localStorage.getItem('feedbackLog') || '[]')
      const storedEmailIds = JSON.parse(localStorage.getItem('attemptedEmailIds') || '[]')
      const storedSmsIds = JSON.parse(localStorage.getItem('attemptedSmsIds') || '[]')
      const legacyIds = JSON.parse(localStorage.getItem('attemptedIds') || '[]')
      setFeedbacks(stored)
      setAttemptedEmailIds(storedEmailIds.length ? storedEmailIds : legacyIds)
      setAttemptedSmsIds(storedSmsIds)
    }catch(e){ /* ignore */ }
  }, [])

  const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null
  const role = typeof window !== 'undefined' ? localStorage.getItem('role') : null
  const navigate = useNavigate()
  const location = useLocation()

  const isActive = (path) => location.pathname === path
  const navClass = (path) =>
    "px-4 py-2 rounded-full text-sm font-medium transition " +
    (isActive(path)
      ? 'bg-white text-indigo-700 shadow'
      : 'bg-white/15 text-white hover:bg-white/25')

  useEffect(()=>{
    if(!token && location.pathname !== '/login'){
      navigate('/login')
    }
  }, [token, location.pathname, navigate])

  function logout(){
    if(typeof window !== 'undefined'){
      const t = localStorage.getItem('token')
      fetch('/api/logout', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({token: t})}).catch(()=>{})
      localStorage.removeItem('token')
      localStorage.removeItem('role')
      navigate('/login')
    }
  }

  function handleFeedback(entry){
    if(!entry?.item) return
    const channel = entry.channel || 'email'
    const itemId = entry.item.id
    const newItem = {
      item_id: itemId,
      channel,
      subject: entry.item.subject || `SMS from ${entry.item.sender}`,
      sender: entry.item.sender,
      action: entry.action,
      correct: entry.result?.correct,
      message: entry.result?.message,
      tip: entry.result?.tip,
      time_to_action_seconds: entry.result?.time_to_action_seconds,
      created_at: new Date().toISOString()
    }

    setFeedbacks(prev=>{
      const filtered = prev.filter(f=>!(f.item_id === newItem.item_id && (f.channel || 'email') === newItem.channel))
      const next = [newItem, ...filtered]
      localStorage.setItem('feedbackLog', JSON.stringify(next))
      return next
    })

    if(channel === 'sms'){
      setAttemptedSmsIds(prev=>{
        const next = prev.includes(itemId) ? prev : [...prev, itemId]
        localStorage.setItem('attemptedSmsIds', JSON.stringify(next))
        return next
      })
    }else{
      setAttemptedEmailIds(prev=>{
        const next = prev.includes(itemId) ? prev : [...prev, itemId]
        localStorage.setItem('attemptedEmailIds', JSON.stringify(next))
        return next
      })
    }
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="bg-gradient-to-r from-indigo-600 to-indigo-400 text-white">
        <div className="max-w-6xl mx-auto p-6 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="bg-white/20 rounded-full w-12 h-12 flex items-center justify-center shadow-md">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M3 12h18" stroke="white" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/><path d="M7 6h10" stroke="white" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/><path d="M7 18h10" stroke="white" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg>
            </div>
            <div>
              <h1 className="text-lg font-semibold">PHISGUARD</h1>
              <p className="text-sm opacity-90">Interactive phishing simulation</p>
            </div>
          </div>
          <nav className="flex items-center gap-2">
            {location.pathname !== '/login' && <Link to="/" className={navClass('/')}>Home</Link>}
            {token ? (
              <>
                <Link to="/simulation" className={navClass('/simulation')}>Simulation</Link>
                  <Link to="/awareness" className={navClass('/awareness')}>Awareness</Link>
                <Link to="/feedback" className={navClass('/feedback')}>Feedback</Link>
                {role === 'admin' && <Link to="/admin" className={navClass('/admin')}>Admin</Link>}
                <button onClick={logout} className="px-4 py-2 rounded-full text-sm font-medium bg-white/10 text-white hover:bg-white/20 transition">Logout</button>
              </>
            ) : (
              <Link to="/login" className={navClass('/login')}>Login</Link>
            )}
          </nav>
        </div>
      </header>

      <main className="max-w-6xl mx-auto p-6">
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/admin" element={<Admin />} />
          <Route path="/" element={<Simulation emails={emails} smsMessages={smsMessages} feedbacks={feedbacks} attemptedEmailIds={attemptedEmailIds} attemptedSmsIds={attemptedSmsIds} />} />
          <Route path="/awareness" element={<Awareness />} />
          <Route path="/feedback" element={<Feedback feedbacks={feedbacks} />} />
          <Route path="/phished" element={<Phished />} />
          <Route path="/simulation" element={
            <div>
              <div className="mb-5 flex gap-2">
                <button onClick={()=>setSimTab('email')} className={"px-3 py-2 rounded-lg text-sm border " + (simTab==='email' ? 'bg-indigo-50 border-indigo-200 text-indigo-700' : 'bg-white border-slate-200 text-slate-600 hover:bg-slate-50')}>Email Simulation</button>
                <button onClick={()=>setSimTab('sms')} className={"px-3 py-2 rounded-lg text-sm border " + (simTab==='sms' ? 'bg-emerald-50 border-emerald-200 text-emerald-700' : 'bg-white border-slate-200 text-slate-600 hover:bg-slate-50')}>SMS Simulation</button>
              </div>

              {simTab === 'email' && (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <aside className="md:col-span-1">
                    <div className="mb-4"><InboxTips /></div>
                    <EmailList emails={emails} onSelect={async (e)=>{
                      if(e && e.id){
                        const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null
                        await fetch(`/api/emails/${e.id}/open`, { method:'POST', headers:{'Content-Type':'application/json','X-Token': token}, body: JSON.stringify({}) }).catch(()=>{})
                        fetch(`/api/emails/${e.id}`).then(r=>r.json()).then(setSelected)
                      }
                    }} selectedId={selected?.id} />
                  </aside>
                  <section className="md:col-span-2">
                    <EmailView email={selected} onRefresh={loadEmails} onFeedback={handleFeedback} />
                  </section>
                </div>
              )}

              {simTab === 'sms' && (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <aside className="md:col-span-1">
                    <div className="mb-4"><SmsTips /></div>
                    <SmsList messages={smsMessages} onSelect={async (m)=>{
                      if(m && m.id){
                        const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null
                        await fetch(`/api/sms/${m.id}/open`, { method:'POST', headers:{'Content-Type':'application/json','X-Token': token}, body: JSON.stringify({}) }).catch(()=>{})
                        const selected = await fetch(`/api/sms`).then(r=>r.json()).then(list=> list.find(item=>item.id===m.id))
                        setSelectedSms(selected || m)
                      }
                    }} selectedId={selectedSms?.id} />
                  </aside>
                  <section className="md:col-span-2">
                    <SmsView message={selectedSms} onFeedback={handleFeedback} />
                  </section>
                </div>
              )}
            </div>
          } />
        </Routes>
      </main>
    </div>
  )
}
