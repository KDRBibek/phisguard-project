import React from 'react'

export default function FeedbackModal({open, onClose, result}){
  if(!open) return null
  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50" role="dialog" aria-modal="true">
      <div className="bg-white rounded-md p-6 max-w-lg w-full shadow-lg">
        <div className="flex justify-between items-start">
          <h3 className="text-lg font-semibold">{result?.correct ? 'Good choice' : 'Be careful'}</h3>
          <button onClick={onClose} className="text-slate-500 hover:text-slate-700" aria-label="Close">✕</button>
        </div>
        <p className="mt-3 text-slate-700">{result?.message}</p>
        <div className="mt-4 p-3 bg-slate-50 rounded">{result?.tip}</div>

        <h4 className="mt-4 font-semibold">Remember</h4>
        <ul className="list-disc ml-5 text-sm text-slate-700">
          <li>Never enter credentials from a link in an unexpected email.</li>
          <li>Verify requests using the official website or trusted contact method.</li>
          <li>Urgency + link + personal info request = common phishing pattern.</li>
        </ul>

        <div className="mt-4 text-right">
          <button onClick={onClose} className="px-4 py-2 bg-slate-900 text-white rounded hover:bg-slate-800">OK</button>
        </div>
      </div>
    </div>
  )
}
