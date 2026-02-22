import React, { useState, useEffect } from 'react';
import { auditService } from '../../services/auditService';
import DataTable from '../../components/DataTable';
import { Filter, Search, ChevronDown, Download } from 'lucide-react';

const AuditLogs = () => {
    const [logs, setLogs] = useState([]);
    const [isLoading, setIsLoading] = useState(true);

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
                mode: filterMode || undefined,
                decision: filterDecision || undefined,
                query_hash: filterHash || undefined
            });
            setLogs(data);
        } catch (error) {
            console.error("Failed to fetch audit logs", error);
        } finally {
            setIsLoading(false);
        }
    };

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
            cell: (row) => (
                <span className={`text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded border ${row.mode === 'policy'
                    ? 'text-blue-400 border-blue-500/30 bg-blue-500/10'
                    : 'text-purple-400 border-purple-500/30 bg-purple-500/10'
                    }`}>
                    {row.mode}
                </span>
            )
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
            <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-4 mb-2">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight mb-2">Immutable Audit Trail</h1>
                    <p className="text-gray-400">Cryptographically logged system decisions and interactions.</p>
                </div>

                <button
                    onClick={handleExportCSV}
                    disabled={logs.length === 0}
                    className="flex items-center gap-2 px-4 py-2 bg-brand-navy border border-white/10 hover:bg-white/5 rounded-lg text-sm transition-colors text-white disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    <Download className="w-4 h-4" />
                    Export CSV
                </button>
            </div>

            <div className="bg-brand-navy-light/30 border border-white/5 rounded-xl p-4 flex flex-wrap gap-4 items-center">
                <div className="flex items-center gap-2 text-sm font-semibold text-gray-400 mr-2">
                    <Filter className="w-4 h-4" />
                    FILTERS
                </div>

                <select
                    value={filterMode}
                    onChange={(e) => setFilterMode(e.target.value)}
                    className="bg-brand-navy border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-gold"
                >
                    <option value="">All Modes</option>
                    <option value="policy">Policy Mode</option>
                    <option value="research">Research Mode</option>
                </select>

                <select
                    value={filterDecision}
                    onChange={(e) => setFilterDecision(e.target.value)}
                    className="bg-brand-navy border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-gold"
                >
                    <option value="">All Decisions</option>
                    <option value="approved">Approved</option>
                    <option value="refused">Refused</option>
                </select>

                <div className="ml-auto relative">
                    <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
                    <input
                        type="text"
                        value={filterHash}
                        onChange={(e) => setFilterHash(e.target.value)}
                        placeholder="Search by hash..."
                        className="bg-brand-navy border border-white/10 rounded-lg pl-9 pr-3 py-2 text-sm text-white focus:outline-none focus:border-gold w-48 focus:w-64 transition-all"
                    />
                </div>
            </div>

            <DataTable
                columns={columns}
                data={logs}
                isLoading={isLoading}
                emptyMessage="No audit logs match current filters."
            />
        </div>
    );
};

export default AuditLogs;
