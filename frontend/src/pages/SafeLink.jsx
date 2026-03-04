import React from 'react'
import { useLocation, useNavigate } from 'react-router-dom'

export default function SafeLink(){
  const navigate = useNavigate()
  const location = useLocation()
  const params = new URLSearchParams(location.search)
  const channel = params.get('channel') || 'Message'
  const url = params.get('url') || ''

  return (
    <div className="min-h-[70vh] flex items-center justify-center p-6">
      <div className="w-full max-w-3xl rounded-2xl shadow-xl border bg-white overflow-hidden">
        <div className="p-8 bg-gradient-to-r from-emerald-500 to-teal-500 text-white relative">
          <div className="absolute -right-6 -top-6 w-28 h-28 rounded-full bg-white/20" />
          <div className="absolute -left-10 -bottom-10 w-32 h-32 rounded-full bg-white/15" />
          <h1 className="text-3xl font-bold">Good link confirmed</h1>
          <p className="mt-2 text-white/90">Nice work. This is a legitimate simulation link and your decision was correct.</p>
        </div>

        <div className="p-6 sm:p-8 space-y-6">
          <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-4">
            <div className="text-sm text-emerald-700">Channel: {channel}</div>
            {url && <div className="text-xs text-emerald-700 break-all mt-1">Link: {url}</div>}
          </div>

          <div>
            <h2 className="text-lg font-semibold">Why this looked safe</h2>
            <ul className="list-disc ml-5 text-sm text-slate-700 mt-2 space-y-1">
              <li>No pressure or threat language.</li>
              <li>Expected sender and normal context.</li>
              <li>No request for passwords, OTPs, or payment details.</li>
            </ul>
          </div>

          <div className="flex flex-wrap gap-3">
            <button onClick={()=>navigate('/simulation')} className="px-4 py-2 rounded-full bg-slate-900 text-white">Back to Simulation</button>
            <button onClick={()=>navigate('/awareness')} className="px-4 py-2 rounded-full bg-slate-100 text-slate-700">Open Awareness</button>
          </div>
        </div>
      </div>
    </div>
  )
}
