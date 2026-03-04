import React from 'react'

export default function Feedback({feedbacks = []}){
  const total = feedbacks.length
  const correct = feedbacks.filter(item => item.correct).length
  const incorrect = total - correct
  const accuracy = total ? Math.round((correct / total) * 100) : 0

  function actionLabel(action){
    if(action === 'click') return 'You clicked the link'
    if(action === 'report') return 'You reported it as phishing'
    return `Action: ${action || 'unknown'}`
  }

  function channelLabel(channel){
    return (channel || 'email').toUpperCase()
  }

  return (
    <div className="max-w-5xl mx-auto p-6">
      <div className="bg-white rounded-2xl shadow-lg border p-6">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-semibold">Your Results</h2>
          <div className="text-sm text-slate-500">{total} total</div>
        </div>

        <p className="mt-2 text-sm text-slate-600">This page shows what you did, what was right or wrong, and how to improve next time.</p>

        <div className="mt-5 grid grid-cols-1 sm:grid-cols-3 gap-3">
          <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-4">
            <div className="text-xs uppercase tracking-wide text-emerald-700">Correct</div>
            <div className="mt-1 text-2xl font-semibold text-emerald-900">{correct}</div>
          </div>
          <div className="rounded-xl border border-rose-200 bg-rose-50 p-4">
            <div className="text-xs uppercase tracking-wide text-rose-700">Needs Work</div>
            <div className="mt-1 text-2xl font-semibold text-rose-900">{incorrect}</div>
          </div>
          <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
            <div className="text-xs uppercase tracking-wide text-slate-600">Accuracy</div>
            <div className="mt-1 text-2xl font-semibold text-slate-900">{accuracy}%</div>
          </div>
        </div>

        {total === 0 && (
          <div className="mt-6 rounded-xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-600">
            No results yet. Open Simulation, check a message, then click or report to see feedback here.
          </div>
        )}

        {total > 0 && (
          <div className="mt-6 space-y-4">
            {feedbacks.map(item => (
              <div key={`${item.channel || 'email'}-${item.item_id || item.email_id}`} className="border rounded-xl p-4 bg-white">
                <div className="flex items-start justify-between">
                  <div>
                    <div className="font-semibold text-slate-900">{item.subject}</div>
                    <div className="text-xs text-slate-500 mt-1">From {item.sender}</div>
                  </div>
                  <span className={"px-2 py-1 rounded-full text-xs font-medium " + (item.correct ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800')}>
                    {item.correct ? 'Correct decision' : 'Wrong decision'}
                  </span>
                </div>

                <div className="mt-3 text-sm text-slate-700">
                  <span className="font-medium">What you did:</span> {actionLabel(item.action)}
                </div>
                <div className="mt-1 text-sm text-slate-700">
                  <span className="font-medium">Result:</span> {item.message}
                </div>

                {item.tip && (
                  <div className="mt-3 rounded-lg bg-amber-50 border border-amber-200 p-3 text-sm text-amber-900">
                    <span className="font-medium">How to spot it:</span> {item.tip}
                  </div>
                )}

                <div className="mt-3 text-xs text-slate-500">{channelLabel(item.channel)} • {new Date(item.created_at).toLocaleString()}</div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
