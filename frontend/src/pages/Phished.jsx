import React from 'react'
import { useNavigate } from 'react-router-dom'
import phishedImage from '../assets/you-been-phished.jpg'

export default function Phished(){
  const navigate = useNavigate()

  return (
    <div className="min-h-[70vh] flex items-center justify-center p-6">
      <div className="w-full max-w-3xl rounded-2xl shadow-xl border bg-white overflow-hidden">
        <img
          src={phishedImage}
          alt="You have been phished"
          className="w-full h-auto object-cover"
        />

        <div className="p-6 sm:p-8">
          <div className="flex flex-wrap gap-3 justify-center">
            <button onClick={()=>navigate('/simulation')} className="px-4 py-2 rounded-full bg-slate-900 text-white">Back to Simulation</button>
            <button onClick={()=>navigate('/awareness')} className="px-4 py-2 rounded-full bg-slate-100 text-slate-700">Open Awareness</button>
          </div>
        </div>
      </div>
    </div>
  )
}
