const smsMessages = [
  {
    id: 1,
    sender: 'Bank Alerts',
    body: 'Your account is locked. Verify now to restore access.',
    is_phishing: true,
    link_text: 'Verify account',
    link_url: 'http://example.com/bank-verify',
    feedback: 'Phishing signs: urgency, account lock threat, and a non-bank link. Use the official app or website.'
  },
  {
    id: 2,
    sender: 'Delivery Service',
    body: 'Your package is scheduled for delivery tomorrow. Track here.',
    is_phishing: false,
    link_text: 'Track package',
    link_url: 'https://example.com/track',
    feedback: 'Legitimate update: informational with no request for credentials. Still verify the sender and link.'
  },
  {
    id: 3,
    sender: 'Mobile Carrier',
    body: 'You have won a prize! Click to claim within 2 hours.',
    is_phishing: true,
    link_text: 'Claim prize',
    link_url: 'http://example.com/claim',
    feedback: 'Phishing signs: too-good-to-be-true prize, time pressure, and an unknown link.'
  },
  {
    id: 4,
    sender: 'IT Support',
    body: 'Security update available. Install via the official portal.',
    is_phishing: false,
    link_text: 'Open portal',
    link_url: 'https://example.com/it-portal',
    feedback: 'Legitimate update: references an official portal. Still access via known bookmarks.'
  },
  {
    id: 5,
    sender: 'Tax Office',
    body: 'Refund pending. Submit your details to receive funds.',
    is_phishing: true,
    link_text: 'Submit details',
    link_url: 'http://example.com/refund',
    feedback: 'Phishing signs: request for sensitive details and a generic link. Government agencies do not ask via SMS links.'
  }
]

export default smsMessages
