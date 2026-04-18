import React from 'react'

function Item({email, onClick, selected}){
  return (
    <div onClick={()=>onClick(email)} className={"p-3 rounded-md cursor-pointer transition-colors " + (selected? 'bg-white shadow' : 'hover:bg-white') }>
      <div className="flex items-center justify-between">
        <div>
          <div className="font-semibold">{email.sender}</div>
          <div className="text-sm text-slate-600">{email.subject}</div>
        </div>
        <div className="text-xs text-slate-400">{email.is_phishing? 'Phish' : 'Legit'}</div>
      </div>
    </div>
  )
}

export default function EmailList({emails, onSelect, selectedId}){
  return (
    <div className="space-y-3">
      <div className="px-4 py-3 rounded-md bg-gradient-to-r from-slate-950 to-slate-800 text-white font-semibold">Inbox</div>
      <div className="space-y-2 mt-3">
        {emails.length === 0 && (
          <div className="p-3 text-sm text-slate-500">No emails available.</div>
        )}
        {emails.map(e=> (
          <div key={e.id}>
            <button
              onClick={()=>onSelect(e)}
              className={"w-full text-left p-3 rounded-lg transition-shadow flex items-start gap-3 " + (selectedId===e.id? 'bg-white shadow' : 'hover:shadow-md')}
            >
              <div className="w-10 h-10 rounded-full bg-slate-200 flex items-center justify-center text-slate-800 font-semibold">{(e.sender||'')[0]}</div>
              <div className="flex-1">
                <div className="flex items-center justify-between">
                  <div className="font-medium">{e.sender}</div>
                    <div className="text-xs text-slate-700 font-semibold">{(e.difficulty || 'medium').toUpperCase()}</div>
                </div>
                <div className="text-sm text-slate-600">{e.subject}</div>
              </div>
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}
