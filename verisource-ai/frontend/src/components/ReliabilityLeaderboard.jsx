import React from 'react';
import { motion } from 'framer-motion';
import { ShieldCheck, AlertCircle, TrendingUp, BarChart2, Activity } from 'lucide-react';

const ReliabilityLeaderboard = ({ data, isLoading }) => {
    if (isLoading) {
        return (
            <div className="w-full bg-brand-navy-light/20 border border-white/10 rounded-xl p-12 flex flex-col justify-center items-center">
                <Activity className="w-8 h-8 text-gold animate-pulse mb-4" />
                <span className="text-gray-400">Analyzing Document Reliability...</span>
            </div>
        );
    }

    if (!data || data.length === 0) {
        return (
            <div className="w-full bg-brand-navy-light/20 border border-white/10 rounded-xl p-12 flex justify-center items-center text-gray-400">
                No reliability data available yet. Start querying to generate metrics.
            </div>
        );
    }

    return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {data.map((item, index) => (
                <motion.div
                    key={item.document_id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="bg-brand-navy-light/30 border border-white/10 rounded-2xl p-6 relative overflow-hidden group hover:border-gold/30 transition-all"
                >
                    <div className="absolute top-0 right-0 p-4">
                        <span className={`text-[10px] uppercase font-bold tracking-widest px-2 py-0.5 rounded border ${item.status === 'stable' ? 'text-green-400 border-green-500/30 bg-green-500/10' :
                                item.status === 'evaluating' ? 'text-blue-400 border-blue-500/30 bg-blue-500/10' :
                                    'text-red-400 border-red-500/30 bg-red-500/10'
                            }`}>
                            {item.status}
                        </span>
                    </div>

                    <h3 className="text-lg font-bold text-white mb-1 truncate pr-16" title={item.title}>
                        {item.title}
                    </h3>
                    <p className="text-[10px] text-gray-500 font-mono mb-6 uppercase tracking-wider">
                        ID: {item.document_id.substring(0, 8)}...
                    </p>

                    <div className="mb-6">
                        <div className="flex justify-between items-end mb-2">
                            <span className="text-xs text-gray-400 font-medium">Reliability Index</span>
                            <span className={`text-2xl font-black font-mono ${item.reliability_index > 0.7 ? 'text-green-400' :
                                    item.reliability_index > 0.4 ? 'text-blue-400' : 'text-red-400'
                                }`}>
                                {(item.reliability_index * 100).toFixed(0)}%
                            </span>
                        </div>
                        <div className="w-full h-1.5 bg-white/5 rounded-full overflow-hidden">
                            <motion.div
                                initial={{ width: 0 }}
                                animate={{ width: `${item.reliability_index * 100}%` }}
                                className={`h-full ${item.reliability_index > 0.7 ? 'bg-green-500 shadow-[0_0_10px_rgba(34,197,94,0.3)]' :
                                        item.reliability_index > 0.4 ? 'bg-blue-500' : 'bg-red-500'
                                    }`}
                            />
                        </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <div className="bg-white/5 rounded-xl p-3 border border-white/5">
                            <div className="flex items-center gap-2 text-[10px] text-gray-500 uppercase tracking-wider mb-1">
                                <ShieldCheck className="w-3 h-3 text-green-500" />
                                Approvals
                            </div>
                            <div className="text-sm font-bold text-gray-200">
                                {(item.approval_rate * 100).toFixed(1)}%
                            </div>
                        </div>

                        <div className="bg-white/5 rounded-xl p-3 border border-white/5">
                            <div className="flex items-center gap-2 text-[10px] text-gray-500 uppercase tracking-wider mb-1">
                                <AlertCircle className={`w-3 h-3 ${item.conflict_rate > 0.2 ? 'text-red-500' : 'text-gray-500'}`} />
                                Conflicts
                            </div>
                            <div className="text-sm font-bold text-gray-200">
                                {(item.conflict_rate * 100).toFixed(1)}%
                            </div>
                        </div>
                    </div>

                    <div className="mt-4 flex items-center justify-between text-[10px] text-gray-500 font-mono">
                        <div className="flex items-center gap-1">
                            <TrendingUp className="w-3 h-3" />
                            {item.total_queries} Samples
                        </div>
                        <div className="flex items-center gap-1">
                            <BarChart2 className="w-3 h-3" />
                            {item.avg_confidence.toFixed(2)} Avg Conf
                        </div>
                    </div>
                </motion.div>
            ))}
        </div>
    );
};

export default ReliabilityLeaderboard;
