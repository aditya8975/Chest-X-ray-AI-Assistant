import './globals.css'
import Navbar from '../components/Navbar.jsx'

export const metadata = {
  title: 'Aperture — Chest X-ray AI Assistant',
  description: 'Research demo: chest X-ray pathology triage with Grad-CAM explainability. Not for clinical use.',
}

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="true" />
        <link
          href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>
        <div className="disclaimer-banner">
          <strong>Research demo — not a medical device.</strong> Outputs are AI-generated drafts, not diagnoses. Not for clinical use.
        </div>
        <div className="shell">
          <Navbar />
          {children}
        </div>
      </body>
    </html>
  )
}
