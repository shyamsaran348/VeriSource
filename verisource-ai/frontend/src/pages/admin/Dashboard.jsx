import React, { useState, useEffect } from 'react';
import { documentService } from '../../services/documentService';
import { auditService } from '../../services/auditService';
import { BarChart3, FileText, AlertTriangle, Activity, ShieldCheck, ChevronRight } from 'lucide-react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';

const Dashboard = () => {
    const [stats, setStats] = useState({
        totalDocs: 0,
        activePolicyDocs: 0,
        totalQueries: 0,
        refusalRate: 0,
        systemReliability: 0,
    });
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchDashboardData = async () => {
            try {
                const [docs, logs, reliability] = await Promise.all([
                    documentService.getDocuments(),
                    auditService.getLogs(),
                    auditService.getReliability()
                ]);

                const totalQueries = logs.length;
                const refusals = logs.filter(log => log.decision?.toLowerCase() === 'refused').length;

                // Aggregate reliability
                const avgReliability = reliability.length > 0
                    ? reliability.reduce((acc, curr) => acc + curr.reliability_index, 0) / reliability.length
                    : 0;

                setStats({
                    totalDocs: docs.length,
                    activePolicyDocs: docs.filter(doc => (doc.mode === 'policy' || doc.is_active)).length,
                    totalQueries,
                    refusalRate: totalQueries > 0 ? Math.round((refusals / totalQueries) * 100) : 0,
                    systemReliability: Math.round(avgReliability * 100)
                });
            } catch (error) {
                console.error("Failed to load admin stats", error);
            } finally {
                setLoading(false);
            }
        };

        fetchDashboardData();
    }, []);

    const statCards = [
        { label: 'Total Documents', value: stats.totalDocs, icon: FileText, color: 'text-blue-400', bg: 'bg-blue-400/10' },
        { label: 'Active Policy Corpus', value: stats.activePolicyDocs, icon: ShieldCheck, color: 'text-green-400', bg: 'bg-green-400/10' },
        { label: 'Total Verifications', value: stats.totalQueries, icon: BarChart3, color: 'text-gold', bg: 'bg-gold/10' },
        { label: 'System Refusal Rate', value: `${stats.refusalRate}%`, icon: AlertTriangle, color: 'text-red-400', bg: 'bg-red-400/10' },
    ];

    return (
        <div className="max-w-7xl mx-auto space-y-8">
            <div className="flex justify-between items-end">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight mb-2">System Overview</h1>
                    <p className="text-gray-400">VeriSource AI Infrastructure Control Panel</p>
                </div>

                <motion.div
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="bg-brand-navy-light/40 border border-white/5 p-4 rounded-2xl flex items-center gap-6"
                >
                    <div className="text-right">
                        <p className="text-[10px] text-gray-500 uppercase font-bold tracking-widest mb-1">System Trust Score</p>
                        <p className={`text-2xl font-black font-mono ${stats.systemReliability > 70 ? 'text-green-400' : stats.systemReliability > 40 ? 'text-blue-400' : 'text-red-400'}`}>
                            {loading ? '--' : stats.systemReliability}%
                        </p>
                    </div>
                    <div className="w-12 h-12 rounded-full border-2 border-white/5 flex items-center justify-center relative">
                        <Activity className={`w-6 h-6 ${stats.systemReliability > 70 ? 'text-green-500' : 'text-gold'} animate-pulse`} />
                        <svg className="absolute inset-0 w-full h-full -rotate-90">
                            <circle
                                cx="24"
                                cy="24"
                                r="22"
                                fill="none"
                                stroke="currentColor"
                                strokeWidth="2"
                                className="text-white/5"
                            />
                            <motion.circle
                                cx="24"
                                cy="24"
                                r="22"
                                fill="none"
                                stroke="currentColor"
                                strokeWidth="2"
                                strokeDasharray="138"
                                initial={{ strokeDashoffset: 138 }}
                                animate={{ strokeDashoffset: 138 - (138 * stats.systemReliability) / 100 }}
                                className={stats.systemReliability > 70 ? 'text-green-500' : stats.systemReliability > 40 ? 'text-gold' : 'text-red-500'}
                            />
                        </svg>
                    </div>
                </motion.div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {statCards.map((stat, i) => {
                    const Icon = stat.icon;
                    return (
                        <motion.div
                            key={i}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: i * 0.1 }}
                            className="bg-brand-navy-light/40 border border-white/5 rounded-2xl p-6 relative overflow-hidden group hover:border-white/10 transition-colors"
                        >
                            <div className="flex items-start justify-between relative z-10">
                                <div>
                                    <p className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-1">{stat.label}</p>
                                    <h3 className="text-4xl font-bold text-white group-hover:text-transparent group-hover:bg-clip-text group-hover:bg-gradient-to-r group-hover:from-white group-hover:to-gray-400 transition-all">
                                        {loading ? '-' : stat.value}
                                    </h3>
                                </div>
                                <div className={`p-3 rounded-xl ${stat.bg} ${stat.color}`}>
                                    <Icon className="w-6 h-6" />
                                </div>
                            </div>
                            <div className={`absolute -bottom-6 -right-6 w-24 h-24 rounded-full blur-2xl opacity-20 ${stat.bg.replace('/10', '')}`} />
                        </motion.div>
                    );
                })}
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mt-8">
                <div className="bg-brand-navy-light/30 border border-white/5 rounded-2xl p-8">
                    <h3 className="text-xl font-bold mb-6 flex items-center gap-2">
                        <Activity className="w-5 h-5 text-gold" />
                        Quick Actions
                    </h3>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        <Link to="/admin/upload" className="p-4 bg-white/5 border border-white/10 rounded-xl hover:bg-white/10 transition-colors text-center group">
                            <div className="w-10 h-10 mx-auto bg-brand-navy rounded-full flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
                                <FileText className="w-5 h-5 text-gold" />
                            </div>
                            <span className="font-semibold block">Ingest Document</span>
                            <span className="text-xs text-gray-500 mt-1 block">Process & Index new corpus</span>
                        </Link>

                        <Link to="/admin/audit" className="p-4 bg-white/5 border border-white/10 rounded-xl hover:bg-white/10 transition-colors text-center group">
                            <div className="w-10 h-10 mx-auto bg-brand-navy rounded-full flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
                                <AlertTriangle className="w-5 h-5 text-red-400" />
                            </div>
                            <span className="font-semibold block">View Audit Logs</span>
                            <span className="text-xs text-gray-500 mt-1 block">Monitor system decisions</span>
                        </Link>
                    </div>
                </div>

                <div className="bg-brand-navy-light/30 border border-white/5 rounded-2xl p-8 group cursor-pointer hover:border-gold/30 transition-all relative">
                    <Link to="/admin/audit" className="absolute inset-0 z-10" />
                    <div className="flex justify-between items-start mb-6">
                        <h3 className="text-xl font-bold text-white flex items-center gap-2">
                            <ShieldCheck className="w-5 h-5 text-green-500" />
                            Reliability Calibration
                        </h3>
                        <ChevronRight className="w-5 h-5 text-gray-500 group-hover:text-gold transition-colors" />
                    </div>

                    <div className="space-y-4">
                        <p className="text-sm text-gray-400 leading-relaxed">
                            Empirical trust score of the entire policy corpus based on historical audit trails.
                        </p>
                        <div className="flex items-center gap-4">
                            <div className="flex-1 h-2 bg-white/5 rounded-full overflow-hidden">
                                <motion.div
                                    initial={{ width: 0 }}
                                    animate={{ width: `${stats.systemReliability}%` }}
                                    className={`h-full ${stats.systemReliability > 70 ? 'bg-green-500' : 'bg-gold'}`}
                                />
                            </div>
                            <span className="text-xs font-mono text-gray-500">{stats.systemReliability}% TOTAL</span>
                        </div>
                        <p className="text-[10px] text-gray-500 uppercase tracking-widest">
                            {stats.systemReliability > 70 ? 'CORPUS STABLE' : 'CALIBRATION REQUIRED'} • AUGMENTED DECISION LOGS
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
