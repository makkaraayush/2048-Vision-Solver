"use client";

import { useEffect, useState, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  Activity, Cpu, Clock, Zap, Target, 
  ArrowUp, ArrowDown, ArrowLeft, ArrowRight, 
  Play, Square, Sparkles, Trophy, RefreshCw, Flame, CheckCircle2, RotateCcw, Trash2
} from "lucide-react";

interface SolverStats {
  best_move: string | null;
  score: number;
  structure_quality: number;
  depth: number;
  nodes_evaluated: number;
  time_ms: number;
  move_scores: Record<string, number>;
}

interface TrainingStats {
  generation: number;
  level: number;
  best_max_tile: number;
  best_score: number;
  current_max_tile: number;
  current_score: number;
  games_played: number;
  status: string;
}

interface SolverState {
  is_running: boolean;
  automation_allowed: boolean;
  auto_play_active: boolean;
  is_calibrated?: boolean;
  calibration_status?: "idle" | "step1" | "step2" | "done" | "error";
  vision_preview?: string;
  active_model?: "default" | "champion";
  has_champion?: boolean;
  champion_meta?: {
    generation?: number;
    best_max_tile?: number;
    best_score?: number;
    games_played?: number;
  };
  last_stats: SolverStats;
  current_grid: number[];
  training_active?: boolean;
  training_stats?: TrainingStats;
}

const TILE_COLORS: Record<number, string> = {
  0: "bg-slate-800/50",
  2: "bg-slate-700 text-slate-200",
  4: "bg-slate-600 text-slate-100",
  8: "bg-orange-500/80 text-white shadow-[0_0_15px_rgba(249,115,22,0.3)]",
  16: "bg-orange-600/90 text-white shadow-[0_0_20px_rgba(234,88,12,0.4)]",
  32: "bg-red-500/90 text-white shadow-[0_0_20px_rgba(239,68,68,0.5)]",
  64: "bg-red-600 text-white shadow-[0_0_25px_rgba(220,38,38,0.6)]",
  128: "bg-amber-400 text-slate-900 shadow-[0_0_30px_rgba(251,191,36,0.6)] font-bold",
  256: "bg-amber-500 text-slate-900 shadow-[0_0_30px_rgba(245,158,11,0.7)] font-bold",
  512: "bg-amber-600 text-slate-900 shadow-[0_0_35px_rgba(217,119,6,0.8)] font-bold",
  1024: "bg-yellow-400 text-slate-900 shadow-[0_0_40px_rgba(250,204,21,0.9)] text-3xl font-extrabold",
  2048: "bg-yellow-500 text-slate-900 shadow-[0_0_50px_rgba(234,179,8,1)] text-3xl font-black ring-4 ring-yellow-300/50",
  4096: "bg-purple-600 text-white shadow-[0_0_50px_rgba(168,85,247,0.9)] text-3xl font-black ring-4 ring-purple-400/50"
};

const LEVEL_NAMES: Record<number, string> = {
  1: "Novice (256)",
  2: "Adept (512)",
  3: "Expert (1024)",
  4: "Master (2048)",
  5: "Grandmaster (4096+)"
};

