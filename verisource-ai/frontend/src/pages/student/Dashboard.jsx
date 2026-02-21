import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import ModeSelector from '../../components/ModeSelector';
import DocumentSelector from '../../components/DocumentSelector';
import QueryForm from '../../components/QueryForm';
import { documentService } from '../../services/documentService';
import { queryService } from '../../services/queryService';
import { ShieldCheck, AlertCircle } from 'lucide-react';
import { motion } from 'framer-motion';

const Dashboard = () => {
    const [mode, setMode] = useState('');
    const [documents, setDocuments] = useState([]);
    const [selectedDocId, setSelectedDocId] = useState('');
    const [isLoadingDocs, setIsLoadingDocs] = useState(false);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [error, setError] = useState(null);

    const navigate = useNavigate();

    // Fetch documents when mode changes
    useEffect(() => {
        const fetchDocuments = async () => {
            if (!mode) {
                setDocuments([]);
                setSelectedDocId('');
                return;
            }

            setIsLoadingDocs(true);
            setError(null);

            try {
                const data = await documentService.getDocuments(mode);
                // Only show active documents
                const activeDocs = data.filter(doc => doc.active !== false);
                setDocuments(activeDocs);

                // Auto-select if only one document
                if (activeDocs.length === 1) {
                    setSelectedDocId(activeDocs[0].id);
                } else {
                    setSelectedDocId(''); // Clear selection on mode change
                }
            } catch (err) {
                setError('Failed to fetch compliant documents. Verify backend connection.');
            } finally {
                setIsLoadingDocs(false);
            }
        };

        fetchDocuments();
    }, [mode]);

    const handleQuerySubmit = async (queryText) => {
        if (!mode || !selectedDocId) {
            setError('Mode and target corpus must be explicitly defined before submitting a query.');
            return;
        }

        setIsSubmitting(true);
        setError(null);

        try {
            const result = await queryService.submitQuery(selectedDocId, mode, queryText);

            // Navigate to results page with data
            navigate('/student/result', {
                state: {
                    result,
                    query: queryText,
                    document_id: selectedDocId,
                    mode
                }
            });
        } catch (err) {
            setError(err.response?.data?.detail || 'Execution failed. The policy engine rejected the request.');
            setIsSubmitting(false);
        }
    };

    return (
        <div className="h-full flex flex-col md:flex-row overflow-hidden relative">
            {/* Dynamic Background Effects */}
            {mode === 'policy' && (
                <div className="absolute top-0 right-0 w-1/2 h-full bg-blue-500/5 blur-[120px] pointer-events-none transition-all duration-1000"></div>
            )}
            {mode === 'research' && (
                <div className="absolute top-0 right-0 w-1/2 h-full bg-purple-500/5 blur-[120px] pointer-events-none transition-all duration-1000"></div>
            )}

            {/* Left Configuration Panel */}
            <div className="w-full md:w-[350px] lg:w-[400px] border-r border-white/10 bg-brand-navy-light/30 backdrop-blur-sm p-6 flex flex-col gap-8 shrink-0 overflow-y-auto z-10">
                <div>
                    <h2 className="text-2xl font-bold tracking-tight mb-2">Gatekeeper Auth</h2>
                    <p className="text-gray-400 text-sm leading-relaxed">
                        Configure validation parameters. Explicit bounds are strictly enforced by system governance.
                    </p>
                </div>

                {error && (
                    <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        className="p-4 bg-red-500/10 border border-red-500/20 text-red-200 text-sm rounded-xl flex gap-3"
                    >
                        <AlertCircle className="w-5 h-5 flex-shrink-0 text-red-400 -mt-0.5" />
                        <p className="leading-relaxed">{error}</p>
                    </motion.div>
                )}

                <div className="space-y-8">
                    <ModeSelector
                        selectedMode={mode}
                        onModeSelect={setMode}
                    />

                    <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: mode ? 1 : 0.4, y: 0 }}
                        transition={{ duration: 0.3 }}
                    >
                        <DocumentSelector
                            documents={documents}
                            selectedDocumentId={selectedDocId}
                            onDocumentSelect={setSelectedDocId}
                            isLoading={isLoadingDocs}
                            disabled={!mode}
                        />
                    </motion.div>
                </div>

                <div className="mt-auto pt-8 border-t border-white/10">
                    <div className="flex items-start gap-3 p-4 bg-brand-navy/50 rounded-xl border border-white/5">
                        <ShieldCheck className="w-5 h-5 text-gold flex-shrink-0 mt-0.5" />
                        <div>
                            <h4 className="text-sm font-semibold text-white">Strict Governance</h4>
                            <p className="text-xs text-gray-400 leading-relaxed mt-1">Multi-document synthesis is permanently disabled. VeriSource strictly enforces 1:1 evidence mapping.</p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Right Main Interface */}
            <div className="flex-1 p-6 md:p-8 flex flex-col h-full bg-[radial-gradient(circle_at_top_right,_var(--tw-gradient-stops))] from-transparent via-brand-navy-light/10 to-transparent z-10">
                <div className="mb-6 flex items-center justify-between">
                    <h2 className="text-2xl font-bold tracking-tight flex items-center gap-3">
                        Verification Console
                        {mode && (
                            <span className={`text-xs font-bold uppercase tracking-wider px-2.5 py-1 rounded bg-white/10 ${mode === 'policy' ? 'text-blue-400 border border-blue-500/30' : 'text-purple-400 border border-purple-500/30'}`}>
                                {mode} scope
                            </span>
                        )}
                    </h2>
                </div>

                <div className="flex-1 relative">
                    <QueryForm
                        onSubmit={handleQuerySubmit}
                        isSubmitting={isSubmitting}
                        disabled={!mode || !selectedDocId}
                        modeColorClass={mode}
                    />
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
