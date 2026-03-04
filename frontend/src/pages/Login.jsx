import React, {useState} from 'react'
import { useNavigate } from 'react-router-dom'
import loginBg from '../assets/login logos.webp'

export default function Login(){
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
    const [adminPassword, setAdminPassword] = useState('')
    const [adminError, setAdminError] = useState('')
  const nav = useNavigate()

  async function submit(e){
    e.preventDefault()
    setError('')
    try{
      const r = await fetch('/api/login', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({password, role: 'user'})})
      const j = await r.json()
      if(r.ok && j.token){
        localStorage.setItem('adminToken', j.token)
          localStorage.setItem('role', j.role || 'user')
          // store token under a generic key
          localStorage.setItem('token', j.token)
          nav('/')
      }else{
        setError(j.error || 'Login failed')
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
          setAdminError(j.error || 'Admin login failed')
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
        <div className="max-w-5xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-[2fr_1fr] gap-6 items-start">
            <div className="w-full bg-white rounded-2xl shadow-lg p-8 border border-white/80">
              <div className="flex items-center gap-3">
                <div className="bg-slate-100 text-slate-800 rounded-full w-12 h-12 flex items-center justify-center">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M3 12h18" stroke="#0f172a" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg>
                </div>
                <div>
                  <h2 className="text-2xl font-semibold text-slate-900">User Login</h2>
                  <p className="text-sm text-slate-600">Access simulations and learning tools.</p>
                </div>
              </div>

              <form onSubmit={submit} className="mt-6 space-y-4">
                <input type="password" className="w-full p-3 border rounded-lg shadow-sm focus:ring-2 focus:ring-slate-400" placeholder="User password" value={password} onChange={e=>setPassword(e.target.value)} />
                <div className="flex items-center justify-between">
                  <button className="px-4 py-2 bg-slate-900 text-white rounded-lg shadow">Log in</button>
                  <span className="text-sm text-slate-500">Default: <strong>user</strong></span>
                </div>
                {error && <div className="text-red-600 text-sm">{error}</div>}
              </form>
            </div>

            <div className="w-full bg-slate-900/92 text-white rounded-2xl shadow-xl p-6 lg:sticky lg:top-8 backdrop-blur-sm border border-slate-100/20">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold">Admin Login</h3>
                <span className="text-xs uppercase tracking-[0.25em] text-slate-400">Restricted</span>
              </div>
              <p className="mt-2 text-sm text-slate-300">For administrators managing simulations and analytics.</p>

              <form onSubmit={submitAdmin} className="mt-5 space-y-4">
                <input type="password" className="w-full p-3 rounded-lg bg-slate-900 border border-slate-800 text-white placeholder:text-slate-500 focus:ring-2 focus:ring-slate-500" placeholder="Admin password" value={adminPassword} onChange={e=>setAdminPassword(e.target.value)} />
                <button className="w-full px-4 py-2 bg-white text-slate-900 rounded-lg font-semibold">Admin log in</button>
                {adminError && <div className="text-rose-300 text-sm">{adminError}</div>}
              </form>
            </div>
          </div>
        </div>
      </div>
  )
}
