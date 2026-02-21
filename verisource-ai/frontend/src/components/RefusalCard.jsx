import React from 'react';
import { ShieldAlert, AlertTriangle } from 'lucide-react';
import { motion } from 'framer-motion';

const RefusalCard = ({ reason, confidence_score }) => {
    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-red-950/30 border border-red-500/40 rounded-2xl p-6 relative overflow-hidden"
        >
            <div className="absolute top-0 right-0 w-full h-full bg-[repeating-linear-gradient(45deg,transparent,transparent_10px,rgba(239,68,68,0.03)_10px,rgba(239,68,68,0.03)_20px)] pointer-events-none"></div>

            <div className="flex items-start gap-4 relative z-10">
                <div className="mt-1 p-3 bg-red-500/20 rounded-xl border border-red-500/30 text-red-500">
                    <ShieldAlert className="w-8 h-8" />
                </div>

                <div>
                    <h3 className="text-xl font-bold text-red-400 mb-2 flex items-center gap-2">
                        System Refused to Answer
                        <span className="px-2 py-0.5 bg-red-500/20 text-red-300 text-xs rounded uppercase tracking-wider border border-red-500/20">
                            Hard Block
                        </span>
                    </h3>

                    <div className="bg-brand-navy-light/80 rounded-lg p-4 border border-red-500/20 mb-4 inline-flex w-full">
                        <AlertTriangle className="w-5 h-5 text-red-400 mr-3 flex-shrink-0 mt-0.5" />
                        <p className="text-red-100 leading-relaxed font-medium">
                            {reason || 'The provided evidence was insufficient, contradictory, or off-topic relative to the explicit document scope.'}
                        </p>
                    </div>

                    <p className="text-sm text-gray-400">
                        VeriSource AI strictly enforces single-document scoping and evidence-first reasoning. Queries that attempt to bypass these guardrails or rely on external knowledge are permanently blocked to prevent hallucination.
                    </p>
                </div>
            </div>
        </motion.div>
    );
};

export default RefusalCard;
