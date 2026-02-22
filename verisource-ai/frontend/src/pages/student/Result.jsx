import React from 'react';
import { useLocation, useNavigate, Navigate } from 'react-router-dom';
import DecisionCard from '../../components/DecisionCard';
import EvidencePanel from '../../components/EvidencePanel';
import RefusalCard from '../../components/RefusalCard';
import { ArrowLeft, RefreshCw, FileText } from 'lucide-react';
import { motion } from 'framer-motion';

const Result = () => {
    const location = useLocation();
    const navigate = useNavigate();

    // Validate state
    if (!location.state || !location.state.result) {
        return <Navigate to="/student/dashboard" replace />;
    }

    const { result, query, mode } = location.state;
    const isApproved = result.decision?.toLowerCase() === 'approved';

    return (
        <div className="h-full overflow-y-auto w-full relative">
            {/* Background glow effects based on decision */}
            <div className={`fixed top-0 right-0 w-[800px] h-[800px] rounded-full blur-[150px] pointer-events-none opacity-[0.15] z-0 ${isApproved ? 'bg-green-500' : 'bg-red-500'
                }`} />

            <div className="max-w-7xl mx-auto p-6 md:p-10 relative z-10">
                {/* Header Actions */}
                <div className="flex items-center justify-between mb-8">
                    <button
                        onClick={() => navigate('/student/dashboard')}
                        className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors bg-brand-navy-light/40 hover:bg-brand-navy-light px-4 py-2 rounded-xl border border-white/5"
                    >
                        <ArrowLeft className="w-5 h-5" />
                        <span className="font-semibold">New Verification</span>
                    </button>

                    <button
                        onClick={() => window.print()}
                        className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors p-2"
                        title="Export Audit Log"
                    >
                        <FileText className="w-5 h-5" />
                    </button>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-12 gap-10">
                    {/* Main Content Area */}
                    <div className="lg:col-span-7 space-y-8">
                        <motion.div
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="bg-brand-navy-light/30 border border-white/10 rounded-2xl p-6 backdrop-blur-sm"
                        >
                            <h4 className="text-sm font-semibold text-gray-400 uppercase tracking-widest mb-3 flex items-center gap-2">
                                <RefreshCw className="w-4 h-4 text-gold" />
                                Original Query
                            </h4>
                            <p className="text-xl text-white leading-relaxed font-serif">
                                "{query}"
                            </p>
                        </motion.div>

                        {isApproved ? (
                            <DecisionCard response={result} />
                        ) : (
                            <RefusalCard
                                reason={result.reason}
                                confidence_score={result.confidence_score}
                                explanation={result.explanation}
                            />
                        )}

                        {(!isApproved || result.decision?.toLowerCase() === 'refused') && result.confidence_score > 0 && (
                            <div className="mt-8">
                                <h4 className="text-sm font-semibold text-gray-400 uppercase tracking-widest mb-4">Post-Mortem Analysis</h4>
                                <div className="bg-brand-navy-light/20 border border-white/5 rounded-2xl p-6">
                                    <EvidencePanel chunks={result.evidence || []} />
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Sidebar Area - Evidence (shown if approved, or if refused with chunks but usually separated) */}
                    <div className="lg:col-span-5 relative">
                        <div className="sticky top-10">
                            {isApproved && (
                                <div className="bg-brand-navy-light/20 border border-white/5 rounded-2xl p-6 relative">
                                    <EvidencePanel chunks={result.evidence} />
                                </div>
                            )}

                            {/* Diagnostic Meta Info */}
                            <motion.div
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                transition={{ delay: 0.5 }}
                                className="mt-8 p-5 bg-black/20 rounded-xl border border-white/5"
                            >
                                <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-widest mb-3">Diagnostic Metadata</h4>
                                <div className="space-y-2 text-xs font-mono text-gray-400">
                                    <div className="flex justify-between">
                                        <span>Transaction ID</span>
                                        <span className="text-gray-300">{result.query_hash?.substring(0, 16)}...</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span>Logged At</span>
                                        <span className="text-gray-300">
                                            {result.timestamp ? new Date(result.timestamp).toLocaleTimeString() : 'N/A'}
                                        </span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span>Policy Mode</span>
                                        <span className={mode === 'policy' ? 'text-blue-400' : 'text-purple-400'}>{mode.toUpperCase()}</span>
                                    </div>
                                </div>
                            </motion.div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Result;
