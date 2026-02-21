import React from 'react';
import { motion } from 'framer-motion';

const ConfidenceMeter = ({ score, threshold = 0.05 }) => {
    const percentage = Math.round(score * 100);
    const isPassing = score >= threshold;

    // Decide color based on score relative to threshold
    const colorClass = isPassing
        ? 'bg-green-500'
        : score >= threshold - 0.02
            ? 'bg-yellow-500'
            : 'bg-red-500';

    // Visual scaling for ONNX embeddings (which compress scores)
    // We boost the visual width so an 11% score doesn't look empty, 
    // while keeping the actual text percentage accurate.
    const visualWidth = Math.min(Math.max((score / (threshold * 3)) * 100, 5), 100);

    return (
        <div className="w-full">
            <div className="flex justify-between items-end mb-2">
                <span className="text-xs font-semibold text-gray-400 uppercase tracking-widest">Confidence Score</span>
                <span className={`text-lg font-bold ${isPassing ? 'text-green-400' : 'text-red-400'}`}>
                    {percentage}%
                </span>
            </div>

            <div className="h-3 w-full bg-brand-navy-light rounded-full overflow-hidden border border-white/5 relative">
                <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${visualWidth}%` }}
                    transition={{ duration: 1, ease: "easeOut", delay: 0.2 }}
                    className={`h-full ${colorClass} relative`}
                >
                    {/* Shimmer effect */}
                    <div className="absolute inset-0 bg-white/20 w-full h-full custom-shimmer"></div>
                </motion.div>

                {/* Threshold indicator */}
                <div
                    className="absolute top-0 bottom-0 w-0.5 bg-white/50 z-10"
                    style={{ left: `${threshold * 100}%` }}
                    title={`Required Threshold: ${threshold * 100}%`}
                />
            </div>

            <style dangerouslySetInnerHTML={{
                __html: `
        @keyframes shimmer {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(100%); }
        }
        .custom-shimmer {
          animation: shimmer 2s infinite linear;
        }
      `}} />
        </div>
    );
};

export default ConfidenceMeter;
