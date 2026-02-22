import React from 'react';
import { ShieldAlert, AlertTriangle, Compass, CheckCircle2 } from 'lucide-react';
import { motion } from 'framer-motion';

const RefusalCard = ({ reason, confidence_score, explanation }) => {
    const missingElements = explanation?.missing_evidence_requirements || [];

    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-red-950/30 border border-red-500/40 rounded-2xl p-6 relative overflow-hidden"
        >
            <div className="absolute top-0 right-0 w-full h-full bg-[repeating-linear-gradient(45deg,transparent,transparent_10px,rgba(239,68,68,0.03)_10px,rgba(239,68,68,0.03)_20px)] pointer-events-none"></div>

            <div className="flex flex-col lg:flex-row items-start gap-8 relative z-10">
                <div className="flex-1">
                    <div className="flex items-start gap-4 mb-6">
                        <div className="p-3 bg-red-500/20 rounded-xl border border-red-500/30 text-red-500">
                            <ShieldAlert className="w-8 h-8" />
                        </div>
                        <div>
                            <h3 className="text-xl font-bold text-red-400 mb-2 flex items-center gap-2">
                                System Refused to Answer
                                <span className="px-2 py-0.5 bg-red-500/20 text-red-300 text-xs rounded uppercase tracking-wider border border-red-500/20">
                                    Hard Block
                                </span>
                            </h3>

                            <div className="bg-brand-navy-light/80 rounded-lg p-4 border border-red-500/20 inline-flex w-full">
                                <AlertTriangle className="w-5 h-5 text-red-400 mr-3 flex-shrink-0 mt-0.5" />
                                <p className="text-red-100 leading-relaxed font-medium text-sm">
                                    {reason || 'The provided evidence was insufficient, contradictory, or off-topic relative to the explicit document scope.'}
                                </p>
                            </div>
                        </div>
                    </div>

                    <p className="text-sm text-gray-400 leading-relaxed italic border-l-2 border-red-500/20 pl-4">
                        VeriSource AI strictly enforces single-document scoping. Queries that attempt to bypass guardrails or rely on external knowledge are permanently blocked to prevent hallucination.
                    </p>
                </div>

                {/* Compass / Transition Layer */}
                {missingElements.length > 0 && (
                    <motion.div
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.3 }}
                        className="w-full lg:w-80 bg-brand-navy-light/40 rounded-2xl border border-white/10 p-5 backdrop-blur-md"
                    >
                        <h4 className="text-xs font-bold text-gold uppercase tracking-[0.2em] mb-4 flex items-center gap-2">
                            <Compass className="w-4 h-4 animate-pulse" />
                            Counterfactual Guide
                        </h4>

                        <p className="text-[11px] text-gray-400 mb-4 leading-tight">
                            The system would have approved this query if the document contained:
                        </p>

                        <ul className="space-y-3">
                            {missingElements.map((item, idx) => (
                                <li key={idx} className="flex items-start gap-3">
                                    <div className="mt-1 w-1.5 h-1.5 rounded-full bg-red-500/40 border border-red-500/20 flex-shrink-0" />
                                    <span className="text-xs text-red-200/80 leading-snug">
                                        {item}
                                    </span>
                                </li>
                            ))}
                        </ul>

                        <div className="mt-6 pt-4 border-t border-white/5">
                            <div className="flex items-center justify-between text-[10px] font-mono text-gray-500">
                                <span>Calibrated Gate</span>
                                <span className="text-gray-400">{explanation.mode_threshold_context?.calibrated_gate} similarities</span>
                            </div>
                        </div>
                    </motion.div>
                )}
            </div>
        </motion.div>
    );
};

export default RefusalCard;
