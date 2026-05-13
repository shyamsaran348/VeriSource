import React from 'react';
import { X, CheckCircle2, XCircle, Info, Activity } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const AuditReportModal = ({ isOpen, onClose, results, docName }) => {
    if (!isOpen || !results) return null;

    const score = results.overall_reliability;
    const isHigh = score >= 75;

    return (
        <AnimatePresence>
            <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
                <motion.div 
                    initial={{ opacity: 0, scale: 0.9, y: 20 }}
                    animate={{ opacity: 1, scale: 1, y: 0 }}
                    exit={{ opacity: 0, scale: 0.9, y: 20 }}
                    className="relative w-full max-w-2xl bg-[#0F172A] border border-white/10 rounded-2xl shadow-2xl overflow-hidden"
                >
                    {/* Header */}
                    <div className="p-6 border-b border-white/5 flex justify-between items-center bg-gradient-to-r from-blue-500/10 to-transparent">
                        <div className="flex items-center gap-3">
                            <Activity className="w-5 h-5 text-blue-400" />
                            <div>
                                <h3 className="text-xl font-bold text-white">Reliability Audit Report</h3>
                                <p className="text-xs text-gray-400 font-mono tracking-wider uppercase mt-0.5">{docName}</p>
                            </div>
                        </div>
                        <button onClick={onClose} className="p-2 text-gray-400 hover:text-white hover:bg-white/5 rounded-lg">
                            <X className="w-5 h-5" />
                        </button>
                    </div>

                    {/* Body */}
                    <div className="p-8 space-y-8">
                        {/* Score Section */}
                        <div className="flex items-center justify-between p-6 bg-white/5 rounded-xl border border-white/5">
                            <div className="space-y-1">
                                <span className="text-sm text-gray-400 uppercase tracking-widest font-bold">Overall Reliability</span>
                                <div className="flex items-baseline gap-2">
                                    <span className={`text-5xl font-black ${isHigh ? 'text-emerald-400' : 'text-amber-400'}`}>
                                        {score}%
                                    </span>
                                    <span className="text-gray-500 font-medium">Confidence</span>
                                </div>
                            </div>
                            <div className="text-right space-y-1">
                                <span className="text-sm text-gray-400 uppercase tracking-widest font-bold">Document Clarity</span>
                                <div className={`text-xl font-bold ${isHigh ? 'text-emerald-400' : 'text-amber-400'}`}>
                                    {results.clarity_rating}
                                </div>
                            </div>
                        </div>

                        {/* Stress Tests */}
                        <div className="space-y-4">
                            <h4 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
                                <Info className="w-4 h-4 text-blue-400" />
                                Automated Stress Tests
                            </h4>
                            <div className="grid gap-3">
                                {results.stress_tests.map((test, idx) => (
                                    <div key={idx} className="p-4 bg-white/5 rounded-lg border border-white/5 flex items-start justify-between gap-4">
                                        <div className="space-y-1">
                                            <p className="text-sm text-gray-200 leading-relaxed font-medium italic">"{test.question}"</p>
                                            <div className="flex items-center gap-2">
                                                <span className="text-[10px] text-gray-500 uppercase tracking-tighter">AI Verification Confidence:</span>
                                                <span className="text-[10px] font-mono text-blue-400">{(test.confidence * 100).toFixed(1)}%</span>
                                            </div>
                                        </div>
                                        <div className={`flex items-center gap-1.5 px-2 py-1 rounded text-[10px] uppercase font-black tracking-widest ${
                                            test.status === 'pass' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                                        }`}>
                                            {test.status === 'pass' ? <CheckCircle2 className="w-3 h-3" /> : <XCircle className="w-3 h-3" />}
                                            {test.status}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* Methodology Info */}
                        <div className="p-4 bg-blue-500/5 rounded-lg border border-blue-500/10">
                            <p className="text-[10px] text-blue-300/60 leading-normal italic text-center uppercase tracking-widest">
                                The Meta-RAG audit simulates real-world governance requests by generating synthetic stress-test questions based on document-wide semantic clusters. Failure in a stress test indicates low semantic retrieval density for that specific subject area.
                            </p>
                        </div>
                    </div>
                </motion.div>
            </div>
        </AnimatePresence>
    );
};

export default AuditReportModal;
