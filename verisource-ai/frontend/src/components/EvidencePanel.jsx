import React from 'react';
import { motion } from 'framer-motion';
import { FileSearch, Link2, Quote } from 'lucide-react';

const EvidencePanel = ({ chunks }) => {
    if (!chunks || chunks.length === 0) return null;

    return (
        <div className="space-y-4">
            <div className="flex items-center gap-2 mb-6">
                <FileSearch className="w-5 h-5 text-gold" />
                <h3 className="text-lg font-bold text-white">Retrieved Cryptographic Evidence</h3>
                <span className="ml-2 text-xs font-mono bg-white/10 px-2 py-0.5 rounded text-gray-400">
                    {chunks.length} chunks sourced
                </span>
            </div>

            <div className="space-y-4">
                {chunks.map((chunk, index) => (
                    <motion.div
                        key={index}
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: index * 0.1 }}
                        className="group relative bg-brand-navy-light/40 border border-white/10 rounded-xl p-5 hover:bg-brand-navy-light/60 hover:border-white/20 transition-all"
                    >
                        {/* Semantic linking indicator */}
                        <div className="absolute -left-2 top-6 w-4 h-4 bg-brand-navy border-2 border-gold rounded-full z-10 shadow-[0_0_10px_rgba(197,162,77,0.5)]"></div>

                        <div className="flex justify-between items-start mb-3">
                            <div className="flex items-center gap-2 text-gold">
                                <Quote className="w-4 h-4" />
                                <span className="text-xs font-bold uppercase tracking-wider">Verified Extract {index + 1}</span>
                            </div>

                            {chunk.similarity && (
                                <div className="flex items-center gap-1.5 text-xs text-brand-navy bg-gold/90 px-2 py-1 rounded font-medium shadow-sm">
                                    <Link2 className="w-3 h-3" />
                                    Match: {(chunk.similarity * 100).toFixed(1)}%
                                </div>
                            )}
                        </div>

                        <div className="text-gray-300 text-sm leading-relaxed border-l-2 border-white/10 pl-4 py-1 italic">
                            "{chunk.text || chunk.content}"
                        </div>

                        {(chunk.metadata || chunk.page) && (
                            <div className="mt-4 pt-3 border-t border-white/5 flex gap-3 text-xs text-gray-500">
                                {chunk.page && <span>Page: {chunk.page}</span>}
                                {chunk.metadata && <span>ID: <span className="font-mono text-[10px]">{chunk.metadata.id || chunk.id || 'N/A'}</span></span>}
                            </div>
                        )}
                    </motion.div>
                ))}
            </div>

            {/* Decorative timeline wire */}
            <div className="absolute left-6 top-16 bottom-16 w-px bg-gradient-to-b from-gold/50 via-gold/20 to-transparent -z-10"></div>
        </div>
    );
};

export default EvidencePanel;
