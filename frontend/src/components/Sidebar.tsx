import React from 'react';
import {
  LayoutDashboard,
  Activity,
  Users,
  TrendingUp,
  Bell,
  Cpu,
  FileText,
  Settings,
  ChevronRight
} from 'lucide-react';
import { SidebarPage } from '../App';
import { RiskLevel } from '../types/vitals';

interface SidebarProps {
  activePage: SidebarPage;
  onNavigate: (page: SidebarPage) => void;
  alertCount?: number;
  riskLevel?: RiskLevel;
  isConnected?: boolean;
}

interface NavItem {
  id: SidebarPage;
  label: string;
  icon: React.ElementType;
}

const NAV_ITEMS: NavItem[] = [
  { id: 'overview', label: 'Overview', icon: LayoutDashboard },
  { id: 'monitoring', label: 'Live Monitoring', icon: Activity },
  { id: 'patients', label: 'Patients', icon: Users },
  { id: 'trends', label: 'Trends', icon: TrendingUp },
  { id: 'alerts', label: 'Alerts', icon: Bell },
  { id: 'devices', label: 'Devices', icon: Cpu },
  { id: 'settings', label: 'Settings', icon: Settings },
];

const RISK_COLORS: Record<RiskLevel, string> = {
  NORMAL: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20',
  WATCH: 'text-amber-400 bg-amber-500/10 border-amber-500/20',
  HIGH_RISK: 'text-rose-400 bg-rose-500/10 border-rose-500/20',
};

export const Sidebar: React.FC<SidebarProps> = ({
  activePage,
  onNavigate,
  alertCount = 0,
  riskLevel,
  isConnected = false,
}) => {
  return (
    <aside className="hidden md:flex flex-col w-56 lg:w-64 border-r border-slate-800/60 bg-[#080d17]/80 shrink-0">
      {/* System Status */}
      <div className="p-4 border-b border-slate-800/60">
        <div className="text-[10px] uppercase tracking-widest text-slate-500 font-semibold mb-2">System</div>
        <div className="flex items-center gap-2">
          <span className={`w-2 h-2 rounded-full ${isConnected ? 'bg-emerald-500' : 'bg-rose-500 animate-pulse'}`} />
          <span className={`text-xs font-semibold ${isConnected ? 'text-emerald-400' : 'text-rose-400'}`}>
            {isConnected ? 'ONLINE' : 'OFFLINE'}
          </span>
        </div>
        {riskLevel && <div className={`mt-2 inline-flex items-center gap-1.5 text-xs font-bold px-2 py-0.5 rounded-full border ${RISK_COLORS[riskLevel]}`}>
          {riskLevel === 'NORMAL' ? '● Normal' : riskLevel === 'WATCH' ? '▲ Watch' : '⚠ High Risk'}
        </div>}
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
        <div className="text-[10px] uppercase tracking-widest text-slate-500 font-semibold px-2 py-1.5">Navigation</div>
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          const isActive = activePage === item.id;
          const showBadge = item.id === 'alerts' && alertCount > 0;

          return (
            <button
              key={item.id}
              onClick={() => onNavigate(item.id)}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all group ${
                isActive
                  ? 'bg-cyan-500/10 text-cyan-300 border border-cyan-500/20'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60 border border-transparent'
              }`}
            >
              <Icon className={`w-4 h-4 shrink-0 ${isActive ? 'text-cyan-400' : 'text-slate-500 group-hover:text-slate-300'}`} />
              <span className="flex-1 text-left">{item.label}</span>
              {showBadge && (
                <span className="text-[10px] font-bold bg-rose-500 text-white rounded-full px-1.5 py-0.5 min-w-[18px] text-center">
                  {alertCount}
                </span>
              )}
              {isActive && <ChevronRight className="w-3 h-3 text-cyan-400/60" />}
            </button>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-slate-800/60">
        <div className="text-[9px] text-slate-600 text-center font-mono uppercase tracking-wider">
          Imagine Cup 2026 · v1.0
        </div>
      </div>
    </aside>
  );
};
