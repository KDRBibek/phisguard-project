import React, {useState} from 'react'
import { useNavigate } from 'react-router-dom'

function ActionButtons({email, onActionResult}){
  const [loading, setLoading] = useState(false)
  if(!email) return null

  async function postAction(type){
    setLoading(true)
    try{
      const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null
      const res = await fetch(`/api/emails/${email.id}/${type}`, { method: 'POST', headers: {'Content-Type':'application/json','X-Token': token}, body: JSON.stringify({}) })
      const json = await res.json()
      onActionResult(json, type)
    }catch(err){
      onActionResult({ correct: false, message: 'Network error', tip: '' }, type)
    }finally{ setLoading(false) }
  }

  return (
    <div className="flex gap-3">
      <button onClick={()=>postAction('click')} disabled={loading} className="px-4 py-2 bg-green-600 text-white rounded-md">{loading? '...' : email.link_text}</button>
      <button onClick={()=>postAction('report')} disabled={loading} className="px-4 py-2 bg-red-600 text-white rounded-md">Report as phishing</button>
    </div>
  )
}

export default function EmailView({email, onRefresh, onFeedback}){
  const [saved, setSaved] = useState(false)
  const navigate = useNavigate()

  function handleActionResult(res, action){
    setSaved(true)
    if(onFeedback) onFeedback({item: email, result: res, action, channel: 'email'})
    if(onRefresh) onRefresh()
    setTimeout(()=>setSaved(false), 2000)
  }

  if(!email) return <div className="p-6 bg-white rounded-xl shadow">Select an email to view</div>
  const role = typeof window !== 'undefined' ? localStorage.getItem('role') : null

  return (
    <div className="p-6 bg-white rounded-xl shadow">
      <div className="flex items-start justify-between">
        <div>
          <h2 className="text-2xl font-bold">{email.subject}</h2>
          <p className="text-sm text-slate-500 mt-1">From: <span className="font-medium">{email.sender}</span></p>
        </div>
        <div>
          {role === 'admin' ? (
            <div className="flex items-center gap-2">
              <span className={"px-3 py-1 rounded-full text-sm font-medium " + (email.is_phishing? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800') }>{email.is_phishing? 'Phishing' : 'Legitimate'}</span>
              <span className="px-3 py-1 rounded-full text-sm font-medium bg-indigo-100 text-indigo-700">{(email.difficulty || 'medium').toUpperCase()}</span>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <span className="px-3 py-1 rounded-full text-sm font-medium bg-slate-100 text-slate-500">Unknown</span>
              <span className="px-3 py-1 rounded-full text-sm font-medium bg-indigo-100 text-indigo-700">{(email.difficulty || 'medium').toUpperCase()}</span>
            </div>
          )}
        </div>
      </div>

      <div className="mt-4 p-4 bg-slate-50 rounded">
        <p className="whitespace-pre-wrap text-slate-700">{email.body}</p>
      </div>

      <div className="mt-4 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <ActionButtons email={email} onActionResult={handleActionResult} />
        <div className="text-sm text-slate-500">Link: <button onClick={()=>navigate('/phished', {state:{channel:'Email', url: email.link_url}})} className="text-indigo-600 underline">{email.link_url}</button></div>
      </div>

      {saved && (
        <div className="mt-3 text-sm text-emerald-600">Saved to feedback summary.</div>
      )}

      <div className="mt-6 border-t pt-4">
        <h3 className="mt-0 font-semibold">Email Inspection Tips</h3>
        <ul className="list-disc ml-5 text-sm text-slate-700 mt-2">
          <li>Check the <strong>sender domain</strong>: display names can be spoofed, domains cannot.</li>
          <li>Look for <strong>urgency or threats</strong> (lockouts, penalties, limited time).</li>
          <li>Verify the <strong>link destination</strong> by hovering; do not trust link text.</li>
          <li>Be cautious with <strong>requests for credentials</strong>, OTP codes, or payment updates.</li>
          <li>Check for <strong>odd formatting</strong>, missing signatures, or vague details.</li>
          <li>When unsure, <strong>go directly</strong> to the official site or contact the sender via trusted channels.</li>
        </ul>
      </div>

    </div>
  )
}
