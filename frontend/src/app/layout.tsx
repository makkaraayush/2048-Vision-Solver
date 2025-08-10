import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';

const inter = Inter({ subsets: ['latin'], variable: '--font-inter' });

export const metadata: Metadata = {
  title: 'CodeD3mon-2048 | Autonomous Vision Solver',
  description: 'High-speed CV-based 2048 autonomous agent and evolutionary AI dashboard by CodeD3mon',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.variable} font-sans antialiased bg-slate-950 text-slate-50 min-h-screen selection:bg-gold-500/30`}>
        {/* Subtle background glow */}
        <div className="fixed inset-0 -z-10 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-slate-900 via-slate-950 to-slate-950"></div>
        {children}
      </body>
    </html>
  );
}
