'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'

const LINKS = [
  { href: '/', label: 'Upload' },
  { href: '/worklist', label: 'Worklist' },
  { href: '/dashboard', label: 'Dashboard' },
]

export default function Navbar() {
  const pathname = usePathname()
  return (
    <div className="navbar">
      <Link href="/" className="brand">
        <span className="brand-mark" />
        Aperture
      </Link>
      <nav className="nav-links">
        {LINKS.map((l) => (
          <Link
            key={l.href}
            href={l.href}
            className={'nav-link' + (pathname === l.href ? ' active' : '')}
          >
            {l.label}
          </Link>
        ))}
      </nav>
    </div>
  )
}
