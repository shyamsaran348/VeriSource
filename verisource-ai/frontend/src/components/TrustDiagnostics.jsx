import React from 'react';
import { motion } from 'framer-motion';
import { Target, Users, ShieldCheck } from 'lucide-react';

const DiagnosticBar = ({ label, value, icon: Icon, color }) => (
    <div className="flex flex-col gap-2">
        <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-[10px] font-bold text-gray-500 uppercase tracking-widest">
                <Icon className="w-3 h-3" />
                {label}
            </div>
            <span className={`text-xs font-mono font-bold ${color}`}>
                {(value * 100).toFixed(1)}%
            </span>
        </div>
        <div className="h-1.5 w-full bg-white/5 rounded-full overflow-hidden">
            <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${value * 100}%` }}
                className={`h-full ${color.replace('text-', 'bg-')}`}
            />
        </div>
    </div>
);

const TrustDiagnostics = ({ diagnostics }) => {
    if (!diagnostics) return null;

    return (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6 pt-6 border-t border-white/5">
            <DiagnosticBar 
                label="Retrieval Focus" 
                value={diagnostics.focus_score} 
                icon={Target} 
                color="text-blue-400"
            />
            <DiagnosticBar 
                label="Evidence Consensus" 
                value={diagnostics.consensus_score} 
                icon={Users} 
                color="text-purple-400"
            />
            
            <div className="md:col-span-2 flex items-center justify-between px-4 py-2 bg-white/5 rounded-lg border border-white/5">
                <div className="flex items-center gap-2">
                    <ShieldCheck className="w-4 h-4 text-gold" />
                    <span className="text-[10px] font-bold text-gray-400 uppercase tracking-[0.2em]">Governance Integrity</span>
                </div>
                <span className="text-[10px] font-mono text-gold/60">
                    Validated by Formal Statistical Gating
                </span>
            </div>
        </div>
    );
};

export default TrustDiagnostics;
