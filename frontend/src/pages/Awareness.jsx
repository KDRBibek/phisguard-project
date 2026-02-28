import React from 'react'

const sections = [
	{ id: 'intro', title: 'Phishing Awareness Quick Guide' },
	{ id: 'stop-check-verify', title: 'Stop Check Verify Report' },
	{ id: 'red-flags', title: 'Common Red Flags' },
	{ id: 'what-to-do', title: 'What Should I Do' },
	{ id: 'if-clicked', title: 'If You Clicked' },
	{ id: 'self-check', title: 'Quick Self Check' }
]

export default function Awareness(){
	return (
		<div className="max-w-5xl mx-auto p-6">
			<div className="bg-white rounded-2xl shadow-lg overflow-hidden">
				<div className="p-8 bg-gradient-to-r from-amber-500 to-rose-500 text-white relative">
					<div className="absolute -right-8 -top-8 w-32 h-32 rounded-full bg-white/15" />
					<div className="absolute -left-12 -bottom-12 w-40 h-40 rounded-full bg-white/10" />
					<h2 className="text-3xl font-bold" style={{fontFamily: 'Comic Sans MS, Trebuchet MS, sans-serif'}}>Phishing Awareness</h2>
					<p className="mt-2 opacity-90">Use this guide before you click links or share information.</p>
				</div>

				<div className="p-6 sm:p-10 grid grid-cols-1 lg:grid-cols-[220px_1fr] gap-6">
					<aside className="lg:sticky lg:top-6 self-start">
						<div className="border rounded-xl p-4 bg-slate-50" style={{fontFamily: 'Comic Sans MS, Trebuchet MS, sans-serif'}}>
							<div className="text-sm font-semibold mb-3">Awareness Navigation</div>
							<nav className="flex flex-col gap-2">
								{sections.map(s => (
									<a key={s.id} href={`#${s.id}`} className="text-sm px-3 py-2 rounded-lg border bg-white hover:bg-slate-50 text-slate-700">
										{s.title}
									</a>
								))}
							</nav>
						</div>
					</aside>

					<section className="space-y-8">
						<div id="intro">
							<h3 className="text-xl font-semibold flex items-center gap-2" style={{fontFamily: 'Comic Sans MS, Trebuchet MS, sans-serif'}}>
								<span className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-amber-100">🔎</span>
								Phishing Awareness Quick Guide
							</h3>
							<p className="mt-2 text-slate-600">
								Phishing is when attackers pretend to be a trusted person or service to trick you into clicking links,
								sharing passwords, or sending money. Use this checklist before you click.
							</p>
						</div>

						<div id="stop-check-verify">
							<h3 className="text-xl font-semibold flex items-center gap-2" style={{fontFamily: 'Comic Sans MS, Trebuchet MS, sans-serif'}}>
								<span className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-rose-100">🛑</span>
								Stop Check Verify Report
							</h3>
							<div className="mt-3 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
								<div className="border rounded-xl p-4">
									<div className="font-semibold">STOP</div>
									<p className="text-sm text-slate-600 mt-1">Do not rush. Phishing relies on panic and urgency.</p>
								</div>
								<div className="border rounded-xl p-4">
									<div className="font-semibold">CHECK</div>
									<p className="text-sm text-slate-600 mt-1">Look at the sender, link domain, and what is being asked.</p>
								</div>
								<div className="border rounded-xl p-4">
									<div className="font-semibold">VERIFY</div>
									<p className="text-sm text-slate-600 mt-1">Use the official portal or app directly, not the message link.</p>
								</div>
								<div className="border rounded-xl p-4">
									<div className="font-semibold">REPORT</div>
									<p className="text-sm text-slate-600 mt-1">Report suspicious messages so others are protected.</p>
								</div>
							</div>
						</div>

						<div id="red-flags">
							<h3 className="text-xl font-semibold flex items-center gap-2" style={{fontFamily: 'Comic Sans MS, Trebuchet MS, sans-serif'}}>
								<span className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-amber-100">🚩</span>
								Common Red Flags
							</h3>
							<div className="mt-3 grid grid-cols-1 sm:grid-cols-2 gap-3">
								<div className="border rounded-xl p-4 bg-slate-50">
									<div className="font-semibold">Urgency or threats</div>
									<p className="text-sm text-slate-600 mt-1">Act now, account will be suspended, pay today.</p>
								</div>
								<div className="border rounded-xl p-4 bg-slate-50">
									<div className="font-semibold">Weird sender or domain</div>
									<p className="text-sm text-slate-600 mt-1">Name looks right but the email or URL domain is wrong.</p>
								</div>
								<div className="border rounded-xl p-4 bg-slate-50">
									<div className="font-semibold">Sensitive info requests</div>
									<p className="text-sm text-slate-600 mt-1">Passwords, OTP codes, bank details, confirm login.</p>
								</div>
								<div className="border rounded-xl p-4 bg-slate-50">
									<div className="font-semibold">Unexpected attachment</div>
									<p className="text-sm text-slate-600 mt-1">Invoice or document you were not expecting.</p>
								</div>
								<div className="border rounded-xl p-4 bg-slate-50">
									<div className="font-semibold">Generic greeting</div>
									<p className="text-sm text-slate-600 mt-1">Dear user instead of your real name.</p>
								</div>
								<div className="border rounded-xl p-4 bg-slate-50">
									<div className="font-semibold">Too good to be true</div>
									<p className="text-sm text-slate-600 mt-1">Prize, scholarship, or free money out of nowhere.</p>
								</div>
							</div>
						</div>

						<div id="what-to-do">
							<h3 className="text-xl font-semibold flex items-center gap-2" style={{fontFamily: 'Comic Sans MS, Trebuchet MS, sans-serif'}}>
								<span className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-emerald-100">🧭</span>
								What Should I Do
							</h3>
							<div className="mt-3 border rounded-xl p-4">
								<ul className="list-disc ml-5 text-sm text-slate-700 space-y-2">
									<li><strong>If it asks you to log in:</strong> close it and open the official portal or app yourself.</li>
									<li><strong>If it is about payments or fees:</strong> check through the official finance portal, not the link.</li>
									<li><strong>If it is about deliveries:</strong> track using the courier app or website you already trust.</li>
									<li><strong>If it asks for OTP:</strong> never share OTP with anyone, not even support.</li>
								</ul>
							</div>
						</div>

						<div id="if-clicked">
							<h3 className="text-xl font-semibold flex items-center gap-2" style={{fontFamily: 'Comic Sans MS, Trebuchet MS, sans-serif'}}>
								<span className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-rose-100">🚑</span>
								If You Clicked a Suspicious Link
							</h3>
							<div className="mt-3 border rounded-xl p-4 bg-rose-50">
								<ol className="list-decimal ml-5 text-sm text-slate-700 space-y-2">
									<li><strong>Disconnect</strong> by closing the tab or app.</li>
									<li><strong>Change your password</strong> using the official portal or app.</li>
									<li><strong>Enable MFA</strong> if available.</li>
									<li><strong>Report it</strong> to your IT or admin team.</li>
								</ol>
								<p className="mt-3 text-xs text-slate-600">Tip: If you reused the same password elsewhere, change it there too.</p>
							</div>
						</div>

						<div id="self-check">
							<h3 className="text-xl font-semibold flex items-center gap-2" style={{fontFamily: 'Comic Sans MS, Trebuchet MS, sans-serif'}}>
								<span className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-indigo-100">🎯</span>
								Quick Self Check
							</h3>
							<div className="mt-3 grid grid-cols-1 sm:grid-cols-2 gap-3">
								<div className="border rounded-xl p-4">
									<div className="font-semibold">Q1: Does the domain exactly match the official service?</div>
									<p className="text-sm text-slate-600 mt-1">If no, do not click. Verify first.</p>
								</div>
								<div className="border rounded-xl p-4">
									<div className="font-semibold">Q2: Is it asking for password, OTP, or bank info?</div>
									<p className="text-sm text-slate-600 mt-1">If yes, it is likely phishing.</p>
								</div>
								<div className="border rounded-xl p-4">
									<div className="font-semibold">Q3: Is it urgent, threatening, or pressuring?</div>
									<p className="text-sm text-slate-600 mt-1">If yes, stop and verify through official channels.</p>
								</div>
							</div>
						</div>
					</section>
				</div>
			</div>
		</div>
	)
}
