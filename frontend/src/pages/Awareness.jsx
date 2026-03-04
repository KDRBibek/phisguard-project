import React from 'react'

const sections = [
	{ id: 'intro', title: 'Before You Act' },
	{ id: 'stop-check-verify', title: 'Pause, Check, Verify, Report' },
	{ id: 'red-flags', title: 'Indicators To Watch' },
	{ id: 'what-to-do', title: 'Recommended Next Steps' },
	{ id: 'if-clicked', title: 'If You Already Clicked' },
	{ id: 'self-check', title: 'Brief Self Check' }
]

export default function Awareness(){
	return (
		<div className="awareness-shell min-h-screen px-4 py-10 sm:px-10">
			<div className="max-w-6xl mx-auto">
				<div className="awareness-card rounded-3xl overflow-hidden">
					<div className="relative p-8 sm:p-12">
						<div className="absolute -right-16 -top-16 h-48 w-48 rounded-full bg-emerald-300/10" />
						<div className="absolute -left-20 -bottom-20 h-56 w-56 rounded-full bg-rose-300/10" />
						<div className="relative">
							<p className="font-body uppercase tracking-[0.35em] text-xs awareness-subtle">Phishing Awareness</p>
							<h2 className="font-display text-3xl sm:text-5xl text-slate-100 mt-3">
								Maintain vigilance and control.
							</h2>
							<p className="font-body mt-4 max-w-2xl awareness-subtle">
								Phishing attempts often rely on urgency and uncertainty. If a message appears rushed, pause and
								confirm using the official application or portal. This page provides a concise reference checklist.
							</p>
							<div className="mt-6 flex flex-wrap gap-3 font-body text-sm">
								<span className="awareness-chip rounded-full px-4 py-2">Pause before responding</span>
								<span className="awareness-chip rounded-full px-4 py-2">Verify using the official app</span>
								<span className="awareness-chip rounded-full px-4 py-2">Report promptly</span>
							</div>
						</div>
					</div>

					<div className="px-6 pb-10 sm:px-10 grid grid-cols-1 lg:grid-cols-[240px_1fr] gap-8">
						<aside className="lg:sticky lg:top-6 self-start">
							<div className="awareness-panel rounded-2xl p-4">
								<div className="font-body text-xs uppercase tracking-[0.28em] awareness-subtle mb-4">On this page</div>
								<nav className="flex flex-col gap-2 font-body">
									{sections.map(s => (
										<a key={s.id} href={`#${s.id}`} className="text-sm px-3 py-2 rounded-xl border border-transparent bg-slate-900/40 hover:border-emerald-200/40 hover:bg-slate-900/60 text-slate-200 transition">
											{s.title}
										</a>
									))}
								</nav>
							</div>
						</aside>

						<section className="space-y-10">
							<div id="intro">
								<h3 className="font-display text-2xl text-slate-100">Before you respond</h3>
								<p className="font-body mt-3 awareness-subtle">
									If a message demands speed, secrecy, or payment, stop. Legitimate services allow time to confirm.
									Close the message and go directly to the official app or site.
								</p>
							</div>

							<div id="stop-check-verify">
								<h3 className="font-display text-2xl text-slate-100">Pause, Check, Verify, Report</h3>
								<div className="mt-4 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 font-body">
										<div className="awareness-panel rounded-2xl p-4">
											<div className="font-semibold text-slate-100">PAUSE</div>
											<p className="text-sm awareness-subtle mt-2">Pause briefly. Urgency is a common tactic.</p>
										</div>
										<div className="awareness-panel rounded-2xl p-4">
											<div className="font-semibold text-slate-100">CHECK</div>
											<p className="text-sm awareness-subtle mt-2">Review the sender, the domain, and the request.</p>
										</div>
										<div className="awareness-panel rounded-2xl p-4">
											<div className="font-semibold text-slate-100">VERIFY</div>
											<p className="text-sm awareness-subtle mt-2">Use the official app or trusted portal.</p>
										</div>
										<div className="awareness-panel rounded-2xl p-4">
											<div className="font-semibold text-slate-100">REPORT</div>
											<p className="text-sm awareness-subtle mt-2">Notify IT or the designated administrative team.</p>
										</div>
								</div>
							</div>

							<div id="red-flags">
								<h3 className="font-display text-2xl text-slate-100">Indicators to observe</h3>
								<div className="mt-4 grid grid-cols-1 sm:grid-cols-2 gap-3 font-body">
										<div className="awareness-panel rounded-2xl p-4">
											<div className="font-semibold text-slate-100">High-pressure language</div>
											<p className="text-sm awareness-subtle mt-2">Phrases like "act now" or "final warning" are common signals.</p>
										</div>
										<div className="awareness-panel rounded-2xl p-4">
											<div className="font-semibold text-slate-100">Look-alike domains</div>
											<p className="text-sm awareness-subtle mt-2">Small changes can conceal a fraudulent site.</p>
										</div>
										<div className="awareness-panel rounded-2xl p-4">
											<div className="font-semibold text-slate-100">Requests for credentials or one-time codes</div>
											<p className="text-sm awareness-subtle mt-2">Legitimate teams do not request one-time codes.</p>
										</div>
										<div className="awareness-panel rounded-2xl p-4">
											<div className="font-semibold text-slate-100">Unexpected files</div>
											<p className="text-sm awareness-subtle mt-2">Invoices or documents you did not request.</p>
										</div>
										<div className="awareness-panel rounded-2xl p-4">
											<div className="font-semibold text-slate-100">Overly generic greetings</div>
											<p className="text-sm awareness-subtle mt-2">Generic salutations instead of your name.</p>
										</div>
										<div className="awareness-panel rounded-2xl p-4">
											<div className="font-semibold text-slate-100">Offers that seem too good to be true</div>
											<p className="text-sm awareness-subtle mt-2">Unexpected prizes, refunds, or bonuses.</p>
										</div>
								</div>
							</div>

							<div id="what-to-do">
								<h3 className="font-display text-2xl text-slate-100">Recommended actions</h3>
								<div className="awareness-panel mt-4 rounded-2xl p-5">
									<ul className="font-body list-disc ml-5 text-sm text-slate-200 space-y-2">
										<li><strong>Login request:</strong> Close the message and sign in through the official app or portal.</li>
										<li><strong>Payment or fee:</strong> Use the finance portal you already trust, not a link.</li>
										<li><strong>Delivery notice:</strong> Track it in the carrier app or official website.</li>
										<li><strong>OTP or reset code:</strong> Do not share it, even with support.</li>
									</ul>
								</div>
							</div>

							<div id="if-clicked">
								<h3 className="font-display text-2xl text-slate-100">If you have already clicked</h3>
								<div className="mt-4 rounded-2xl border border-rose-200/30 bg-rose-200/10 p-5">
									<ol className="font-body list-decimal ml-5 text-sm text-slate-200 space-y-2">
										<li><strong>Close the tab</strong> and discontinue interaction with the message.</li>
										<li><strong>Change your password</strong> using the official site or app.</li>
										<li><strong>Enable MFA</strong> if it is not already enabled.</li>
										<li><strong>Report the incident</strong> so the team can protect others.</li>
									</ol>
									<p className="font-body mt-3 text-xs awareness-subtle">Note: If the same password is reused elsewhere, update those accounts as well.</p>
								</div>
							</div>

							<div id="self-check">
								<h3 className="font-display text-2xl text-slate-100">Brief self-check</h3>
								<div className="mt-4 grid grid-cols-1 sm:grid-cols-2 gap-3 font-body">
										<div className="awareness-panel rounded-2xl p-4">
											<div className="font-semibold text-slate-100">Does the domain match exactly?</div>
											<p className="text-sm awareness-subtle mt-2">If not, do not click. Confirm via the official site.</p>
										</div>
										<div className="awareness-panel rounded-2xl p-4">
											<div className="font-semibold text-slate-100">Are they asking for sensitive data?</div>
											<p className="text-sm awareness-subtle mt-2">Passwords, one-time codes, or bank details should not be shared.</p>
										</div>
										<div className="awareness-panel rounded-2xl p-4">
											<div className="font-semibold text-slate-100">Does it feel urgent or intimidating?</div>
											<p className="text-sm awareness-subtle mt-2">Pressure and fear are common tactics. Slow down.</p>
										</div>
										<div className="awareness-panel rounded-2xl p-4">
											<div className="font-semibold text-slate-100">Is the request unexpected?</div>
											<p className="text-sm awareness-subtle mt-2">Unsolicited requests warrant extra caution.</p>
										</div>
								</div>
							</div>
						</section>
					</div>
				</div>
			</div>
		</div>
	)
}
