import './globals.css'
import { Inter } from 'next/font/google'
import Providers from './providers'
import Image from 'next/image'

const inter = Inter({ subsets: ['latin'] })

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <Providers>
          <div className="min-h-screen bg-gray-50">
            <header className="sticky top-0 z-20 bg-white/80 backdrop-blur border-b border-gray-200">
              <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3 flex items-center space-x-3">
                <Image src="/stackai-mark.svg" alt="StackAI" width={28} height={28} priority />
                <span className="text-sm font-semibold tracking-tight">StackAI</span>
              </div>
            </header>
            {children}
          </div>
        </Providers>
      </body>
    </html>
  )
}

export const metadata = {
  title: 'StackAI Frontend - Vector Database Testing Interface',
  description: 'Modern testing interface for StackAI Vector Database with backup and rollback features',
} 