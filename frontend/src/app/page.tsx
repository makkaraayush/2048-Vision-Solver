'use client';
import React, { useState } from 'react';

export default function Home() {
  const [board, setBoard] = useState<number[]>(Array(16).fill(0));
  const [isAutoplaying, setIsAutoplaying] = useState(false);

  const toggleAutoplay = () => setIsAutoplaying(!isAutoplaying);

  return (
    <main className="min-h-screen bg-slate-950 text-white p-8">
      <div className="max-w-4xl mx-auto">
        <header className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold">CodeD3mon 2048 HUD</h1>
          <button 
            onClick={toggleAutoplay}
            className={`px-4 py-2 rounded-lg font-semibold ${isAutoplaying ? 'bg-red-500' : 'bg-emerald-500'}`}
          >
            {isAutoplaying ? 'Pause AI' : 'Start Autoplay'}
          </button>
        </header>
      </div>
    </main>
  );
}
