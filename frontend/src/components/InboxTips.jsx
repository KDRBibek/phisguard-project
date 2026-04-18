import React, {useState} from 'react'

const TIPS = [
  {
    id: 'sender',
    title: 'Check the sender',
    description: 'Verify the sender address and look for mismatched domains or unexpected names.',
    icon: (
      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none"><path d="M12 2v6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/><path d="M6.2 7.5l1.6 1.6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/><path d="M2 12h6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/><path d="M7.8 16.5l1.6-1.6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/><path d="M12 22v-6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg>
    )
  },
  {
    id: 'urgency',
    title: 'Watch for urgency',
    description: 'Be cautious with messages that pressure you to act immediately — it is a common phishing tactic.',
    icon: (
      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none"><path d="M12 8v4l3 3" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/><path d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg>
    )
  },
  {
    id: 'credentials',
    title: 'Protect credentials',
    description: 'Never enter passwords, OTPs, or bank details from an email link — always use official sites.',
    icon: (
      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none"><path d="M3 7h18" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/><path d="M7 11h10" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/><path d="M10 15h4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg>
    )
  }
]

export default function InboxTips(){
  const [activeId, setActiveId] = useState(TIPS[0].id)
  const activeTip = TIPS.find(t=>t.id===activeId) || TIPS[0]
  return (
    <div className="p-4 bg-white rounded-xl shadow-sm">
      <div className="flex items-center justify-between">
        <h3 className="text-md font-semibold">Inbox Tips</h3>
        <span className="text-xs text-slate-500">Quick guide</span>
      </div>

      <div className="mt-4 grid grid-cols-1 sm:grid-cols-[160px_1fr] gap-4">
        <div className="flex sm:flex-col gap-2 overflow-auto">
          {TIPS.map(tip => (
            <button
              key={tip.id}
              onClick={()=>setActiveId(tip.id)}
              className={"text-left px-3 py-2 rounded-lg text-sm border transition " + (activeId===tip.id ? 'bg-slate-900 border-slate-900 text-white' : 'bg-white border-slate-200 text-slate-600 hover:bg-slate-50')}
            >
              {tip.title}
            </button>
          ))}
        </div>

        <div className="p-4 border rounded-lg bg-slate-50">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-white text-slate-900 flex items-center justify-center">{activeTip.icon}</div>
            <div className="font-medium">{activeTip.title}</div>
          </div>
          <div className="mt-2 text-sm text-slate-600">{activeTip.description}</div>
        </div>
      </div>

      <div className="mt-4 pt-3 border-t text-sm text-slate-500">This is a safe simulation — take your time and learn.</div>
    </div>
  )
}
