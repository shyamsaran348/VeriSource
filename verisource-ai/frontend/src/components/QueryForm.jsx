import React, { useState } from 'react';
import { Search, Loader2 } from 'lucide-react';

const QueryForm = ({ onSubmit, isSubmitting, disabled, modeColorClass }) => {
    const [query, setQuery] = useState('');

    const handleKeyDown = (e) => {
        if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
            handleSubmit(e);
        }
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        if (query.trim() && !disabled && !isSubmitting) {
            onSubmit(query.trim());
        }
    };

    const ringClass = modeColorClass === 'policy'
        ? 'focus:ring-blue-500/50'
        : modeColorClass === 'research'
            ? 'focus:ring-purple-500/50'
            : 'focus:ring-gold/50';

    const buttonClass = modeColorClass === 'policy'
        ? 'bg-blue-600 hover:bg-blue-500'
        : modeColorClass === 'research'
            ? 'bg-purple-600 hover:bg-purple-500'
            : 'bg-gold hover:bg-yellow-500 text-brand-navy';

    return (
        <form onSubmit={handleSubmit} className="flex flex-col h-full relative">
            <div className="flex-grow">
                <textarea
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    onKeyDown={handleKeyDown}
                    disabled={disabled || isSubmitting}
                    placeholder={disabled ? "Select Verification Mode and Target Corpus first..." : "Enter verification query based strictly on the selected document..."}
                    className={`w-full h-full min-h-[160px] p-6 bg-brand-navy border border-white/10 rounded-2xl text-white text-lg placeholder-gray-500 resize-none focus:outline-none focus:ring-2 ${ringClass} transition-all disabled:opacity-50 disabled:cursor-not-allowed z-10 relative`}
                />
            </div>

            <div className="absolute bottom-6 right-6 z-20">
                <button
                    type="submit"
                    disabled={disabled || isSubmitting || !query.trim()}
                    className={`flex items-center gap-2 px-6 py-3 rounded-xl font-semibold text-white shadow-lg transition-all transform hover:-translate-y-0.5 disabled:transform-none disabled:opacity-50 disabled:cursor-not-allowed ${buttonClass}`}
                >
                    {isSubmitting ? (
                        <>
                            <Loader2 className="w-5 h-5 animate-spin" />
                            <span>Analyzing...</span>
                        </>
                    ) : (
                        <>
                            <Search className="w-5 h-5" />
                            <span>Verify Claim</span>
                        </>
                    )}
                </button>
            </div>
        </form>
    );
};

export default QueryForm;
