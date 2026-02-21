import React from 'react';
import { motion } from 'framer-motion';
import { Database, FileText, Lock, Hash } from 'lucide-react';

const LoaderPipeline = ({ step, progress }) => {
    const steps = [
        { id: 1, name: 'Parsing Document', icon: FileText, desc: 'Extracting raw text from source' },
        { id: 2, name: 'Cryptographic Hashing', icon: Hash, desc: 'Generating SHA-256 integrity hash' },
        { id: 3, name: 'Semantic Chunking', icon: Database, desc: 'Splitting into knowledge fragments' },
        { id: 4, name: 'Vector Embedding', icon: Lock, desc: 'Generating embeddings in Chroma' },
    ];

    return (
        <div className="w-full bg-brand-navy-light/30 border border-white/5 rounded-2xl p-8 backdrop-blur-md">
            <h3 className="text-xl font-bold text-white mb-8 text-center">Ingestion Pipeline Active</h3>

            <div className="relative max-w-2xl mx-auto pl-4 md:pl-0">
                {/* Connecting Line (Mobile: left, Desktop: top) */}
                <div className="absolute top-0 bottom-0 left-[27px] w-0.5 md:w-full md:h-0.5 md:top-[28px] md:left-0 md:bottom-auto bg-white/10 z-0" />

                {/* Animated Progress Line */}
                <motion.div
                    className="absolute top-0 bottom-auto left-[27px] w-0.5 md:w-full md:h-0.5 md:top-[28px] md:left-0 bg-gold z-0"
                    initial={{ height: 0, width: 0 }}
                    animate={{
                        height: window.innerWidth < 768 ? `${((step - 1) / (steps.length - 1)) * 100}%` : 'auto',
                        width: window.innerWidth >= 768 ? `${((step - 1) / (steps.length - 1)) * 100}%` : 'auto'
                    }}
                    transition={{ duration: 0.5 }}
                />

                <div className="flex flex-col md:flex-row justify-between gap-8 md:gap-0 relative z-10">
                    {steps.map((s, i) => {
                        const isCompleted = step > s.id;
                        const isCurrent = step === s.id;
                        const isPending = step < s.id;

                        const Icon = s.icon;

                        return (
                            <div key={s.id} className="flex md:flex-col items-center gap-4 md:gap-3 group md:w-1/4">
                                <div className={`
                  w-14 h-14 rounded-xl flex items-center justify-center border-2 transition-all duration-300 relative bg-brand-navy shadow-lg
                  ${isCompleted ? 'border-green-500 text-green-400' :
                                        isCurrent ? 'border-gold text-gold shadow-[0_0_20px_rgba(197,162,77,0.3)]' :
                                            'border-white/10 text-gray-500'}
                `}>
                                    <Icon className={`w-6 h-6 ${isCurrent ? 'animate-pulse' : ''}`} />

                                    {isCurrent && (
                                        <motion.svg
                                            className="absolute inset-0 w-full h-full text-gold/30 -mx-[2px] -my-[2px] rounded-xl"
                                            viewBox="0 0 100 100"
                                        >
                                            <circle cx="50" cy="50" r="48" fill="none" stroke="currentColor" strokeWidth="4" className="stroke-dasharray-100 animate-[spin_3s_linear_infinite]" strokeLinecap="round" />
                                        </motion.svg>
                                    )}
                                </div>

                                <div className="md:text-center flex-1 md:flex-none">
                                    <h4 className={`font-semibold ${isCurrent ? 'text-gold' : isCompleted ? 'text-gray-200' : 'text-gray-500'}`}>
                                        {s.name}
                                    </h4>
                                    <p className="text-xs text-gray-400 mt-1 md:mt-2 hidden md:block opacity-0 group-hover:opacity-100 transition-opacity absolute w-32 -ml-16 left-1/2">
                                        {s.desc}
                                    </p>
                                </div>
                            </div>
                        );
                    })}
                </div>
            </div>

            {/* Overall Progress Bar */}
            <div className="mt-12 max-w-sm mx-auto text-center">
                <div className="flex justify-between text-xs text-gray-400 mb-2 font-mono">
                    <span>Processing Step {step}/{steps.length}</span>
                    <span>{progress}%</span>
                </div>
                <div className="h-1.5 w-full bg-black/40 rounded-full overflow-hidden">
                    <motion.div
                        className="h-full bg-gold"
                        initial={{ width: 0 }}
                        animate={{ width: `${progress}%` }}
                        transition={{ ease: "easeOut" }}
                    />
                </div>
            </div>
        </div>
    );
};

export default LoaderPipeline;
