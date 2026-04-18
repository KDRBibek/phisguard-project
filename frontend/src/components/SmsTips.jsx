import React, {useState} from 'react'

const TIPS = [
  {
    id: 'shortlinks',
    title: 'Short links',
    description: 'Be cautious with shortened or unfamiliar links. Verify by typing the official site directly.',
  },
  {
    id: 'urgency',
    title: 'Urgency and prizes',
    description: 'Messages that pressure you or promise rewards are common SMS phishing tactics.',
  },
  {
    id: 'personalinfo',
    title: 'Sensitive info',
    description: 'Never share passwords, OTPs, or bank details via SMS links or replies.',
  }
]

export default function SmsTips(){
  const [activeId, setActiveId] = useState(TIPS[0].id)
  const activeTip = TIPS.find(t=>t.id===activeId) || TIPS[0]

  return (
    <div className="p-4 bg-white rounded-xl shadow-sm">
      <div className="flex items-center justify-between">
        <h3 className="text-md font-semibold">SMS Tips</h3>
        <span className="text-xs text-slate-500">Quick guide</span>
      </div>

      <div className="mt-4 grid grid-cols-1 sm:grid-cols-[160px_1fr] gap-4">
        <div className="flex sm:flex-col gap-2 overflow-auto">
          {TIPS.map(tip => (
            <button
              key={tip.id}
              onClick={()=>setActiveId(tip.id)}
              className={"text-left px-3 py-2 rounded-lg text-sm border transition " + (activeId===tip.id ? 'bg-emerald-50 border-emerald-200 text-emerald-700' : 'bg-white border-slate-200 text-slate-600 hover:bg-slate-50')}
            >
              {tip.title}
            </button>
          ))}
        </div>

        <div className="p-4 border rounded-lg bg-slate-50">
          <div className="font-medium">{activeTip.title}</div>
          <div className="mt-2 text-sm text-slate-600">{activeTip.description}</div>
        </div>
      </div>

      <div className="mt-4 pt-3 border-t text-sm text-slate-500">Treat SMS links as untrusted unless verified.</div>
    </div>
  )
}
