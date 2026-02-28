import React from 'react'

export default function Feedback({feedbacks = []}){
  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="bg-white rounded-2xl shadow-lg p-6">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-semibold">My Feedback</h2>
          <div className="text-sm text-slate-500">{feedbacks.length} item(s)</div>
        </div>

        {feedbacks.length === 0 && (
          <div className="mt-6 text-sm text-slate-500">
            No feedback yet. Interact with emails in the Inbox to generate results.
          </div>
        )}

        {feedbacks.length > 0 && (
          <div className="mt-6 space-y-4">
            {feedbacks.map(item => (
              <div key={`${item.channel || 'email'}-${item.item_id || item.email_id}`} className="border rounded-lg p-4">
                <div className="flex items-start justify-between">
                  <div>
                    <div className="font-semibold">{item.subject}</div>
                    <div className="text-xs text-slate-500">From {item.sender}</div>
                  </div>
                  <span className={"px-2 py-1 rounded-full text-xs font-medium " + (item.correct ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800')}>
                    {item.correct ? 'Correct' : 'Incorrect'}
                  </span>
                </div>
                <div className="mt-2 text-sm text-slate-700">{item.message}</div>
                {item.tip && <div className="mt-2 text-xs text-slate-500">Tip: {item.tip}</div>}
                <div className="mt-2 text-xs text-slate-400">{(item.channel || 'email').toUpperCase()} • Action: {item.action} • {new Date(item.created_at).toLocaleString()}</div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
