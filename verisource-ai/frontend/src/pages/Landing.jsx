import React from 'react';
import { Link } from 'react-router-dom';
import { ShieldCheck, FileSearch, Lock } from 'lucide-react';
import { motion } from 'framer-motion';

const Landing = () => {
    return (
        <div className="flex min-h-screen bg-grain overflow-hidden">
            {/* Left Panel - Dark Institutional */}
            <div className="hidden lg:flex lg:w-3/5 bg-brand-navy flex-col justify-center px-20 relative overflow-hidden">
                {/* Dramatic Gradient Backgrounds */}
                <div className="absolute top-0 right-0 w-[1000px] h-[1000px] bg-blue-600 rounded-full blur-[160px] opacity-[0.07] transform translate-x-1/2 -translate-y-1/2"></div>
                <div className="absolute bottom-0 left-0 w-[800px] h-[800px] bg-gold rounded-full blur-[140px] opacity-[0.05] transform -translate-x-1/3 translate-y-1/3"></div>
                
                {/* Grid Pattern Overlay */}
                <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-[0.03] pointer-events-none"></div>
                <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:40px_40px]"></div>

                <motion.div
                    initial={{ opacity: 0, x: -30 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 1, ease: "easeOut" }}
                    className="relative z-10"
                >
                    <div className="flex items-center gap-4 mb-16 group">
                        <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-gold to-gold-light p-[1px]">
                            <div className="w-full h-full bg-brand-navy rounded-[11px] flex items-center justify-center transition-all group-hover:bg-transparent">
                                <span className="text-gold group-hover:text-brand-navy font-bold text-2xl transition-colors">VS</span>
                            </div>
                        </div>
                        <h1 className="text-4xl font-black tracking-tighter text-white">
                            VeriSource<span className="bg-gradient-to-r from-gold to-gold-light bg-clip-text text-transparent">AI</span>
                        </h1>
                    </div>

                    <h2 className="text-7xl font-black leading-[1.1] mb-8 tracking-tight">
                        Deterministic <br />
                        <span className="text-gold">Intelligence.</span>
                    </h2>
                    
                    <p className="text-xl text-gray-400 mb-14 max-w-xl leading-relaxed font-light">
                        The world's first **Governance-First** verification platform. Built to prove that AI can be a source of truth — without hallucinating, guessing, or mixing sources.
                    </p>

                    <div className="grid grid-cols-1 gap-6 max-w-lg">
                        <Feature
                            icon={<FileSearch className="w-6 h-6 text-blue-400" />}
                            title="Evidence-Only Synthesis"
                            description="Strictly bound to cryptographic text chunks. No external knowledge leakage."
                        />
                        <Feature
                            icon={<ShieldCheck className="w-6 h-6 text-green-400" />}
                            title="Counterfactual Guardrails"
                            description="Real-time mathematical refusal layers with explainable refusal guides."
                        />
                    </div>
                </motion.div>
                
                {/* Status Bar */}
                <div className="absolute bottom-10 left-20 flex items-center gap-6 text-[10px] font-mono text-gray-500 tracking-[0.2em] uppercase">
                    <div className="flex items-center gap-2">
                        <div className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse"></div>
                        CORE_ENGINE: ACTIVE
                    </div>
                    <div>GOVERNANCE: v0.9.4</div>
                    <div>LATENCY: 42MS</div>
                </div>
            </div>

            {/* Right Panel - Premium Login Area */}
            <div className="w-full lg:w-2/5 bg-[#080C14] flex flex-col justify-center items-center p-8 lg:p-24 relative">
                <div className="absolute inset-0 bg-gradient-to-b from-brand-navy-light/20 to-transparent pointer-events-none"></div>
                
                <div className="w-full max-w-md relative z-10">
                    <div className="text-center lg:text-left mb-12">
                        <div className="inline-block px-3 py-1 bg-gold/10 border border-gold/20 rounded-full text-[10px] font-bold text-gold uppercase tracking-widest mb-6">
                            Enterprise Security Protocol
                        </div>
                        <h3 className="text-4xl font-bold text-white mb-4 tracking-tight">Institutional Access</h3>
                        <p className="text-gray-400 font-light leading-relaxed">
                            Authorized personnel only. Please authenticate to access the verification dashboard.
                        </p>
                    </div>

                    <div className="space-y-4">
                        <Link
                            to="/login"
                            className="group relative w-full flex justify-center py-5 px-4 rounded-xl overflow-hidden"
                        >
                            <div className="absolute inset-0 bg-gradient-to-r from-gold to-gold-light transition-transform duration-500 group-hover:scale-105"></div>
                            <span className="relative z-10 text-brand-navy font-black uppercase tracking-widest text-sm flex items-center gap-3">
                                Enter Console
                                <motion.span
                                    animate={{ x: [0, 5, 0] }}
                                    transition={{ repeat: Infinity, duration: 1.5 }}
                                >
                                    &rarr;
                                </motion.span>
                            </span>
                        </Link>
                        
                        <Link
                            to="/register"
                            className="w-full flex justify-center py-4 px-4 border border-white/10 rounded-xl text-sm font-medium text-gray-400 hover:text-white hover:bg-white/5 transition-all"
                        >
                            Request New Credentials
                        </Link>
                    </div>

                    <div className="mt-16 flex items-center gap-4 grayscale opacity-40 hover:grayscale-0 hover:opacity-100 transition-all duration-700">
                        <div className="text-[10px] font-bold text-gray-500 uppercase tracking-widest">Powered By</div>
                        <div className="h-4 w-[1px] bg-white/10"></div>
                        <div className="text-xs font-serif italic text-gray-300">Llama 3.1 Synthesis Engine</div>
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
