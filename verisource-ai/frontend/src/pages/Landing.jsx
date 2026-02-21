import React from 'react';
import { Link } from 'react-router-dom';
import { ShieldCheck, FileSearch, Lock } from 'lucide-react';
import { motion } from 'framer-motion';

const Landing = () => {
    return (
        <div className="flex min-h-screen">
            {/* Left Panel - Dark Institutional */}
            <div className="hidden lg:flex lg:w-3/5 bg-brand-navy flex-col justify-center px-20 relative overflow-hidden">
                {/* Decorative elements */}
                <div className="absolute top-0 right-0 w-[800px] h-[800px] bg-brand-navy-light rounded-full blur-3xl opacity-20 transform translate-x-1/2 -translate-y-1/2"></div>
                <div className="absolute bottom-0 left-0 w-[600px] h-[600px] bg-gold rounded-full blur-3xl opacity-5 transform -translate-x-1/3 translate-y-1/3"></div>

                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8 }}
                    className="relative z-10"
                >
                    <div className="flex items-center gap-3 mb-12">
                        <div className="w-12 h-12 rounded bg-gold/20 flex items-center justify-center">
                            <span className="text-gold font-bold text-xl">VS</span>
                        </div>
                        <h1 className="text-3xl font-bold tracking-tight">VeriSource<span className="text-gold">AI</span></h1>
                    </div>

                    <h2 className="text-5xl font-extrabold leading-tight mb-6">
                        AI That Refuses to <span className="text-gold">Hallucinate.</span>
                    </h2>
                    <p className="text-xl text-gray-400 mb-12 max-w-2xl leading-relaxed">
                        Single-document, evidence-first academic verification infrastructure built for absolute certainty.
                    </p>

                    <div className="space-y-8">
                        <Feature
                            icon={<FileSearch className="w-6 h-6 text-blue-400" />}
                            title="Single Document Scope"
                            description="Strictly bounded context limits preventing conceptual bleed and cross-contamination."
                        />
                        <Feature
                            icon={<ShieldCheck className="w-6 h-6 text-green-400" />}
                            title="Evidence-First Reasoning"
                            description="Every claim is mapped directly to explicitly retrieved cryptographic chunks."
                        />
                        <Feature
                            icon={<Lock className="w-6 h-6 text-red-400" />}
                            title="Confidence-Gated Decisions"
                            description="Hard thresholds enforce mandatory refusals for ambiguous or unsupported queries."
                        />
                    </div>
                </motion.div>
            </div>

            {/* Right Panel - Light Login Area */}
            <div className="w-full lg:w-2/5 bg-white flex flex-col justify-center items-center p-8 lg:p-16">
                <div className="w-full max-w-md">
                    {/* Mobile Header visible only on small screens */}
                    <div className="flex lg:hidden items-center gap-3 mb-10 justify-center">
                        <div className="w-10 h-10 rounded bg-brand-navy/10 flex items-center justify-center">
                            <span className="text-brand-navy font-bold text-lg">VS</span>
                        </div>
                        <h1 className="text-2xl font-bold tracking-tight text-brand-navy">VeriSource<span className="text-gold">AI</span></h1>
                    </div>

                    <div className="text-center lg:text-left mb-10">
                        <h3 className="text-3xl font-bold text-gray-900 mb-2">Gatekeeper Access</h3>
                        <p className="text-gray-500">Authenticate to enter the verification sandbox.</p>
                    </div>

                    <div className="space-y-6">
                        <Link
                            to="/login"
                            className="w-full flex justify-center py-4 px-4 border border-transparent rounded-lg shadow-sm text-lg font-medium text-white bg-brand-navy hover:bg-brand-navy-light focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-brand-navy transition-all transform hover:-translate-y-0.5"
                        >
                            Continue to Login  &rarr;
                        </Link>

                        <div className="mt-8 pt-8 border-t border-gray-100 text-sm text-gray-500 text-center">
                            <p>System Status: <span className="text-green-500 font-medium">Operational</span></p>
                            <p className="mt-2 text-xs">Phase 8 Integration &bull; Governance Active</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

const Feature = ({ icon, title, description }) => (
    <motion.div
        whileHover={{ x: 5 }}
        className="flex items-start gap-4 p-4 rounded-xl hover:bg-white/5 transition-colors border border-transparent hover:border-white/10"
    >
        <div className="mt-1 p-2 bg-white/5 rounded-lg border border-white/10">
            {icon}
        </div>
        <div>
            <h4 className="text-lg font-semibold text-white mb-1">{title}</h4>
            <p className="text-gray-400 text-sm leading-relaxed">{description}</p>
        </div>
    </motion.div>
);

export default Landing;
