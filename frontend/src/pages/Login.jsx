import React, {useState} from 'react'
import { useNavigate } from 'react-router-dom'
import loginBg from '../assets/login logos.webp'

export default function Login(){
  const [name, setName] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [adminPassword, setAdminPassword] = useState('')
  const [adminError, setAdminError] = useState('')
  const [showAdmin, setShowAdmin] = useState(false)
  const nav = useNavigate()

  async function submit(e){
    e.preventDefault()
    setError('')
    if(!name.trim()){
      setError('Please enter your name')
      return
    }
    try{
      const r = await fetch('/api/login', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({name: name.trim(), password, role: 'user'})})
      const j = await r.json()
      if(r.ok && j.token){
        localStorage.setItem('adminToken', j.token)
        localStorage.setItem('role', j.role || 'user')
        localStorage.setItem('token', j.token)
        localStorage.setItem('displayName', j.name || name.trim())
        nav('/')
      }else{
        if((j.error || '').toLowerCase().includes('name')){
          setError('Please enter your name')
        }else if((j.error || '').toLowerCase().includes('password')){
          setError('Wrong password. Default user password is "user".')
        }else{
          setError('Login failed')
        }
      }
    }catch(err){ setError('Network error') }
  }

  async function submitAdmin(e){
    e.preventDefault()
    setAdminError('')
    try{
      const r = await fetch('/api/login', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({password: adminPassword, role: 'admin'})})
      const j = await r.json()
      if(r.ok && j.token){
        localStorage.setItem('adminToken', j.token)
        localStorage.setItem('role', j.role || 'admin')
        localStorage.setItem('token', j.token)
        nav('/admin')
      }else{
        setAdminError('Wrong admin password.')
      }
    }catch(err){ setAdminError('Network error') }
  }

  return (
      <div
        className="relative left-1/2 right-1/2 -translate-x-1/2 w-screen min-h-screen px-4 py-10 bg-cover bg-center bg-no-repeat"
        style={{
          backgroundImage: `linear-gradient(rgba(8, 20, 28, 0.46), rgba(8, 20, 28, 0.46)), url(${loginBg})`
        }}
      >
        <button
          type="button"
          onClick={()=>setShowAdmin(v=>!v)}
          className="absolute top-5 right-5 px-3 py-2 rounded-lg bg-slate-900/75 text-white text-sm border border-slate-200/20 hover:bg-slate-900"
        >
          {showAdmin ? 'Close Admin' : 'Admin'}
        </button>

        {showAdmin && (
          <div className="absolute top-16 right-5 w-full max-w-sm bg-slate-900/95 text-white rounded-2xl shadow-xl p-6 backdrop-blur-sm border border-slate-100/20 z-20">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold">Admin Login</h3>
              <span className="text-xs uppercase tracking-[0.25em] text-slate-400">Restricted</span>
            </div>
            <p className="mt-2 text-sm text-slate-300">For administrators only.</p>

            <form onSubmit={submitAdmin} className="mt-5 space-y-4">
              <input type="password" className="w-full p-3 rounded-lg bg-slate-900 border border-slate-700 text-white placeholder:text-slate-500 focus:ring-2 focus:ring-slate-500" placeholder="Admin password" value={adminPassword} onChange={e=>setAdminPassword(e.target.value)} />
              <button className="w-full px-4 py-2 bg-white text-slate-900 rounded-lg font-semibold">Admin log in</button>
              {adminError && <div className="text-rose-300 text-sm">{adminError}</div>}
            </form>
          </div>
        )}

        <div className="max-w-xl mx-auto min-h-screen flex items-center justify-center">
          <div className="w-full bg-white rounded-2xl shadow-lg p-8 border border-white/80">
              <div className="flex items-center gap-3">
                <div className="bg-slate-100 text-slate-800 rounded-full w-12 h-12 flex items-center justify-center">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M3 12h18" stroke="#0f172a" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg>
                </div>
                <div>
                  <h2 className="text-2xl font-semibold text-slate-900">User Login</h2>
                  <p className="text-sm text-slate-600">Enter your name and the default password.</p>
                </div>
              </div>

              <form onSubmit={submit} className="mt-6 space-y-4">
                <input type="text" className="w-full p-3 border rounded-lg shadow-sm focus:ring-2 focus:ring-slate-400" placeholder="Your name" value={name} onChange={e=>setName(e.target.value)} />
                <input type="password" className="w-full p-3 border rounded-lg shadow-sm focus:ring-2 focus:ring-slate-400" placeholder="User password" value={password} onChange={e=>setPassword(e.target.value)} />
                <div className="flex items-center justify-between">
                  <button className="px-4 py-2 bg-slate-900 text-white rounded-lg shadow">Log in</button>
                  <span className="text-sm text-slate-500">Default password: <strong>user</strong></span>
                </div>
                {error && <div className="text-red-600 text-sm">{error}</div>}
              </form>
          </div>
        </div>
      </div>
  )
}
