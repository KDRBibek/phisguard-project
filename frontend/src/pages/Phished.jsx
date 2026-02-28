import React from 'react'
import { useLocation, useNavigate } from 'react-router-dom'

export default function Phished(){
  const navigate = useNavigate()
  const location = useLocation()
  const state = location.state || {}
  const channel = state.channel || 'Message'
  const url = state.url || ''

  return (
    <div className="min-h-[70vh] flex items-center justify-center p-6">
      <div className="w-full max-w-3xl rounded-2xl shadow-xl border bg-white overflow-hidden">
        <div className="p-8 bg-gradient-to-r from-rose-500 to-orange-400 text-white relative">
          <div className="absolute -right-6 -top-6 w-28 h-28 rounded-full bg-white/20" />
          <div className="absolute -left-10 -bottom-10 w-32 h-32 rounded-full bg-white/15" />
          <h1 className="text-3xl font-bold">You got phished</h1>
          <p className="mt-2 text-white/90">That link led to a simulated trap. In real life, this could steal credentials or money.</p>
        </div>

        <div className="p-6 sm:p-8 space-y-6">
          <div className="rounded-xl border border-rose-200 bg-rose-50 p-4">
            <div className="text-sm text-rose-700">Channel: {channel}</div>
            {url && <div className="text-xs text-rose-700 break-all mt-1">Link: {url}</div>}
          </div>

          <div>
            <h2 className="text-lg font-semibold">Why this was risky</h2>
            <ul className="list-disc ml-5 text-sm text-slate-700 mt-2 space-y-1">
              <li>Urgency or threat to push fast action.</li>
              <li>Look-alike domains that mimic trusted services.</li>
              <li>Requests for passwords, OTPs, or payment details.</li>
            </ul>
          </div>

          <div>
            <h2 className="text-lg font-semibold">What to do next</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-2">
              <div className="border rounded-xl p-4 bg-slate-50">
                <div className="font-medium">Pause and verify</div>
                <div className="text-sm text-slate-600 mt-1">Open the official site or app directly.</div>
              </div>
              <div className="border rounded-xl p-4 bg-slate-50">
                <div className="font-medium">Report it</div>
                <div className="text-sm text-slate-600 mt-1">Use the Report button in the simulation.</div>
              </div>
            </div>
          </div>

          <div className="flex flex-wrap gap-3">
            <button onClick={()=>navigate('/simulation')} className="px-4 py-2 rounded-full bg-indigo-600 text-white">Back to Simulation</button>
            <button onClick={()=>navigate('/awareness')} className="px-4 py-2 rounded-full bg-slate-100 text-slate-700">Open Awareness</button>
          </div>
        </div>
      </div>
    </div>
  )
}
