import React from 'react'

export default function SmsList({messages, onSelect, selectedId}){
  return (
    <div className="space-y-3">
      <div className="px-4 py-3 rounded-md bg-gradient-to-r from-emerald-600 to-emerald-500 text-white font-semibold">SMS Inbox</div>
      <div className="space-y-2 mt-3">
        {messages.length === 0 && (
          <div className="p-3 text-sm text-slate-500">No messages available.</div>
        )}
        {messages.map(m=> (
          <div key={m.id}>
            <button
              onClick={()=>onSelect(m)}
              className={"w-full text-left p-3 rounded-lg transition-shadow flex items-start gap-3 " + (selectedId===m.id? 'bg-white shadow' : 'hover:shadow-md')}
            >
              <div className="w-10 h-10 rounded-full bg-emerald-100 flex items-center justify-center text-emerald-600 font-semibold">{(m.sender||'')[0]}</div>
              <div className="flex-1">
                <div className="flex items-center justify-between">
                  <div className="font-medium">{m.sender}</div>
                  <div className="text-xs text-emerald-600 font-semibold">{(m.difficulty || 'medium').toUpperCase()}</div>
                </div>
                <div className="text-sm text-slate-600">{m.body}</div>
              </div>
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}
