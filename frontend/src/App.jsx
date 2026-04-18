import React, {useEffect, useState} from 'react'
import EmailList from './components/EmailList'
import EmailView from './components/EmailView'
import InboxTips from './components/InboxTips'
import SmsList from './components/SmsList'
import SmsView from './components/SmsView'
import SmsTips from './components/SmsTips'
import Admin from './pages/Admin'
import Login from './pages/Login'
import Feedback from './pages/Feedback'
import Awareness from './pages/Awareness'
import Phished from './pages/Phished'
import SafeLink from './pages/SafeLink'
import Home from './pages/Home'
import { Routes, Route, Link, Navigate, useNavigate, useLocation } from 'react-router-dom'

// AUTH STORAGE PATTERN:
// - localStorage.token: JWT token for all authenticated requests (user or admin)
// - localStorage.role: 'user' or 'admin' (set by backend during login)
// - Both are cleared on logout or failed auth
// - Components read these values on-demand; no centralized auth context needed

export default function App(){
  const [emails, setEmails] = useState([])
  const [selected, setSelected] = useState(null)
  const [feedbacks, setFeedbacks] = useState([])
  const [attemptedEmailIds, setAttemptedEmailIds] = useState([])
  const [attemptedSmsIds, setAttemptedSmsIds] = useState([])
  const [selectedSms, setSelectedSms] = useState(null)
  const [simTab, setSimTab] = useState('email')
  const [smsMessages, setSmsMessages] = useState([])
  const [globalError, setGlobalError] = useState(null)

  function showGlobalError(message, onRetry){
    setGlobalError({ message, onRetry: onRetry || null })
  }

  function clearGlobalError(){
    setGlobalError(null)
  }

  async function loadEmails(){
    try{
      const r = await fetch('/api/emails')
      if(!r.ok) throw new Error('Failed to load emails')
      const data = await r.json()
      setEmails(data)
      clearGlobalError()

      // removed auto-generation to keep a fixed inbox size
    }catch(e){
      setEmails([])
      showGlobalError('Could not load email scenarios. Please retry.', loadEmails)
    }
  }

  useEffect(()=>{ loadEmails() }, [])

  async function loadSms(){
    try{
      const r = await fetch('/api/sms')
      if(!r.ok) throw new Error('Failed to load sms')
      const data = await r.json()
      setSmsMessages(data)
      clearGlobalError()
    }catch(e){
      setSmsMessages([])
      showGlobalError('Could not load SMS scenarios. Please retry.', loadSms)
    }
  }

  useEffect(()=>{ loadSms() }, [])

  const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null
  const role = typeof window !== 'undefined' ? localStorage.getItem('role') : null
  const navigate = useNavigate()
  const location = useLocation()

  async function loadFeedback(){
    if(!token){
      setFeedbacks([])
      setAttemptedEmailIds([])
      setAttemptedSmsIds([])
      return
    }
    try{
      const r = await fetch('/api/feedback', { headers: {'X-Token': token} })
      if(!r.ok) throw new Error('Failed to load feedback')
      const data = await r.json()
      setFeedbacks(Array.isArray(data) ? data : [])
      const emailIds = new Set()
      const smsIds = new Set()
      for(const entry of (Array.isArray(data) ? data : [])){
        if((entry.channel || 'email') === 'sms') smsIds.add(entry.item_id)
        else emailIds.add(entry.item_id)
      }
      setAttemptedEmailIds([...emailIds])
      setAttemptedSmsIds([...smsIds])
    }catch(e){
      showGlobalError('Could not load feedback history. Please retry.', loadFeedback)
    }
  }

  const isActive = (path) => location.pathname === path
  const isAwareness = location.pathname === '/awareness'
  const isLogin = location.pathname === '/login'
  const isFullBleed = isAwareness || isLogin
  const navClass = (path) =>
    "px-4 py-2 rounded-full text-sm font-medium transition " +
    (isActive(path)
      ? 'bg-white text-slate-900 shadow'
      : 'bg-white/15 text-white hover:bg-white/25')

  useEffect(()=>{
    if(!token && location.pathname !== '/login'){
      navigate('/login')
    }
  }, [token, location.pathname, navigate])

  useEffect(()=>{
    loadFeedback()
  }, [token])

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
      return [newItem, ...filtered]
    })

    if(channel === 'sms'){
      setAttemptedSmsIds(prev=>{
        return prev.includes(itemId) ? prev : [...prev, itemId]
      })
    }else{
      setAttemptedEmailIds(prev=>{
        return prev.includes(itemId) ? prev : [...prev, itemId]
      })
    }
  }

  async function resetSimulationProgress(){
    const activeToken = typeof window !== 'undefined' ? localStorage.getItem('token') : null
    if(activeToken){
      try{
        const r = await fetch('/api/feedback/reset', {
          method: 'POST',
          headers: {'Content-Type':'application/json', 'X-Token': activeToken},
          body: JSON.stringify({}),
        })
        if(!r.ok) throw new Error('Failed to reset')
      }catch(e){
        showGlobalError('Could not reset progress right now. Please retry.', resetSimulationProgress)
        return
      }
    }
    setFeedbacks([])
    setAttemptedEmailIds([])
    setAttemptedSmsIds([])
    clearGlobalError()
  }

  const emailIds = new Set(emails.map(e => e.id))
  const smsIds = new Set(smsMessages.map(s => s.id))
  const completedEmailCount = attemptedEmailIds.filter(id => emailIds.has(id)).length
  const completedSmsCount = attemptedSmsIds.filter(id => smsIds.has(id)).length
  const totalScenarios = emails.length + smsMessages.length
  const completedScenarios = completedEmailCount + completedSmsCount
  const correctCount = feedbacks.filter(f => f.correct === true).length
  const accuracy = feedbacks.length ? Math.round((correctCount / feedbacks.length) * 100) : 0

  const clickedPhishMistakes = feedbacks.filter(f => f.channel === 'email' && f.action === 'click' && f.correct === false).length +
    feedbacks.filter(f => f.channel === 'sms' && f.action === 'click' && f.correct === false).length
  const overReportedLegit = feedbacks.filter(f => f.action === 'report' && f.correct === false).length

  const currentTotal = simTab === 'email' ? emails.length : smsMessages.length
  const currentDone = simTab === 'email' ? completedEmailCount : completedSmsCount
  const allFinished = totalScenarios > 0 && completedScenarios >= totalScenarios

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="bg-gradient-to-r from-slate-950 to-slate-800 text-white">
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
            {location.pathname !== '/login' && <Link to="/home" className={navClass('/home')}>Home</Link>}
            {token ? (
              <>
                <Link to="/simulation" className={navClass('/simulation')}>Simulation</Link>
                  <Link to="/awareness" className={navClass('/awareness')}>Awareness</Link>
                <Link to="/feedback" className={navClass('/feedback')}>Feedback</Link>
                <Link to="/admin" className={navClass('/admin')}>Admin</Link>
                <button onClick={logout} className="px-4 py-2 rounded-full text-sm font-medium bg-white/10 text-white hover:bg-white/20 transition">Logout</button>
              </>
            ) : (
              location.pathname !== '/login' ? (
                <Link to="/login" className={navClass('/login')}>Login</Link>
              ) : null
            )}
          </nav>
        </div>
      </header>

      {globalError && (
        <div className="max-w-6xl mx-auto px-6 pt-4" role="alert" aria-live="polite">
          <div className="rounded-xl border border-amber-300 bg-amber-50 p-4 flex items-center justify-between gap-3">
            <div className="text-sm text-amber-900">{globalError.message}</div>
            <div className="flex items-center gap-2 shrink-0">
              {globalError.onRetry && (
                <button
                  onClick={async ()=>{
                    clearGlobalError()
                    await globalError.onRetry()
                  }}
                  className="px-3 py-1.5 rounded-lg border border-amber-500 text-amber-900 text-sm font-medium hover:bg-amber-100"
                >
                  Retry
                </button>
              )}
              <button onClick={clearGlobalError} className="px-3 py-1.5 rounded-lg text-sm text-amber-900 hover:bg-amber-100">Dismiss</button>
            </div>
          </div>
        </div>
      )}

      {isFullBleed ? (
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/awareness" element={<Awareness />} />
        </Routes>
      ) : (
        <main className="max-w-6xl mx-auto p-6">
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/" element={<Navigate to="/login" replace />} />
            <Route path="/admin" element={token ? <Admin /> : <Navigate to="/login" replace />} />
            <Route path="/home" element={token ? <Home /> : <Navigate to="/login" replace />} />
            <Route path="/feedback" element={<Feedback feedbacks={feedbacks} />} />
            <Route path="/phished" element={<Phished />} />
            <Route path="/safe-link" element={<SafeLink />} />
            <Route path="/simulation" element={token ? (
              <div className="rounded-2xl border border-rose-100 bg-gradient-to-br from-rose-50 via-amber-50 to-orange-50 p-4 sm:p-6 shadow-sm">
                <div className="mb-6 grid grid-cols-1 lg:grid-cols-3 gap-4">
                  <div className="bg-white/90 rounded-xl border border-rose-200 shadow-sm p-4">
                    <div className="text-xs uppercase tracking-wide text-slate-500">Simulation Score</div>
                    <div className="mt-2 text-2xl font-bold text-slate-900">{correctCount}/{feedbacks.length || 0}</div>
                    <div className="text-sm text-slate-600 mt-1">Accuracy: {accuracy}%</div>
                  </div>

                  <div className="bg-white/90 rounded-xl border border-amber-200 shadow-sm p-4">
                    <div className="text-xs uppercase tracking-wide text-slate-500">Progress</div>
                    <div className="mt-2 text-sm text-slate-700">Current tab: {currentDone}/{currentTotal || 0}</div>
                    <div className="mt-2 h-2 bg-slate-100 rounded-full overflow-hidden">
                      <div className="h-full bg-orange-500" style={{width: `${currentTotal ? (currentDone / currentTotal) * 100 : 0}%`}} />
                    </div>
                    <div className="mt-3 text-sm text-slate-700">Overall: {completedScenarios}/{totalScenarios || 0}</div>
                    <div className="mt-2 h-2 bg-slate-100 rounded-full overflow-hidden">
                      <div className="h-full bg-rose-700" style={{width: `${totalScenarios ? (completedScenarios / totalScenarios) * 100 : 0}%`}} />
                    </div>
                  </div>

                  <div className="bg-white/90 rounded-xl border border-orange-200 shadow-sm p-4">
                    <div className="text-xs uppercase tracking-wide text-slate-500">Learning Pattern</div>
                    <div className="mt-2 text-sm text-slate-700">Clicked suspicious links: <span className="font-semibold">{clickedPhishMistakes}</span></div>
                    <div className="text-sm text-slate-700 mt-1">Reported legitimate items: <span className="font-semibold">{overReportedLegit}</span></div>
                    <button onClick={resetSimulationProgress} className="mt-3 text-sm px-3 py-1.5 rounded-lg border border-rose-300 text-rose-800 hover:bg-rose-100">Restart Progress</button>
                  </div>
                </div>

                {allFinished && (
                  <div className="mb-6 bg-emerald-50 border border-emerald-200 rounded-xl p-4">
                    <div className="text-lg font-semibold text-emerald-900">Simulation Complete</div>
                    <p className="text-sm text-emerald-800 mt-1">You completed all scenarios. Final score: {correctCount}/{feedbacks.length || 0} ({accuracy}%).</p>
                    <div className="mt-2 text-sm text-emerald-900">Top improvement area: {clickedPhishMistakes >= overReportedLegit ? 'Pause before clicking urgent links.' : 'Verify context before reporting legitimate messages.'}</div>
                  </div>
                )}

                <div className="mb-5 flex gap-2">
                  <button onClick={()=>setSimTab('email')} className={"px-3 py-2 rounded-lg text-sm border font-medium transition " + (simTab==='email' ? 'bg-rose-700 border-rose-700 text-white shadow' : 'bg-white/90 border-rose-200 text-rose-800 hover:bg-rose-50')}>Email Simulation</button>
                  <button onClick={()=>setSimTab('sms')} className={"px-3 py-2 rounded-lg text-sm border font-medium transition " + (simTab==='sms' ? 'bg-teal-700 border-teal-700 text-white shadow' : 'bg-white/90 border-teal-200 text-teal-800 hover:bg-teal-50')}>SMS Simulation</button>
                </div>

                {simTab === 'email' && (
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <aside className="md:col-span-1">
                      <div className="mb-4"><InboxTips /></div>
                      <EmailList emails={emails} onSelect={async (e)=>{
                        if(e && e.id){
                          const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null
                          try{
                            const opened = await fetch(`/api/emails/${e.id}/open`, { method:'POST', headers:{'Content-Type':'application/json','X-Token': token}, body: JSON.stringify({}) })
                            if(!opened.ok) throw new Error('Failed to open selected email')
                            const details = await fetch(`/api/emails/${e.id}`)
                            if(!details.ok) throw new Error('Failed to load selected email')
                            const data = await details.json()
                            setSelected(data)
                            clearGlobalError()
                          }catch(err){
                            showGlobalError('Could not open this email. Please try again.', loadEmails)
                          }
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
                          try{
                            const opened = await fetch(`/api/sms/${m.id}/open`, { method:'POST', headers:{'Content-Type':'application/json','X-Token': token}, body: JSON.stringify({}) })
                            if(!opened.ok) throw new Error('Failed to open selected sms')
                            const selected = await fetch(`/api/sms`)
                            if(!selected.ok) throw new Error('Failed to load selected sms')
                            const list = await selected.json()
                            setSelectedSms(list.find(item=>item.id===m.id) || m)
                            clearGlobalError()
                          }catch(err){
                            showGlobalError('Could not open this SMS. Please try again.', loadSms)
                          }
                        }
                      }} selectedId={selectedSms?.id} />
                    </aside>
                    <section className="md:col-span-2">
                      <SmsView message={selectedSms} onFeedback={handleFeedback} />
                    </section>
                  </div>
                )}
              </div>
            ) : <Navigate to="/login" replace />} />
          </Routes>
        </main>
      )}
    </div>
  )
}
