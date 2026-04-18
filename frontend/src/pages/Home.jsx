import React from 'react'
import { useNavigate } from 'react-router-dom'
import homeBg from '../assets/phisguard image.png'

export default function Home(){
  const navigate = useNavigate()

  return (
    <div
      className="relative left-1/2 right-1/2 -translate-x-1/2 w-screen min-h-screen flex items-center justify-center px-6 py-10 bg-cover bg-center bg-no-repeat"
      style={{
        backgroundImage: `linear-gradient(rgba(8,10,14,0.58), rgba(8,10,14,0.58)), url(${homeBg})`
      }}
    >
      <div className="w-full max-w-4xl rounded-3xl border border-amber-200/30 bg-slate-950/55 backdrop-blur-md shadow-[0_24px_80px_-32px_rgba(0,0,0,0.9)] overflow-hidden">
        <div className="p-10 sm:p-14 text-center bg-gradient-to-br from-amber-300/10 via-transparent to-orange-300/10">
          <div className="mx-auto w-16 h-16 rounded-full border border-amber-200/40 bg-amber-100/20 flex items-center justify-center">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M3 12h18" stroke="#fde68a" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"/><path d="M7 6h10" stroke="#fde68a" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"/><path d="M7 18h10" stroke="#fde68a" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"/></svg>
          </div>
          <h1 className="mt-5 text-4xl sm:text-6xl font-semibold tracking-[0.06em] text-amber-50">PHISGUARD</h1>
          <p className="mt-4 max-w-2xl mx-auto text-amber-100/90 text-lg">Phishing awareness training in a safe, controlled environment.</p>
          <button onClick={()=>navigate('/simulation')} className="mt-8 px-8 py-3 rounded-full bg-amber-300 text-slate-950 font-semibold hover:bg-amber-200 transition-colors">Start Simulation</button>
        </div>
      </div>
    </div>
  )
}
