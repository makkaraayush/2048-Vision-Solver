'use client';
import React, { useState } from 'react';

export default function Home() {
  const [board, setBoard] = useState<number[]>(Array(16).fill(0));
  return (
    <main className="min-h-screen bg-slate-950 text-white p-8">
      <h1 className="text-3xl font-bold tracking-tight">CodeD3mon 2048 AI Solver</h1>
      <div className="mt-8 grid grid-cols-4 gap-2 w-72 h-72 bg-slate-800/80 backdrop-blur p-2 rounded-xl">
        {board.map((v, i) => (
          <div key={i} className="flex items-center justify-center bg-slate-700/60 rounded-lg text-xl font-bold transition-all duration-150">
            {v > 0 ? v : ''}
          </div>
        ))}
      </div>
    </main>
  );
}
