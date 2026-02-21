import React, { useState, useEffect } from 'react';
import { documentService } from '../../services/documentService';
import DataTable from '../../components/DataTable';
import { Shield, Microscope, Trash2 } from 'lucide-react';

const Documents = () => {
    const [documents, setDocuments] = useState([]);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        fetchDocuments();
    }, []);

    const fetchDocuments = async () => {
        setIsLoading(true);
        try {
            const data = await documentService.getDocuments();
            setDocuments(data);
        } catch (error) {
            console.error("Failed to fetch documents", error);
        } finally {
            setIsLoading(false);
        }
    };

    const columns = [
        {
            header: 'Document Name',
            accessor: 'document_name',
            cell: (row) => (
                <div className="font-medium text-white">
                    {row.document_name}
                    {!row.active && <span className="ml-2 px-1.5 py-0.5 bg-gray-500/20 text-gray-400 text-[10px] rounded border border-gray-500/30 uppercase">Inactive</span>}
                </div>
            )
        },
        {
            header: 'Mode',
            accessor: 'mode',
            cell: (row) => (
                <div className="flex items-center gap-1.5">
                    {row.mode === 'policy' ? (
                        <Shield className="w-4 h-4 text-blue-400" />
                    ) : (
                        <Microscope className="w-4 h-4 text-purple-400" />
                    )}
                    <span className={`text-xs uppercase font-bold tracking-wider ${row.mode === 'policy' ? 'text-blue-400' : 'text-purple-400'}`}>
                        {row.mode}
                    </span>
                </div>
            )
        },
        {
            header: 'Version',
            accessor: 'version',
            cell: (row) => <span className="text-gray-400 font-mono text-xs">{row.version || '1.0'}</span>
        },
        {
            header: 'Authority',
            accessor: 'authority',
            cell: (row) => <span className="text-gray-300">{row.authority || 'N/A'}</span>
        },
        {
            header: 'Indexed At',
            accessor: 'created_at',
            cell: (row) => <span className="text-gray-400 text-sm">{new Date(row.created_at).toLocaleDateString()}</span>
        },
        {
            header: 'Actions',
            cell: (row) => (
                <button
                    onClick={async () => {
                        if (window.confirm('Are you sure you want to delete this document? This will also remove its vector embeddings.')) {
                            try {
                                await documentService.deleteDocument(row.document_id);
                                fetchDocuments(); // Refresh the list
                            } catch (err) {
                                alert('Failed to delete document');
                            }
                        }
                    }}
                    className="p-1.5 text-gray-500 hover:text-red-400 hover:bg-red-500/10 rounded transition-colors"
                    title="Delete or Archive Document"
                >
                    <Trash2 className="w-4 h-4" />
                </button>
            )
        }
    ];

    return (
        <div className="max-w-7xl mx-auto space-y-8">
            <div className="flex justify-between items-end">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight mb-2">Corpus Management</h1>
                    <p className="text-gray-400">Manage indexed knowledge and semantic embeddings.</p>
                </div>
            </div>

            <DataTable
                columns={columns}
                data={documents}
                isLoading={isLoading}
                emptyMessage="No documents have been ingested yet. Use the Ingestion flow to add knowledge."
            />
        </div>
    );
};

export default Documents;
