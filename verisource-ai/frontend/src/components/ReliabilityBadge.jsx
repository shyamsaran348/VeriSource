import React from 'react';
import { ShieldCheck, ShieldAlert, Zap } from 'lucide-react';

const ReliabilityBadge = ({ results, onClick }) => {
    if (!results) return (
        <div className="flex items-center gap-1.5 px-2 py-1 bg-gray-500/10 border border-gray-500/20 rounded text-[10px] text-gray-500 uppercase font-bold">
            Not Audited
        </div>
    );

    const score = results.overall_reliability;
    const isHigh = score >= 75;
    const isLow = score < 40;

    return (
        <button 
            onClick={() => onClick && onClick(results)}
            className={`flex items-center gap-1.5 px-2 py-1 rounded border transition-all hover:scale-105 active:scale-95 ${
                isHigh ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400' :
                isLow ? 'bg-rose-500/10 border-rose-500/30 text-rose-400' :
                'bg-amber-500/10 border-amber-500/30 text-amber-400'
            }`}
        >
            {isHigh ? <ShieldCheck className="w-3 h-3" /> : isLow ? <ShieldAlert className="w-3 h-3" /> : <Zap className="w-3 h-3" />}
            <span className="text-xs font-bold tracking-tight">{score}%</span>
        </button>
    );
};

export default ReliabilityBadge;
