import React from 'react';
import { FileText, Loader2, Target } from 'lucide-react';

const DocumentSelector = ({ documents, selectedDocumentId, onDocumentSelect, isLoading, disabled }) => {
    if (!documents && !isLoading) return null;

    return (
        <div className="space-y-3">
            <label className="text-sm font-semibold text-gray-400 uppercase tracking-widest pl-1 flex items-center justify-between">
                <span>Target Corpus</span>
                {isLoading && <Loader2 className="w-4 h-4 animate-spin text-gold" />}
            </label>

            <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Target className={`h-5 w-5 ${disabled ? 'text-gray-600' : 'text-gray-400 group-hover:text-gold transition-colors'}`} />
                </div>

                <select
                    value={selectedDocumentId || ''}
                    onChange={(e) => onDocumentSelect(e.target.value)}
                    disabled={disabled || isLoading}
                    className="block w-full pl-10 pr-10 py-3 bg-brand-navy border border-white/10 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-gold/50 focus:border-transparent transition-all appearance-none cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    <option value="" disabled>
                        {isLoading ? 'Loading documents...' : 'Select explicitly bounded document...'}
                    </option>
                    {documents?.map((doc) => (
                        <option key={doc.document_id} value={doc.document_id}>
                            {doc.document_name} v{doc.version || '1.0'}
                        </option>
                    ))}
                </select>

                <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
                    <svg className={`h-4 w-4 ${disabled ? 'text-gray-600' : 'text-gray-400'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" />
                    </svg>
                </div>
            </div>

            {documents?.length === 0 && !isLoading && (
                <p className="text-xs text-yellow-500 mt-2 flex items-center gap-1 opacity-80">
                    <FileText className="w-3 h-3" />
                    No compliant documents available in this mode.
                </p>
            )}
        </div>
    );
};

export default DocumentSelector;
