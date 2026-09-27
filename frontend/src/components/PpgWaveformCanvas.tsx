import React, { useEffect, useRef } from 'react';

interface PpgWaveformCanvasProps {
  ppgBuffer: number[];
  height?: number;
}

export const PpgWaveformCanvas: React.FC<PpgWaveformCanvasProps> = ({
  ppgBuffer,
  height = 200
}) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const animationFrameRef = useRef<number | null>(null);
  const sweepXRef = useRef<number>(0);
  const sampleIndexRef = useRef<number>(0);
  const historyRef = useRef<{ x: number; y: number }[]>([]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || ppgBuffer.length === 0) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Handle high DPI displays
    const dpr = window.devicePixelRatio || 1;
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width * dpr;
    canvas.height = height * dpr;
    ctx.scale(dpr, dpr);

    const width = rect.width;
    const midY = height / 2;
    const sweepSpeed = 2.2; // Pixels per frame

    const render = () => {
      // Draw dark monitor background with faint medical grid
      ctx.fillStyle = '#070d14';
      ctx.fillRect(0, 0, width, height);

      // Draw waveform guide grid (0.2s large squares, 0.04s small squares)
      ctx.lineWidth = 0.5;
      ctx.strokeStyle = 'rgba(16, 185, 129, 0.08)';
      
      const gridSize = 20;
      for (let x = 0; x < width; x += gridSize) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, height);
        ctx.stroke();
      }
      for (let y = 0; y < height; y += gridSize) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(width, y);
        ctx.stroke();
      }

      // Read current sample from rolling buffer
      let currentSample = 0.0;
      if (ppgBuffer.length > 0) {
        const idx = Math.floor(sampleIndexRef.current) % ppgBuffer.length;
        currentSample = ppgBuffer[idx] || 0.0;
        sampleIndexRef.current = (sampleIndexRef.current + 50 / 60) % ppgBuffer.length;
      }

      // Convert millivolt sample to canvas Y coordinate
      // 1.0 mV ≈ 45 pixels deflection
      const targetY = midY - currentSample * 45;

      const currentX = sweepXRef.current;
      historyRef.current.push({ x: currentX, y: targetY });

      // Clean up points that are behind or ahead of sweep
      if (historyRef.current.length > 500) {
        historyRef.current.shift();
      }

      // Erase a gap ahead of the sweep cursor (medical oscilloscope style)
      const eraseWidth = 35;
      ctx.fillStyle = '#070d14';
      ctx.fillRect(currentX, 0, eraseWidth, height);
      if (currentX + eraseWidth > width) {
        ctx.fillRect(0, 0, (currentX + eraseWidth) - width, height);
      }

      // Draw the waveform trail with phosphor glow
      ctx.lineWidth = 2.2;
      ctx.lineJoin = 'round';
      ctx.lineCap = 'round';
      ctx.shadowBlur = 8;
      ctx.shadowColor = '#10b981';
      ctx.strokeStyle = '#34d399';

      const points = historyRef.current;
      if (points.length > 1) {
        ctx.beginPath();
        for (let i = 0; i < points.length; i++) {
          const pt = points[i];
          // Skip drawing across screen wrap
          if (i > 0 && Math.abs(pt.x - points[i - 1].x) > 20) {
            ctx.stroke();
            ctx.beginPath();
            ctx.moveTo(pt.x, pt.y);
          } else if (i === 0) {
            ctx.moveTo(pt.x, pt.y);
          } else {
            ctx.lineTo(pt.x, pt.y);
          }
        }
        ctx.stroke();
      }

      // Reset shadow for overlays
      ctx.shadowBlur = 0;

      // Draw sweep cursor vertical glow bar
      ctx.fillStyle = 'rgba(16, 185, 129, 0.4)';
      ctx.fillRect(currentX, 0, 2, height);

      // Increment sweep cursor
      sweepXRef.current += sweepSpeed;
      if (sweepXRef.current >= width) {
        sweepXRef.current = 0;
        historyRef.current = [];
      }

      animationFrameRef.current = requestAnimationFrame(render);
    };

    render();

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [ppgBuffer, height]);

  if (ppgBuffer.length === 0) {
    return (
      <div className="flex flex-col justify-between rounded-2xl border border-slate-800 bg-[#070d14] p-5 shadow-2xl" style={{ minHeight: height }}>
        <div className="flex flex-wrap items-center justify-between gap-3">
          <span className="rounded-md border border-slate-700 bg-slate-900/60 px-2.5 py-1 font-mono text-xs font-bold tracking-widest text-slate-300">
            MAX30102 · PPG
          </span>
          <span className="text-xs text-slate-400">Signal quality: Not available</span>
        </div>
        <div className="py-8 text-center">
          <p className="text-sm font-semibold text-slate-200">PPG waveform unavailable</p>
          <p className="mt-2 text-xs text-slate-400">Raw PPG samples are not currently transmitted by this device.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="relative rounded-2xl border border-slate-800 bg-[#070d14] overflow-hidden shadow-2xl">
      {/* Oscilloscope Header Telemetry Overlay */}
      <div className="absolute top-3 left-4 z-10 flex items-center gap-3">
        <span className="text-xs font-mono font-bold tracking-widest text-emerald-400 bg-emerald-950/60 border border-emerald-800/60 px-2.5 py-1 rounded-md">
          MAX30102 - PPG
        </span>
        <span className="text-[11px] font-mono text-slate-400">
          Raw PPG waveform samples
        </span>
      </div>

      <canvas
        ref={canvasRef}
        style={{ width: '100%', height: `${height}px` }}
        className="block"
      />
    </div>
  );
};
