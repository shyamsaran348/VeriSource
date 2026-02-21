import React from 'react';
import { motion } from 'framer-motion';

const DataTable = ({ columns, data, isLoading, emptyMessage = "No records found." }) => {
    if (isLoading) {
        return (
            <div className="w-full bg-brand-navy-light/20 border border-white/10 rounded-xl p-12 flex justify-center items-center">
                <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-gold"></div>
                <span className="ml-3 text-gray-400">Loading data...</span>
            </div>
        );
    }

    if (!data || data.length === 0) {
        return (
            <div className="w-full bg-brand-navy-light/20 border border-white/10 rounded-xl p-12 flex justify-center items-center text-gray-400">
                {emptyMessage}
            </div>
        );
    }

    return (
        <div className="w-full border border-white/10 rounded-xl overflow-hidden bg-brand-navy-light/10">
            <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse">
                    <thead>
                        <tr className="bg-white/5 border-b border-white/10 text-xs font-semibold text-gray-400 uppercase tracking-wider">
                            {columns.map((col, i) => (
                                <th key={i} className="px-6 py-4">{col.header}</th>
                            ))}
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-white/5">
                        {data.map((row, rowIndex) => (
                            <motion.tr
                                key={rowIndex}
                                initial={{ opacity: 0, y: 5 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: rowIndex * 0.05, duration: 0.2 }}
                                className="hover:bg-white/5 transition-colors group"
                            >
                                {columns.map((col, colIndex) => (
                                    <td key={colIndex} className="px-6 py-4 text-sm text-gray-300">
                                        {col.cell ? col.cell(row) : row[col.accessor]}
                                    </td>
                                ))}
                            </motion.tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default DataTable;
