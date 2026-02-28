import React, {useState} from 'react'
import { useNavigate } from 'react-router-dom'

export default function Login(){
  const [password, setPassword] = useState('')
  const [role, setRole] = useState('user')
  const [error, setError] = useState('')
  const nav = useNavigate()

  async function submit(e){
    e.preventDefault()
    setError('')
    try{
      const r = await fetch('/api/login', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({password, role})})
      const j = await r.json()
      if(r.ok && j.token){
        localStorage.setItem('adminToken', j.token)
          localStorage.setItem('role', j.role || 'user')
          // store token under a generic key
          localStorage.setItem('token', j.token)
          nav('/simulation')
      }else{
        setError(j.error || 'Login failed')
      }
    }catch(err){ setError('Network error') }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-b from-slate-50 to-white">
      <div className="w-full max-w-md bg-white rounded-xl shadow-lg p-6">
          <div className="flex items-center gap-3">
          <div className="bg-indigo-50 text-indigo-600 rounded-full w-12 h-12 flex items-center justify-center">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M3 12h18" stroke="#4F46E5" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg>
          </div>
          <div>
            <h2 className="text-2xl font-semibold">Login</h2>
            <p className="text-sm text-slate-500">Enter the admin password to manage simulations</p>
          </div>
        </div>

        <form onSubmit={submit} className="mt-5 space-y-4">
          <div className="flex gap-3 items-center">
            <label className={"px-3 py-1 rounded-full " + (role==='user'? 'bg-indigo-50 text-indigo-600' : 'bg-slate-100 text-slate-600')}>
              <input type="radio" name="role" value="user" checked={role==='user'} onChange={()=>setRole('user')} className="mr-2" /> User
            </label>
            <label className={"px-3 py-1 rounded-full " + (role==='admin'? 'bg-indigo-50 text-indigo-600' : 'bg-slate-100 text-slate-600')}>
              <input type="radio" name="role" value="admin" checked={role==='admin'} onChange={()=>setRole('admin')} className="mr-2" /> Admin
            </label>
          </div>
          <input type="password" className="w-full p-3 border rounded-lg shadow-sm focus:ring-2 focus:ring-indigo-300" placeholder="Password" value={password} onChange={e=>setPassword(e.target.value)} />
          <div className="flex items-center justify-between">
            <button className="px-4 py-2 bg-indigo-600 text-white rounded-lg shadow">Log in</button>
            <span className="text-sm text-slate-500">Default: <strong>user</strong></span>
          </div>
          {error && <div className="text-red-600 text-sm">{error}</div>}
        </form>
      </div>
    </div>
  )
}
