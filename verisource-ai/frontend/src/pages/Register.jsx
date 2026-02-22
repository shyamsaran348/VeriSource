import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';
import { authService } from '../services/authService';
import { Shield, KeyRound, User, Lock, Loader2, AlertCircle, Briefcase } from 'lucide-react';
import { motion } from 'framer-motion';

const Register = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [role, setRole] = useState('student');
    const [error, setError] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);

    const { login } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!username || !password || !role) {
            setError('Please fill out all fields.');
            return;
        }

        if (password.length < 6) {
            setError('Password must be at least 6 characters long.');
            return;
        }

        setIsSubmitting(true);
        setError('');

        try {
            // 1. Register User
            await authService.register(username, password, role);

            // 2. Immediately Login that User
            const authData = await authService.login(username, password);

            login({
                access_token: authData.access_token,
                role: role,
                username: username
            });

            navigate(role === 'admin' ? '/admin/dashboard' : '/student/dashboard', { replace: true });
        } catch (err) {
            setError(err.response?.data?.detail || 'Registration failed. Username may already exist.');
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className="min-h-screen bg-brand-navy flex items-center justify-center p-4 relative overflow-hidden bg-grain">
            {/* Dynamic Background Elements */}
            <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-brand-navy-light rounded-full blur-3xl opacity-40 mix-blend-screen animate-pulse"></div>
            <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-gold/10 rounded-full blur-3xl opacity-40 mix-blend-screen animate-pulse" style={{ animationDelay: '1s' }}></div>

            <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5 }}
                className="w-full max-w-md relative z-10"
            >
                <div className="glass-panel p-8 sm:p-10 rounded-2xl shadow-2xl">
                    <div className="text-center mb-10">
                        <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-brand-navy-light border border-white/10 mb-6 relative">
                            <Shield className="w-8 h-8 text-gold relative z-10" />
                            <div className="absolute inset-0 bg-gold/20 rounded-full blur-md"></div>
                        </div>
                        <h2 className="text-3xl font-bold text-white mb-2 tracking-tight">System Registration</h2>
                        <p className="text-gray-400">Request access to VeriSource AI</p>
                    </div>

                    {error && (
                        <motion.div
                            initial={{ opacity: 0, y: -10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="mb-6 p-4 rounded-lg bg-red-500/10 border border-red-500/20 flex items-start gap-3"
                        >
                            <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
                            <p className="text-sm text-red-200 leading-relaxed">{error}</p>
                        </motion.div>
                    )}

                    <form onSubmit={handleSubmit} className="space-y-6">
                        <div className="space-y-2">
                            <label className="text-sm font-medium text-gray-300 block">Identificator</label>
                            <div className="relative group">
                                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                                    <User className="h-5 w-5 text-gray-500 group-focus-within:text-gold transition-colors" />
                                </div>
                                <input
                                    type="text"
                                    value={username}
                                    onChange={(e) => setUsername(e.target.value)}
                                    className="block w-full pl-11 pr-4 py-3 bg-brand-navy border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-gold/50 focus:border-transparent transition-all"
                                    placeholder="Choose a system ID"
                                    disabled={isSubmitting}
                                />
                            </div>
                        </div>

                        <div className="space-y-2">
                            <label className="text-sm font-medium text-gray-300 block">Passcode</label>
                            <div className="relative group">
                                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                                    <KeyRound className="h-5 w-5 text-gray-500 group-focus-within:text-gold transition-colors" />
                                </div>
                                <input
                                    type="password"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    className="block w-full pl-11 pr-4 py-3 bg-brand-navy border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-gold/50 focus:border-transparent transition-all"
                                    placeholder="Create strong passcode"
                                    disabled={isSubmitting}
                                />
                            </div>
                        </div>

                        <div className="space-y-2">
                            <label className="text-sm font-medium text-gray-300 block">Access Level</label>
                            <div className="grid grid-cols-2 gap-3">
                                <button
                                    type="button"
                                    onClick={() => setRole('student')}
                                    className={`py-3 px-4 rounded-xl border flex items-center justify-center gap-2 transition-all ${role === 'student'
                                        ? 'bg-blue-500/10 border-blue-500/50 text-blue-400 shadow-[0_0_10px_rgba(59,130,246,0.1)]'
                                        : 'bg-brand-navy border-white/10 text-gray-500 hover:text-gray-300 hover:border-white/20'
                                        }`}
                                >
                                    <User className="w-4 h-4" />
                                    <span className="font-semibold text-sm">Student</span>
                                </button>
                                <button
                                    type="button"
                                    onClick={() => setRole('admin')}
                                    className={`py-3 px-4 rounded-xl border flex items-center justify-center gap-2 transition-all ${role === 'admin'
                                        ? 'bg-red-500/10 border-red-500/50 text-red-500 shadow-[0_0_10px_rgba(239,68,68,0.1)]'
                                        : 'bg-brand-navy border-white/10 text-gray-500 hover:text-gray-300 hover:border-white/20'
                                        }`}
                                >
                                    <Briefcase className="w-4 h-4" />
                                    <span className="font-semibold text-sm">Admin</span>
                                </button>
                            </div>
                        </div>

                        <button
                            type="submit"
                            disabled={isSubmitting}
                            className="w-full flex items-center justify-center gap-2 mt-4 py-3.5 px-4 rounded-xl text-brand-navy bg-gold hover:bg-yellow-500 font-semibold focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-brand-navy focus:ring-gold transition-all disabled:opacity-70 disabled:cursor-not-allowed transform hover:-translate-y-0.5"
                        >
                            {isSubmitting ? (
                                <>
                                    <Loader2 className="w-5 h-5 animate-spin" />
                                    <span>Provisioning...</span>
                                </>
                            ) : (
                                <>
                                    <Lock className="w-5 h-5" />
                                    <span>Create Account</span>
                                </>
                            )}
                        </button>
                    </form>

                    <div className="mt-8 text-center text-sm text-gray-400">
                        Already have access?{' '}
                        <Link to="/login" className="text-gold hover:text-yellow-400 font-medium transition-colors">
                            Authenticate here
                        </Link>
                    </div>
                </div>
            </motion.div>
        </div>
    );
};

export default Register;
