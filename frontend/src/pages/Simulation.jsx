import React from 'react'

export default function Simulation({emails = [], smsMessages = [], feedbacks = [], attemptedEmailIds = [], attemptedSmsIds = []}){
  const totalEmails = emails.length
  const totalSms = smsMessages.length
  const attemptedEmails = attemptedEmailIds.length
  const attemptedSms = attemptedSmsIds.length
  const completedAll = totalEmails > 0 && totalSms > 0 && attemptedEmails >= totalEmails && attemptedSms >= totalSms

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
        <div className="p-8 bg-gradient-to-r from-slate-950 to-slate-800 text-white">
          <h2 className="text-3xl font-bold">Welcome to PhisGuard</h2>
          <p className="mt-2 opacity-90">An interactive simulation to improve phishing detection and response.</p>
        </div>

        <div className="p-6 sm:p-10">
          <p className="text-slate-700">PhisGuard helps users recognize common phishing patterns. You'll practice with simulated emails and SMS in the Simulation inbox, inspect links, and get feedback to learn safe habits.</p>

          <div className="mt-6 grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="p-4 border rounded-lg">
              <h4 className="font-semibold">Practice</h4>
              <p className="text-sm text-slate-600 mt-2">Interact with simulated emails and learn by doing.</p>
            </div>
            <div className="p-4 border rounded-lg">
              <h4 className="font-semibold">Learn</h4>
              <p className="text-sm text-slate-600 mt-2">Get concise feedback explaining why a message is suspicious.</p>
            </div>
            <div className="p-4 border rounded-lg">
              <h4 className="font-semibold">Measure</h4>
              <p className="text-sm text-slate-600 mt-2">Admin can create scenarios and view metrics to track progress.</p>
            </div>
          </div>

          <h3 className="mt-8 text-lg font-semibold">How to use</h3>
          <ol className="list-decimal ml-6 mt-2 text-slate-700">
            <li>Open the <strong>Simulation</strong> inbox to review simulated emails and SMS.</li>
            <li>Click a link to test whether it's phishing (you'll receive feedback).</li>
            <li>Use <strong>Report</strong> when you suspect phishing to practice safe behaviour.</li>
          </ol>

          <p className="mt-6 text-slate-600">Tip: Treat simulations like real messages — pause, inspect, and validate before acting.</p>
        </div>
      </div>

      <div className="mt-8 bg-white rounded-2xl shadow-lg p-6">
          <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold">Feedback Summary</h3>
            <div className="text-sm text-slate-500">Emails: {attemptedEmails}/{totalEmails} • SMS: {attemptedSms}/{totalSms}</div>
        </div>

        {!completedAll && (
          <div className="mt-4 p-4 rounded-lg bg-slate-50 text-slate-600 text-sm">
            Complete all emails and SMS in the Simulation inbox to unlock your feedback summary.
          </div>
        )}

        {completedAll && (
          <div className="mt-4 space-y-4">
            {feedbacks.length === 0 && (
              <div className="text-sm text-slate-500">No feedback yet.</div>
            )}
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
                <div className="mt-2 text-xs text-slate-400">
                  {(item.channel || 'email').toUpperCase()} • Action: {item.action}
                  {typeof item.time_to_action_seconds === 'number' && (
                    <> • Time to action: {item.time_to_action_seconds.toFixed(1)}s</>
                  )}
                  {' '}• {new Date(item.created_at).toLocaleString()}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