export default function Home() {
  const [state, setState] = useState<SolverState | null>(null);
  const [connected, setConnected] = useState(false);
  const ws = useRef<WebSocket | null>(null);

  useEffect(() => {
    const connect = () => {
      ws.current = new WebSocket("ws://localhost:8000/ws");
      
      ws.current.onopen = () => setConnected(true);
      ws.current.onclose = () => {
        setConnected(false);
        setTimeout(connect, 2000); // Reconnect logic
      };
      ws.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          setState(data);
        } catch (e) {}
      };
    };
    
    connect();
    return () => ws.current?.close();
  }, []);

  const grid = state?.current_grid?.length === 16 ? state.current_grid : Array(16).fill(0);
  const stats = state?.last_stats;
  const trainStats = state?.training_stats;
  const isTraining = state?.training_active;

  const renderMoveIcon = (move: string | null) => {
    switch (move) {
      case 'UP': return <ArrowUp className="w-8 h-8 text-emerald-400" />;
      case 'DOWN': return <ArrowDown className="w-8 h-8 text-emerald-400" />;
      case 'LEFT': return <ArrowLeft className="w-8 h-8 text-emerald-400" />;
      case 'RIGHT': return <ArrowRight className="w-8 h-8 text-emerald-400" />;
      default: return <Target className="w-8 h-8 text-slate-500" />;
    }
  };

  const levelProgress = Math.min(100, Math.max(15, ((trainStats?.level || 1) / 5) * 100));

  return (
    <main className="min-h-screen p-2.5 sm:p-4 md:p-6 flex flex-col items-center max-w-7xl mx-auto w-full">
      {/* Top Header */}
      <motion.div 
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2 sm:gap-4 mb-3 sm:mb-4"
      >
        <div>
          <div className="flex items-center gap-2 flex-wrap">
            <h1 className="text-lg sm:text-2xl lg:text-3xl font-extrabold tracking-tight">
              CodeD3mon <span className="bg-clip-text text-transparent bg-gradient-to-r from-red-500 via-orange-400 to-amber-300">Vision Engine</span>
            </h1>
            <span className="text-[10px] sm:text-xs px-2 py-0.5 rounded-full bg-red-500/10 border border-red-500/30 text-red-400 font-mono font-semibold">
              Snake-Expectimax
            </span>
          </div>
          <div className="flex items-center gap-2 text-slate-400 mt-0.5 flex-wrap">
            <div className={`w-2 h-2 rounded-full ${connected ? 'bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.5)]' : 'bg-red-500 shadow-[0_0_10px_rgba(239,68,68,0.5)]'}`} />
            <span className="text-[11px] font-medium tracking-wide uppercase">{connected ? "Engine Online" : "Searching for Engine..."}</span>
            <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-slate-800/80 border border-slate-700 text-slate-400">CodeD3mon-2048</span>
          </div>
        </div>
        
        {/* Action Controls Toolbar */}
        <div className="glass-panel p-1.5 sm:p-2 rounded-2xl flex items-center justify-between sm:justify-start gap-1.5 sm:gap-2 flex-wrap border border-slate-800/80 w-full md:w-auto">
          <div className="flex items-center gap-1.5 sm:gap-2 flex-wrap">
            <button 
              onClick={() => ws.current?.send("toggle")}
              className={`flex items-center gap-1.5 px-2.5 sm:px-3 py-1.5 rounded-xl transition-all cursor-pointer border text-xs sm:text-sm font-semibold ${state?.is_running ? 'bg-emerald-500/15 border-emerald-500/50 text-emerald-400 shadow-[0_0_12px_rgba(16,185,129,0.2)]' : 'hover:bg-slate-800/60 border-slate-700 text-slate-300'}`}
            >
              {state?.is_running ? (
                <Play className="w-3.5 h-3.5 animate-pulse" fill="currentColor" />
              ) : (
                <Square className="w-3.5 h-3.5" fill="currentColor" />
              )}
              <span>{state?.is_running ? "Scanner Active" : "Scanner Off"}</span>
            </button>
            
            <button 
              onClick={() => ws.current?.send("toggle_automation")}
              className={`flex items-center gap-1.5 px-2.5 sm:px-3 py-1.5 rounded-xl transition-all cursor-pointer border text-xs sm:text-sm font-semibold ${state?.automation_allowed ? 'bg-sky-500/15 border-sky-500/50 text-sky-400 shadow-[0_0_12px_rgba(14,165,233,0.2)]' : 'hover:bg-slate-800/60 border-slate-700 text-slate-400'}`}
            >
              <span>{state?.automation_allowed ? "Auto-Play Unlocked" : "Auto-Play Locked"}</span>
            </button>

            {state?.automation_allowed && (
              <div className="text-[11px] sm:text-xs text-slate-300 border-l border-slate-700 pl-2 sm:pl-3 flex items-center gap-1 font-medium">
                Hit <kbd className="bg-slate-800 px-1 py-0.5 rounded font-mono text-emerald-400 border border-slate-700 font-bold text-[10px]">F9</kbd> to play
              </div>
            )}

            {/* Model Selector Slider Switch */}
            <div className="flex items-center gap-1.5 border-l border-slate-800 pl-2">
              <span className={`text-[11px] sm:text-xs font-semibold transition-colors ${state?.active_model !== 'champion' ? 'text-cyan-400 font-bold' : 'text-slate-400'}`}>
                Starter
              </span>
              <button
                type="button"
                onClick={() => {
                  if (state?.has_champion) {
                    ws.current?.send("toggle_model");
                  }
                }}
                disabled={!state?.has_champion}
                title={!state?.has_champion ? "No trained champion yet. Evolve a champion in the lab below to unlock!" : `Switch model (Current: ${state?.active_model === 'champion' ? 'Champion' : 'Starter'})`}
                className={`w-10 h-5 rounded-full p-0.5 transition-all flex items-center relative border ${
                  !state?.has_champion
                    ? "bg-slate-800/40 border-slate-700/40 cursor-not-allowed opacity-60"
                    : state?.active_model === "champion"
                    ? "bg-amber-500/25 border-amber-500/60 shadow-[0_0_10px_rgba(245,158,11,0.25)] cursor-pointer"
                    : "bg-cyan-500/20 border-cyan-500/50 cursor-pointer"
                }`}
              >
                <motion.div
                  animate={{ x: state?.has_champion && state?.active_model === "champion" ? 20 : 0 }}
                  transition={{ type: "spring", stiffness: 500, damping: 30 }}
                  className={`w-3.5 h-3.5 rounded-full shadow-sm flex items-center justify-center ${
                    !state?.has_champion
                      ? "bg-slate-600"
                      : state?.active_model === "champion"
                      ? "bg-amber-400 text-slate-950"
                      : "bg-cyan-400 text-slate-950"
                  }`}
                >
                  {state?.has_champion && state?.active_model === "champion" ? (
                    <Trophy className="w-2 h-2" />
                  ) : (
                    <Zap className="w-2 h-2" />
                  )}
                </motion.div>
              </button>
              <div className="flex items-center gap-1">
                <span className={`text-[11px] sm:text-xs font-semibold transition-colors ${state?.has_champion && state?.active_model === 'champion' ? 'text-amber-400 font-bold' : 'text-slate-400'}`}>
                  Champion
                </span>
                {!state?.has_champion && (
                  <span className="text-[9px] uppercase font-mono px-1 py-0.2 rounded bg-slate-800/90 border border-slate-700/80 text-slate-500">
                    Locked
                  </span>
                )}
              </div>
            </div>

            {/* Manual Calibration Controls */}
            {state?.calibration_status === "step1" ? (
              <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-xl bg-amber-500/15 border border-amber-500/40 text-amber-300 text-xs animate-pulse font-medium">
                <Target className="w-3 h-3 text-amber-400" />
                <span>Click <strong>TOP-LEFT</strong></span>
                <button
                  type="button"
                  onClick={() => ws.current?.send("cancel_calibration")}
                  className="ml-1 text-slate-400 hover:text-white underline cursor-pointer text-[10px]"
                >
                  Cancel
                </button>
              </div>
            ) : state?.calibration_status === "step2" ? (
              <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-xl bg-cyan-500/15 border border-cyan-500/40 text-cyan-300 text-xs animate-pulse font-medium">
                <Target className="w-3 h-3 text-cyan-400" />
                <span>Click <strong>BOTTOM-RIGHT</strong></span>
                <button
                  type="button"
                  onClick={() => ws.current?.send("cancel_calibration")}
                  className="ml-1 text-slate-400 hover:text-white underline cursor-pointer text-[10px]"
                >
                  Cancel
                </button>
              </div>
            ) : state?.is_calibrated ? (
              <div className="flex items-center gap-1 bg-slate-900/80 border border-slate-800 rounded-xl p-0.5 text-xs">
                <span className="flex items-center gap-1 text-[10px] text-emerald-400 font-semibold bg-emerald-500/15 border border-emerald-500/30 px-1.5 py-0.5 rounded-lg">
                  <CheckCircle2 className="w-2.5 h-2.5" />
                  Calibrated
                </span>
                <button
                  type="button"
                  onClick={() => ws.current?.send("reset_calibration")}
                  title="Reset to automatic screen detection"
                  className="text-slate-400 hover:text-slate-200 px-1.5 py-0.5 rounded-lg text-[11px] hover:bg-slate-800/80 cursor-pointer transition-colors"
                >
                  Auto
                </button>
                <button
                  type="button"
                  onClick={() => ws.current?.send("start_calibration")}
                  title="Re-calibrate board position"
                  className="text-indigo-400 hover:text-indigo-300 px-1.5 py-0.5 rounded-lg text-[11px] hover:bg-indigo-500/10 cursor-pointer transition-colors"
                >
                  Re-Calibrate
                </button>
              </div>
            ) : (
              <button
                type="button"
                onClick={() => ws.current?.send("start_calibration")}
                title="Manually calibrate the board by clicking top-left and bottom-right corners"
                className="flex items-center gap-1 px-2.5 py-1 rounded-xl text-xs font-semibold transition-all cursor-pointer border border-slate-700 hover:border-indigo-500/50 hover:bg-indigo-500/10 text-slate-300 hover:text-indigo-300"
              >
                <Target className="w-3 h-3 text-indigo-400" />
                <span>Calibrate</span>
              </button>
            )}
          </div>
          
          <button 
            onClick={() => {
              if(confirm("Are you sure you want to cleanly shut down both servers?")) {
                ws.current?.send("shutdown");
                setTimeout(() => window.close(), 500);
              }
            }}
            className="flex items-center gap-1 bg-red-500/10 hover:bg-red-500/20 text-red-400 p-1.5 px-2.5 rounded-xl transition-colors cursor-pointer border border-red-500/20 hover:border-red-500/50 text-xs font-semibold ml-auto sm:ml-0"
          >
            <span>Power Off</span>
          </button>
        </div>
      </motion.div>

      {/* Auto-play Active Alert Banner */}
      {state?.auto_play_active && (
        <motion.div 
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="w-full bg-red-500/20 border border-red-500/50 text-red-200 p-2.5 rounded-2xl text-center text-xs sm:text-sm font-bold shadow-[0_0_20px_rgba(239,68,68,0.3)] animate-pulse mb-4"
        >
          ⚡ AUTO-PLAY ACTIVE: CodeD3mon-2048 is sending keystrokes! Press F9 anytime to pause.
        </motion.div>
      )}

      {/* Main Grid: Left Matrix + Right Engine Telemetry (side-by-side from md: up, compact and auto-scaled) */}
      <div className="w-full grid grid-cols-1 md:grid-cols-12 gap-4 sm:gap-6 mb-6">
        
        {/* Left Column: Board Vision Feed */}
        <motion.div 
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.1 }}
          className="md:col-span-6 lg:col-span-5 glass-panel rounded-3xl p-4 sm:p-6 border border-slate-800/80 flex flex-col justify-between"
        >
          <div>
            <div className="flex items-center justify-between mb-3 sm:mb-4">
              <h2 className="text-base sm:text-lg font-bold flex items-center gap-2 text-slate-200">
                <Activity className="w-4 h-4 sm:w-5 sm:h-5 text-emerald-400" />
                Vision Matrix
              </h2>
              <div className="text-[11px] sm:text-xs font-mono text-emerald-400/90 bg-emerald-500/10 border border-emerald-500/20 px-2 sm:px-2.5 py-0.5 sm:py-1 rounded-full">
                {state?.is_calibrated ? "Manually Calibrated" : "OpenCV Auto-Track"}
              </div>
            </div>
            
            {/* 4x4 Grid with capped max width so it scales cleanly on small screens and never cuts off */}
            <div className="w-full max-w-[290px] sm:max-w-[330px] md:max-w-[350px] aspect-square mx-auto bg-slate-950/80 rounded-2xl p-2 sm:p-3 shadow-inner ring-1 ring-white/5">
              <div className="grid grid-cols-4 gap-1.5 sm:gap-2.5 h-full">
                <AnimatePresence>
                  {grid.map((val, idx) => (
                    <motion.div
                      key={`${idx}-${val}`}
                      initial={{ scale: 0.8, opacity: 0 }}
                      animate={{ scale: 1, opacity: 1 }}
                      className={`rounded-lg sm:rounded-xl flex items-center justify-center text-base sm:text-xl md:text-2xl font-bold transition-all duration-200 ${TILE_COLORS[val] || TILE_COLORS[0]}`}
                    >
                      {val > 0 ? val : ""}
                    </motion.div>
                  ))}
                </AnimatePresence>
              </div>
            </div>

            {/* Live Optical Screen Crop Preview */}
            {state?.vision_preview && (
              <div className="mt-3 p-2.5 rounded-xl bg-slate-950/90 border border-slate-800 flex items-center justify-between gap-2.5 shadow-inner">
                <div className="flex items-center gap-2.5">
                  <img 
                    src={`data:image/jpeg;base64,${state.vision_preview}`} 
                    alt="Live Optical Screen Crop" 
                    className="w-11 h-11 sm:w-12 sm:h-12 rounded-lg border border-emerald-500/40 object-cover shadow-sm ring-1 ring-emerald-500/30 flex-shrink-0"
                  />
                  <div className="flex flex-col">
                    <span className="text-[11px] sm:text-xs font-semibold text-slate-200 flex items-center gap-1">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                      Live Optical Crop
                    </span>
                    <span className="text-[10px] text-slate-400 font-mono">
                      Green grid = 4x4 tile boundaries
                    </span>
                  </div>
                </div>
                <div className="text-[9px] uppercase font-mono px-1.5 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/30 text-emerald-400">
                  {state?.is_calibrated ? "Locked" : "Auto"}
                </div>
              </div>
            )}
          </div>

          <div className="mt-3 flex items-center justify-between text-[11px] text-slate-500 font-mono">
            <span>Color &amp; Contour Active</span>
            <span>Zero-OCR Latency</span>
          </div>
        </motion.div>

        {/* Right Column: Engine Stats */}
        <motion.div 
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
          className="md:col-span-6 lg:col-span-7 flex flex-col gap-3.5 sm:gap-4"
        >
          {/* Main Action Banner */}
          <div className="glass-panel rounded-3xl p-4 sm:p-5 relative overflow-hidden group border border-slate-800/80">
            <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
            <div className="flex justify-between items-center relative z-10 gap-2">
              <div>
                <h3 className="text-slate-400 text-[10px] sm:text-xs font-semibold uppercase tracking-wider mb-1">Calculated Optimum Move</h3>
                <div className="text-3xl sm:text-4xl lg:text-5xl font-black tracking-tight text-white flex items-center gap-2.5">
                  {renderMoveIcon(stats?.best_move || null)}
                  <span>{stats?.best_move || "Awaiting Data"}</span>
                </div>
              </div>
              <div className="text-right flex-shrink-0">
                <div className="text-slate-400 text-[10px] sm:text-xs font-semibold uppercase tracking-wider mb-1" title="Logarithmic grade of how close the board is to mathematical perfection (max 10.0)">
                  Structure Quality
                </div>
                <div className="text-2xl sm:text-3xl lg:text-4xl font-bold text-emerald-400 flex items-end gap-1 justify-end">
                  {stats?.structure_quality ? stats.structure_quality.toFixed(1) : "0.0"}
                  <span className="text-xs sm:text-base text-slate-500 mb-0.5">/ 10</span>
                </div>
              </div>
            </div>

            {/* Direction evaluation pills */}
            {stats?.move_scores && Object.keys(stats.move_scores).length > 0 && (
              <div className="mt-3 pt-2.5 border-t border-slate-800/70 grid grid-cols-4 gap-1.5">
                {(['UP', 'DOWN', 'LEFT', 'RIGHT'] as const).map((dir) => {
                  const score = stats.move_scores[dir];
                  const isBest = stats.best_move === dir;
                  const isPossible = score !== undefined;
                  return (
                    <div 
                      key={dir} 
                      className={`px-1.5 py-1 rounded-xl text-center border transition-all ${
                        isBest 
                          ? 'bg-emerald-500/20 border-emerald-500/50 text-emerald-300 font-bold shadow-[0_0_10px_rgba(16,185,129,0.2)]'
                          : isPossible 
                          ? 'bg-slate-900/60 border-slate-800/80 text-slate-400' 
                          : 'bg-slate-900/20 border-slate-800/40 text-slate-600 opacity-40'
                      }`}
                    >
                      <div className="text-[10px] font-mono tracking-tight flex items-center justify-center gap-0.5">
                        {dir === 'UP' && <ArrowUp className="w-2.5 h-2.5" />}
                        {dir === 'DOWN' && <ArrowDown className="w-2.5 h-2.5" />}
                        {dir === 'LEFT' && <ArrowLeft className="w-2.5 h-2.5" />}
                        {dir === 'RIGHT' && <ArrowRight className="w-2.5 h-2.5" />}
                        <span>{dir}</span>
                      </div>
                      <div className="text-[9px] font-mono font-medium truncate mt-0.5">
                        {isPossible ? Math.round(score).toLocaleString() : 'N/A'}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* Telemetry Grid */}
          <div className="grid grid-cols-2 gap-2.5 sm:gap-3.5">
            <div className="glass-panel p-3 sm:p-4 rounded-2xl flex flex-col border border-slate-800/80">
              <div className="flex items-center gap-2 text-slate-400 mb-1">
                <Cpu className="w-3.5 h-3.5 text-sky-400" />
                <span className="text-xs sm:text-sm font-medium">Nodes Evaluated</span>
              </div>
              <span className="text-lg sm:text-2xl font-bold text-white">
                {stats?.nodes_evaluated ? stats.nodes_evaluated.toLocaleString() : 0}
              </span>
              <span className="text-[10px] text-slate-500 mt-0.5 font-mono">Expectimax Branching</span>
            </div>
            
            <div className="glass-panel p-3 sm:p-4 rounded-2xl flex flex-col border border-slate-800/80">
              <div className="flex items-center gap-2 text-slate-400 mb-1">
                <Clock className="w-3.5 h-3.5 text-indigo-400" />
                <span className="text-xs sm:text-sm font-medium">Compute Latency</span>
              </div>
              <div className="flex items-end gap-1">
                <span className="text-lg sm:text-2xl font-bold text-white">
                  {stats?.time_ms || 0}
                </span>
                <span className="text-slate-400 text-xs font-medium pb-0.5">ms</span>
              </div>
              <span className="text-[10px] text-slate-500 mt-0.5 font-mono">Decision Time</span>
            </div>

            <div className="glass-panel p-3 sm:p-4 rounded-2xl flex flex-col border border-slate-800/80">
              <div className="flex items-center gap-2 text-slate-400 mb-1">
                <Target className="w-3.5 h-3.5 text-rose-400" />
                <span className="text-xs sm:text-sm font-medium">Search Depth</span>
              </div>
              <span className="text-lg sm:text-2xl font-bold text-white">
                {stats?.depth || 0}
              </span>
              <span className="text-[10px] text-slate-500 mt-0.5 font-mono">Adaptive Plys</span>
            </div>

            <div className="glass-panel p-3 sm:p-4 rounded-2xl flex flex-col border border-slate-800/80">
              <div className="flex items-center gap-2 text-slate-400 mb-1">
                <Zap className="w-3.5 h-3.5 text-amber-400" />
                <span className="text-xs sm:text-sm font-medium">Throughput</span>
              </div>
              <span className="text-lg sm:text-2xl font-bold text-white">
                {stats?.nodes_evaluated && stats?.time_ms ? Math.round(stats.nodes_evaluated / (stats.time_ms / 1000)).toLocaleString() : 0}
              </span>
              <span className="text-[10px] text-slate-500 mt-0.5 font-mono">Nodes / sec</span>
            </div>
          </div>
        </motion.div>
      </div>

      {/* AI Evolutionary Training Center */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="w-full glass-panel rounded-3xl p-4 sm:p-6 md:p-8 border border-slate-800/80 relative overflow-hidden"
      >
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-3 sm:gap-4 mb-4 sm:mb-6">
          <div className="flex items-center gap-2.5 sm:gap-3">
            <div className="w-8 h-8 sm:w-10 sm:h-10 rounded-2xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-amber-400 flex-shrink-0">
              <Sparkles className="w-4 h-4 sm:w-5 sm:h-5" />
            </div>
            <div>
              <h2 className="text-lg sm:text-xl font-bold text-white flex items-center gap-2">
                Evolutionary Training Lab
                {isTraining && (
                  <span className="flex h-2 w-2 relative">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-amber-500"></span>
                  </span>
                )}
              </h2>
              <p className="text-[11px] sm:text-xs text-slate-400">Headless genetic algorithm that plays thousands of internal games and continuously evolves better weights.</p>
            </div>
          </div>

          <div className="flex items-center gap-2 sm:gap-3 flex-wrap">
            {state?.has_champion && (
              <button
                type="button"
                onClick={() => {
                  if (confirm("Reset evolved champion and return to default starter weights? This will delete best_weights.json.")) {
                    ws.current?.send("reset_weights");
                  }
                }}
                title="Delete saved champion weights and reset to default starter model"
                className="flex items-center gap-1.5 p-2 px-3 rounded-xl font-semibold text-xs transition-all cursor-pointer border bg-red-500/10 hover:bg-red-500/20 border-red-500/30 text-red-400 hover:border-red-500/50"
              >
                <Trash2 className="w-3.5 h-3.5" />
                <span>Reset Champion</span>
              </button>
            )}

            <button
              onClick={() => ws.current?.send("toggle_training")}
              className={`flex items-center gap-2 p-2 px-4 rounded-xl font-semibold text-xs sm:text-sm transition-all cursor-pointer border ${isTraining ? 'bg-amber-500/20 border-amber-500/50 text-amber-300 shadow-[0_0_20px_rgba(245,158,11,0.2)]' : 'bg-slate-800/80 hover:bg-slate-800 border-slate-700 text-slate-200'}`}
            >
              {isTraining ? (
                <>
                  <RefreshCw className="w-3.5 h-3.5 animate-spin text-amber-400" />
                  <span>Pause Training</span>
                </>
              ) : (
                <>
                  <Flame className="w-3.5 h-3.5 text-amber-400" />
                  <span>Start Evolutionary Training</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Level and Progress Bar */}
        <div className="mb-4 sm:mb-6 p-3 sm:p-4 rounded-2xl bg-slate-900/60 border border-slate-800/80">
          <div className="flex justify-between items-center mb-1.5 sm:mb-2 flex-wrap gap-1">
            <div className="flex items-center gap-1.5 sm:gap-2">
              <Trophy className="w-3.5 h-3.5 text-amber-400" />
              <span className="text-xs sm:text-sm font-bold text-white">AI Mastery Level:</span>
              <span className="text-xs sm:text-sm font-semibold text-amber-400">
                Level {trainStats?.level || 1} &mdash; {LEVEL_NAMES[trainStats?.level || 1]}
              </span>
            </div>
            <div className="text-[11px] sm:text-xs font-mono text-slate-400">
              Evolution Status: <span className="text-emerald-400 font-semibold">{trainStats?.status || "Ready to Train"}</span>
            </div>
          </div>
          
          <div className="w-full bg-slate-800 rounded-full h-2 sm:h-2.5 overflow-hidden">
            <div 
              className="bg-gradient-to-r from-amber-500 via-orange-400 to-emerald-400 h-2 sm:h-2.5 rounded-full transition-all duration-500"
              style={{ width: `${levelProgress}%` }}
            />
          </div>
        </div>

        {/* Training Metrics Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-2.5 sm:gap-4">
          <div className="bg-slate-900/40 p-3 sm:p-4 rounded-2xl border border-slate-800/50">
            <div className="text-[11px] sm:text-xs text-slate-400 font-medium mb-1">Champion Max Tile</div>
            <div className="text-xl sm:text-2xl font-black text-amber-400">
              {trainStats?.best_max_tile || 0}
            </div>
            <div className="text-[10px] text-slate-500 mt-0.5 font-mono">Persistent Record</div>
          </div>

          <div className="bg-slate-900/40 p-3 sm:p-4 rounded-2xl border border-slate-800/50">
            <div className="text-[11px] sm:text-xs text-slate-400 font-medium mb-1">Champion Score</div>
            <div className="text-xl sm:text-2xl font-bold text-white">
              {trainStats?.best_score ? trainStats.best_score.toLocaleString() : 0}
            </div>
            <div className="text-[10px] text-slate-500 mt-0.5 font-mono">Highest Game Score</div>
          </div>

          <div className="bg-slate-900/40 p-3 sm:p-4 rounded-2xl border border-slate-800/50">
            <div className="text-[11px] sm:text-xs text-slate-400 font-medium mb-1">Generations Tested</div>
            <div className="text-xl sm:text-2xl font-bold text-sky-400">
              {trainStats?.generation || 0}
            </div>
            <div className="text-[10px] text-slate-500 mt-0.5 font-mono">Evolution Iterations</div>
          </div>

          <div className="bg-slate-900/40 p-3 sm:p-4 rounded-2xl border border-slate-800/50">
            <div className="text-[11px] sm:text-xs text-slate-400 font-medium mb-1">Games Simulated</div>
            <div className="text-xl sm:text-2xl font-bold text-emerald-400">
              {trainStats?.games_played || 0}
            </div>
            <div className="text-[10px] text-slate-500 mt-0.5 font-mono">Headless Matches</div>
          </div>
        </div>

        <div className="mt-3 sm:mt-4 flex items-center justify-between text-[11px] text-slate-500 font-mono pt-2.5 border-t border-slate-800/60 flex-wrap gap-2">
          <div className="flex items-center gap-1.5 sm:gap-2">
            <span className="text-slate-400">Solver Active Model:</span>
            <span className={`px-2 py-0.5 rounded-full font-bold flex items-center gap-1 ${
              state?.active_model === 'champion' && state?.has_champion
                ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40 shadow-[0_0_10px_rgba(245,158,11,0.2)]'
                : 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40'
            }`}>
              {state?.active_model === 'champion' && state?.has_champion ? (
                <>
                  <Trophy className="w-2.5 h-2.5 text-amber-400" />
                  <span>Evolved Champion (Gen {state?.champion_meta?.generation || trainStats?.generation || 1})</span>
                </>
              ) : (
                <>
                  <Zap className="w-2.5 h-2.5 text-cyan-400" />
                  <span>Default Starter Baseline</span>
                </>
              )}
            </span>
          </div>
          <span>Saves champion to best_weights.json</span>
        </div>
      </motion.div>
    </main>
  );
}
