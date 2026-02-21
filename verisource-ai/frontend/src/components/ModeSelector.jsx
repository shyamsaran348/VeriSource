import React from 'react';
import { motion } from 'framer-motion';
import { Shield, Microscope } from 'lucide-react';

const ModeSelector = ({ selectedMode, onModeSelect }) => {
    return (
        <div className="space-y-3">
            <label className="text-sm font-semibold text-gray-400 uppercase tracking-widest pl-1">
                Validation Mode
            </label>
            <div className="grid grid-cols-2 gap-3">
                <button
                    onClick={() => onModeSelect('policy')}
                    className={`relative p-4 rounded-xl border flex flex-col items-center justify-center gap-2 transition-all ${selectedMode === 'policy'
                            ? 'bg-blue-500/10 border-blue-500/50 text-blue-400 shadow-[0_0_15px_rgba(59,130,246,0.1)]'
                            : 'bg-white/5 border-white/10 text-gray-500 hover:bg-white/10 hover:text-gray-300'
                        }`}
                >
                    {selectedMode === 'policy' && (
                        <motion.div layoutId="mode-outline" className="absolute inset-0 border-2 border-blue-500 rounded-xl" />
                    )}
                    <Shield className="w-6 h-6 z-10" />
                    <span className="font-medium z-10">Policy</span>
                </button>

                <button
                    onClick={() => onModeSelect('research')}
                    className={`relative p-4 rounded-xl border flex flex-col items-center justify-center gap-2 transition-all ${selectedMode === 'research'
                            ? 'bg-purple-500/10 border-purple-500/50 text-purple-400 shadow-[0_0_15px_rgba(168,85,247,0.1)]'
                            : 'bg-white/5 border-white/10 text-gray-500 hover:bg-white/10 hover:text-gray-300'
                        }`}
                >
                    {selectedMode === 'research' && (
                        <motion.div layoutId="mode-outline" className="absolute inset-0 border-2 border-purple-500 rounded-xl" />
                    )}
                    <Microscope className="w-6 h-6 z-10" />
                    <span className="font-medium z-10">Research</span>
                </button>
            </div>
        </div>
    );
};

export default ModeSelector;
