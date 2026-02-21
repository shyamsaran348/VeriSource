import React from 'react';
import { motion } from 'framer-motion';
import { CheckCircle2, XCircle, Clock } from 'lucide-react';
import ConfidenceMeter from './ConfidenceMeter';

const DecisionCard = ({ response }) => {
    const isApproved = response.decision?.toLowerCase() === 'approved';
    const score = response.confidence_score || 0;

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className={`relative overflow-hidden p-6 rounded-2xl border ${isApproved
                ? 'bg-green-950/20 border-green-500/30 shadow-[0_4px_30px_rgba(34,197,94,0.1)]'
                : 'bg-red-950/20 border-red-500/30 shadow-[0_4px_30px_rgba(239,68,68,0.1)]'
                }`}
        >
            {/* Background glow */}
            <div className={`absolute top-0 right-0 w-32 h-32 rounded-full blur-3xl opacity-20 -mr-16 -mt-16 ${isApproved ? 'bg-green-500' : 'bg-red-500'
                }`} />

            <div className="flex items-start justify-between mb-8 relative z-10">
                <div className="flex items-center gap-3">
                    {isApproved ? (
                        <div className="p-2 rounded-full bg-green-500/20 text-green-400">
                            <CheckCircle2 className="w-8 h-8" />
                        </div>
                    ) : (
                        <div className="p-2 rounded-full bg-red-500/20 text-red-400">
                            <XCircle className="w-8 h-8" />
                        </div>
                    )}

                    <div>
                        <h3 className={`text-2xl font-bold ${isApproved ? 'text-green-400' : 'text-red-400'}`}>
                            {isApproved ? 'Verified & Approved' : 'Verification Failed'}
                        </h3>
                        <div className="flex items-center gap-1.5 text-sm text-gray-400 mt-1">
                            <Clock className="w-3.5 h-3.5" />
                            <span>{new Date(response.timestamp || Date.now()).toLocaleString()}</span>
                        </div>
                    </div>
                </div>

                <div className="text-right">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-white/10 text-gray-300 uppercase tracking-wider">
                        {response.mode} Mode
                    </span>
                </div>
            </div>

            <div className="bg-brand-navy-light/50 rounded-xl p-5 border border-white/5 mb-6 relative z-10">
                <h4 className="text-sm font-semibold text-gray-400 uppercase tracking-widest mb-3">System Conclusion</h4>
                <p className="text-white text-lg leading-relaxed">
                    {isApproved ? response.answer : response.reason || 'This query failed to meet the necessary criteria for verification.'}
                </p>
            </div>

            <div className="relative z-10">
                <ConfidenceMeter score={score} threshold={response.mode === 'policy' ? 0.05 : 0.03} />
            </div>
        </motion.div>
    );
};

export default DecisionCard;
