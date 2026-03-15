import React, {useState} from 'react'
import { useNavigate } from 'react-router-dom'

function ActionButtons({message, onActionResult}){
  const [loading, setLoading] = useState(false)
  if(!message) return null

  async function doAction(type){
    setLoading(true)
    try{
      const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null
      const res = await fetch(`/api/sms/${message.id}/${type}`, { method:'POST', headers:{'Content-Type':'application/json','X-Token': token}, body: JSON.stringify({}) })
      const result = await res.json()
      onActionResult(result, type)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex gap-3">
      <button onClick={()=>doAction('click')} disabled={loading} className="px-4 py-2 bg-emerald-600 text-white rounded-md">{loading? '...' : message.link_text || 'Open link'}</button>
      <button onClick={()=>doAction('report')} disabled={loading} className="px-4 py-2 bg-red-600 text-white rounded-md">Report as phishing</button>
    </div>
  )
}

export default function SmsView({message, onFeedback}){
  const [saved, setSaved] = useState(false)
  const [lastAction, setLastAction] = useState(null)
  const [lastResult, setLastResult] = useState(null)
  const [analysis, setAnalysis] = useState(null)
  const [analyzing, setAnalyzing] = useState(false)
  const [analysisError, setAnalysisError] = useState('')
  const navigate = useNavigate()

  React.useEffect(()=>{
    setAnalysis(null)
    setAnalysisError('')
  }, [message?.id])

  function handleActionResult(res, action){
    setSaved(true)
    setLastAction(action)
    setLastResult(res)
    if(onFeedback) onFeedback({item: message, result: res, action, channel: 'sms'})
    if(action === 'click'){
      if(message?.is_phishing){
        navigate('/phished', {state:{channel:'SMS', url: message.link_url}})
      }else{
        const target = `/safe-link?channel=SMS&url=${encodeURIComponent(message?.link_url || '')}`
        window.open(target, '_blank', 'noopener,noreferrer')
      }
    }
    setTimeout(()=>setSaved(false), 2000)
  }

  function openDirectLink(){
    if(!message) return
    if(message.is_phishing){
      navigate('/phished', {state:{channel:'SMS', url: message.link_url}})
      return
    }
    const target = `/safe-link?channel=SMS&url=${encodeURIComponent(message.link_url || '')}`
    window.open(target, '_blank', 'noopener,noreferrer')
  }

  async function runAnalysis(){
    if(!message?.id) return
    setAnalyzing(true)
    setAnalysisError('')
    try{
      const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null
      const res = await fetch('/api/detector/analyze-sms', {
        method: 'POST',
        headers: {'Content-Type':'application/json', 'X-Token': token},
        body: JSON.stringify({message_id: message.id}),
      })
      const json = await res.json()
      if(!res.ok){
        setAnalysisError(json?.error || 'Could not analyze this SMS right now.')
        return
      }
      setAnalysis(json)
    }catch(err){
      setAnalysisError('Could not analyze this SMS right now.')
    }finally{
      setAnalyzing(false)
    }
  }

  if(!message) return <div className="p-6 bg-white rounded-xl shadow">Select an SMS to view</div>

  return (
    <div className="p-6 bg-white rounded-xl shadow">
      <div className="flex items-start justify-between">
        <div>
          <h2 className="text-2xl font-bold">SMS from {message.sender}</h2>
          <p className="text-sm text-slate-500 mt-1">Short message simulation</p>
        </div>
        <div>
          <span className="px-3 py-1 rounded-full text-sm font-medium bg-emerald-100 text-emerald-800">{(message.difficulty || 'medium').toUpperCase()}</span>
        </div>
      </div>

      <div className="mt-4 p-4 bg-slate-50 rounded">
        <p className="whitespace-pre-wrap text-slate-700">{message.body}</p>
      </div>

      <div className="mt-4 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div className="flex flex-wrap gap-3">
          <ActionButtons message={message} onActionResult={handleActionResult} />
          <button onClick={runAnalysis} disabled={analyzing} className="px-4 py-2 bg-slate-900 text-white rounded-md disabled:opacity-60">
            {analyzing ? 'Analyzing...' : 'Analyze SMS'}
          </button>
        </div>
        <div className="text-sm text-slate-500">Link: <button onClick={openDirectLink} className="text-emerald-600 underline">{message.link_url}</button></div>
      </div>

      {analysisError && (
        <div className="mt-3 text-sm text-rose-700 bg-rose-50 border border-rose-200 rounded-lg p-3">{analysisError}</div>
      )}

      {analysis && (
        <div className="mt-4 rounded-xl border border-slate-200 bg-slate-50 p-4">
          <div className="flex items-center justify-between gap-3">
            <div>
              <div className="text-sm font-semibold text-slate-900">Detector verdict: <span className="uppercase">{analysis.verdict}</span></div>
              <div className="text-xs text-slate-500 mt-1">Risk score: {analysis.risk_score}/100</div>
            </div>
            <span className={"px-3 py-1 rounded-full text-xs font-semibold " + (analysis.verdict === 'phishing' ? 'bg-rose-100 text-rose-800' : analysis.verdict === 'suspicious' ? 'bg-amber-100 text-amber-800' : 'bg-emerald-100 text-emerald-800')}>
              {analysis.verdict}
            </span>
          </div>
          <div className="mt-3 h-2 rounded-full bg-slate-200 overflow-hidden">
            <div className={"h-full " + (analysis.risk_score >= 70 ? 'bg-rose-600' : analysis.risk_score >= 40 ? 'bg-amber-500' : 'bg-emerald-600')} style={{width: `${Math.max(0, Math.min(100, analysis.risk_score || 0))}%`}} />
          </div>
          <ul className="mt-3 list-disc ml-5 text-sm text-slate-700 space-y-1">
            {(analysis.reasons || []).map((reason, idx)=>(
              <li key={`sms-reason-${idx}`}>{reason}</li>
            ))}
          </ul>
        </div>
      )}

      {saved && (
        <div className="mt-3 text-sm text-emerald-600">Saved to feedback summary.</div>
      )}

      {lastResult && (
        <div className={"mt-4 rounded-xl border p-4 " + (lastResult.correct ? 'border-emerald-200 bg-emerald-50' : 'border-rose-200 bg-rose-50')}>
          <div className={"text-sm font-semibold " + (lastResult.correct ? 'text-emerald-800' : 'text-rose-800')}>
            {lastResult.correct ? 'Correct decision' : 'Needs improvement'}
          </div>
          <div className="text-sm text-slate-700 mt-1">Action: <span className="font-medium">{lastAction === 'click' ? 'Clicked link' : 'Reported as phishing'}</span></div>
          <div className="text-sm text-slate-700 mt-1">{lastResult.message}</div>
          {lastResult.tip && <div className="text-sm text-slate-600 mt-1">Clue: {lastResult.tip}</div>}
        </div>
      )}

      <div className="mt-6 border-t pt-4">
        <h3 className="mt-0 font-semibold">SMS Inspection Tips</h3>
        <ul className="list-disc ml-5 text-sm text-slate-700 mt-2">
          <li>Be suspicious of <strong>urgent warnings</strong> about accounts, deliveries, or SIM changes.</li>
          <li>Do not tap <strong>shortened or unknown links</strong>; go to the official app/site instead.</li>
          <li>Never share <strong>OTP codes, PINs, or bank details</strong> through SMS.</li>
          <li>Real providers will not ask for payment or personal data via a text link.</li>
          <li>If unsure, <strong>call the provider</strong> using a verified number.</li>
        </ul>
      </div>

    </div>
  )
}
