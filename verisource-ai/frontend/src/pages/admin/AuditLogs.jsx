import React, { useState, useEffect } from 'react';
import { auditService } from '../../services/auditService';
import DataTable from '../../components/DataTable';
import ReliabilityLeaderboard from '../../components/ReliabilityLeaderboard';
import { Filter, Search, ChevronDown, Download, RefreshCw, BarChart2, List } from 'lucide-react';

const AuditLogs = () => {
    const [logs, setLogs] = useState([]);
    const [reliabilityData, setReliabilityData] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [activeTab, setActiveTab] = useState('logs'); // 'logs' or 'reliability'

    // Filters
    const [filterMode, setFilterMode] = useState('');
    const [filterDecision, setFilterDecision] = useState('');
    const [filterHash, setFilterHash] = useState('');

    useEffect(() => {
        const timer = setTimeout(() => {
            fetchLogs();
        }, 300); // Small debounce for hash search
        return () => clearTimeout(timer);
    }, [filterMode, filterDecision, filterHash]);

    const handleExportCSV = () => {
        if (!logs || logs.length === 0) return;

        const headers = ["Timestamp", "Query Hash", "User ID", "Document ID", "Mode", "Decision", "Confidence Score"];
        const csvContent = [
            headers.join(","),
            ...logs.map(log => [
                log.timestamp,
                log.query_hash,
                log.user_id,
                log.document_id,
                log.mode,
                log.decision,
                log.confidence_score
            ].join(","))
        ].join("\n");

        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement("a");
        const url = URL.createObjectURL(blob);
        link.setAttribute("href", url);
        link.setAttribute("download", `verisource_audit_log_${new Date().toISOString().split('T')[0]}.csv`);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };

    const fetchLogs = async () => {
        setIsLoading(true);
        try {
            const data = await auditService.getLogs({
                mode: filterMode?.trim() || undefined,
                decision: filterDecision?.trim() || undefined,
                query_hash: filterHash?.trim() || undefined
            });
            setLogs(data);
        } catch (error) {
            console.error('Failed to fetch logs:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const fetchReliability = async () => {
        setIsLoading(true);
        try {
            const data = await auditService.getReliability();
            setReliabilityData(data);
        } catch (error) {
            console.error('Failed to fetch reliability data:', error);
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        if (activeTab === 'logs') {
            const timer = setTimeout(() => {
                fetchLogs();
            }, 300);
            return () => clearTimeout(timer);
        } else {
            fetchReliability();
        }
    }, [filterMode, filterDecision, filterHash, activeTab]);

    const columns = [
        {
            header: 'Timestamp',
            accessor: 'timestamp',
            cell: (row) => (
                <div className="font-mono text-xs text-gray-400">
                    {new Date(row.timestamp).toLocaleString(undefined, {
                        year: 'numeric', month: '2-digit', day: '2-digit',
                        hour: '2-digit', minute: '2-digit', second: '2-digit'
                    })}
                </div>
            )
        },
        {
            header: 'Query Hash',
            accessor: 'query_hash',
            cell: (row) => (
                <div className="font-mono text-[10px] text-gray-500 bg-black/30 px-2 py-1 rounded inline-block">
                    {row.query_hash.substring(0, 12)}...
                </div>
            )
        },
        {
            header: 'User / Source',
            accessor: 'user_id',
            cell: (row) => <span className="text-gray-300 text-sm">{row.user_id || 'student_1'}</span>
        },
        {
            header: 'Mode',
            accessor: 'mode',
            cell: (row) => {
                const mode = row.mode?.toLowerCase();
                return (
                    <span className={`text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded border ${mode === 'policy'
                        ? 'text-blue-400 border-blue-500/30 bg-blue-500/10'
                        : 'text-purple-400 border-purple-500/30 bg-purple-500/10'
                        }`}>
                        {row.mode}
                    </span>
                );
            }
        },
        {
            header: 'Decision',
            accessor: 'decision',
            cell: (row) => {
                const decision = row.decision?.toLowerCase();
                const isApproved = decision === 'approved';
                return (
                    <span className={`text-xs font-bold flex items-center gap-1.5 ${isApproved ? 'text-green-400' : 'text-red-400'
                        }`}>
                        <span className={`w-1.5 h-1.5 rounded-full ${isApproved ? 'bg-green-400' : 'bg-red-400'}`}></span>
                        {isApproved ? 'Approved' : 'Refused'}
                    </span>
                );
            }
        },
        {
            header: 'Confidence',
            accessor: 'confidence_score',
            cell: (row) => {
                const score = row.confidence_score * 100;
                return (
                    <div className="flex items-center gap-2 w-24">
                        <div className="text-xs font-mono text-right w-8">{score.toFixed(0)}%</div>
                        <div className="h-1.5 flex-1 bg-white/10 rounded-full overflow-hidden">
                            <div
                                className={`h-full ${score > 75 ? 'bg-green-500' : score > 50 ? 'bg-yellow-500' : 'bg-red-500'}`}
                                style={{ width: `${score}%` }}
                            />
                        </div>
                    </div>
                );
            }
        }
    ];

    return (
        <div className="max-w-7xl mx-auto space-y-6">
            {/* Dashboard Headers */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-8">
                <div>
                    <h2 className="text-3xl font-bold text-white mb-2">Audit Dashboard</h2>
                    <p className="text-gray-400">Governance monitoring & document reliability calibration.</p>
                </div>

                <div className="flex items-center gap-3 bg-brand-navy-light/40 p-1 rounded-xl border border-white/5">
                    <button
                        onClick={() => setActiveTab('logs')}
                        className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold transition-all ${activeTab === 'logs'
                            ? 'bg-gold text-brand-navy shadow-lg shadow-gold/20'
                            : 'text-gray-400 hover:text-white hover:bg-white/5'
                            }`}
                    >
                        <List className="w-4 h-4" />
                        Audit Logs
                    </button>
                    <button
                        onClick={() => setActiveTab('reliability')}
                        className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold transition-all ${activeTab === 'reliability'
                            ? 'bg-gold text-brand-navy shadow-lg shadow-gold/20'
                            : 'text-gray-400 hover:text-white hover:bg-white/5'
                            }`}
                    >
                        <BarChart2 className="w-4 h-4" />
                        Reliability Index
                    </button>
                </div>
            </div>

            {/* Controls Row */}
            <div className="flex flex-wrap items-center gap-4 mb-8">
                {activeTab === 'logs' && (
                    <>
                        <div className="relative">
                            <Filter className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
                            <select
                                value={filterMode}
                                onChange={(e) => setFilterMode(e.target.value)}
                                className="pl-10 pr-8 py-2 bg-brand-navy-light/40 border border-white/10 rounded-lg text-sm text-gray-300 focus:outline-none focus:border-gold/50 appearance-none"
                            >
                                <option value="">All Modes</option>
                                <option value="policy">Policy</option>
                                <option value="research">Research</option>
                            </select>
                        </div>

                        <select
                            value={filterDecision}
                            onChange={(e) => setFilterDecision(e.target.value)}
                            className="px-4 py-2 bg-brand-navy-light/40 border border-white/10 rounded-lg text-sm text-gray-300 focus:outline-none focus:border-gold/50 appearance-none"
                        >
                            <option value="">All Decisions</option>
                            <option value="approved">Approved</option>
                            <option value="refused">Refused</option>
                        </select>
                    </>
                )}

                <button
                    onClick={activeTab === 'logs' ? fetchLogs : fetchReliability}
                    className="flex items-center gap-2 px-3 py-2 bg-white/5 border border-white/10 hover:bg-white/10 rounded-lg text-xs transition-colors text-gray-400 hover:text-white"
                >
                    <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
                    Refresh
                </button>

                {activeTab === 'logs' && (
                    <>
                        <div className="ml-auto relative w-full md:w-64">
                            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
                            <input
                                type="text"
                                value={filterHash}
                                onChange={(e) => setFilterHash(e.target.value)}
                                placeholder="Search by Query Hash..."
                                className="w-full pl-10 pr-4 py-2 bg-brand-navy-light/40 border border-white/10 rounded-lg text-sm text-gray-300 focus:outline-none focus:border-gold/50"
                            />
                        </div>

                        <button
                            onClick={handleExportCSV}
                            disabled={logs.length === 0}
                            className="flex items-center gap-2 px-4 py-2 bg-gold/10 hover:bg-gold/20 border border-gold/30 rounded-lg text-sm font-semibold text-gold transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            <Download className="w-4 h-4" />
                            Export CSV
                        </button>
                    </>
                )}
            </div>

            {/* Analytics/Log Content */}
            {activeTab === 'logs' ? (
                <DataTable
                    columns={columns}
                    data={logs}
                    isLoading={isLoading}
                    emptyMessage="No historical logs match your filters."
                />
            ) : (
                <ReliabilityLeaderboard
                    data={reliabilityData}
                    isLoading={isLoading}
                />
            )}
        </div>
    );
};

export default AuditLogs;
