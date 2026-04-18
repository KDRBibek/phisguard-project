import React from 'react'

export default function ConfirmModal({open, title, message, onConfirm, onCancel}){
  if(!open) return null
  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-lg p-6 w-full max-w-md">
        <h3 className="text-lg font-semibold">{title || 'Confirm'}</h3>
        <p className="mt-2 text-sm text-slate-600">{message || 'Are you sure?'}</p>
        <div className="mt-4 flex justify-end gap-2">
          <button onClick={onCancel} className="px-3 py-2 rounded bg-slate-100">Cancel</button>
          <button onClick={onConfirm} className="px-3 py-2 rounded bg-red-600 text-white">Confirm</button>
        </div>
      </div>
    </div>
  )
}
