import React, { useState, useEffect } from 'react';
import { documentService } from '../../services/documentService';
import { auditService } from '../../services/auditService';
import { BarChart3, Users, FileText, AlertTriangle } from 'lucide-react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';

const Dashboard = () => {
    const [stats, setStats] = useState({
        totalDocs: 0,
        activePolicyDocs: 0,
        totalQueries: 0,
        refusalRate: 0,
    });
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchDashboardData = async () => {
            try {
                const [docs, logs] = await Promise.all([
                    documentService.getDocuments(),
                    auditService.getLogs()
                ]);

                const totalQueries = logs.length;
                const refusals = logs.filter(log => log.decision === 'Refused').length;

                setStats({
                    totalDocs: docs.length,
                    activePolicyDocs: docs.filter(doc => doc.mode === 'policy' && doc.active !== false).length,
                    totalQueries,
                    refusalRate: totalQueries > 0 ? Math.round((refusals / totalQueries) * 100) : 0
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
        { label: 'Active Policy Corpus', value: stats.activePolicyDocs, icon: ShieldAlertIcon, color: 'text-green-400', bg: 'bg-green-400/10' },
        { label: 'Total Verifications', value: stats.totalQueries, icon: BarChart3, color: 'text-gold', bg: 'bg-gold/10' },
        { label: 'System Refusal Rate', value: `${stats.refusalRate}%`, icon: AlertTriangle, color: 'text-red-400', bg: 'bg-red-400/10' },
    ];

    return (
        <div className="max-w-7xl mx-auto space-y-8">
            <div>
                <h1 className="text-3xl font-bold tracking-tight mb-2">System Overview</h1>
                <p className="text-gray-400">VeriSource AI Infrastructure Control Panel</p>
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
                        <ShieldAlertIcon className="w-5 h-5 text-gold" />
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

                <div className="bg-brand-navy-light/30 border border-white/5 rounded-2xl p-8">
                    <h3 className="text-xl font-bold mb-6 text-white">System Health</h3>
                    <div className="space-y-6">
                        <div className="flex items-center justify-between border-b border-white/5 pb-4">
                            <div className="flex items-center gap-3">
                                <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                                <span className="text-gray-300">FastAPI Backend</span>
                            </div>
                            <span className="text-green-400 text-sm font-mono">Operational</span>
                        </div>
                        <div className="flex items-center justify-between border-b border-white/5 pb-4">
                            <div className="flex items-center gap-3">
                                <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                                <span className="text-gray-300">ChromaDB Vector Store</span>
                            </div>
                            <span className="text-green-400 text-sm font-mono">Operational</span>
                        </div>
                        <div className="flex items-center justify-between border-b border-white/5 pb-4">
                            <div className="flex items-center gap-3">
                                <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                                <span className="text-gray-300">Supabase Auth/DB</span>
                            </div>
                            <span className="text-green-400 text-sm font-mono">Operational</span>
                        </div>
                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-3">
                                <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                                <span className="text-gray-300">LLM Generation</span>
                            </div>
                            <span className="text-green-400 text-sm font-mono">Governed</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

// Extracted simple shield icon for reuse
const ShieldAlertIcon = ({ className }) => (
    <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
    </svg>
)

export default Dashboard;
