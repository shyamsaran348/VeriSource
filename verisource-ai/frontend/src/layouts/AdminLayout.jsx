import React from 'react';
import { Outlet, useNavigate, useLocation, Link } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';
import { Database, UploadCloud, ScrollText, LogOut, ShieldAlert } from 'lucide-react';
import { motion } from 'framer-motion';

const AdminLayout = () => {
    const { user, logout } = useAuth();
    const navigate = useNavigate();
    const location = useLocation();

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    const navItems = [
        { path: '/admin/dashboard', icon: Database, label: 'Overview' },
        { path: '/admin/upload', icon: UploadCloud, label: 'Ingestion' },
        { path: '/admin/documents', icon: ScrollText, label: 'Documents' },
        { path: '/admin/audit', icon: ShieldAlert, label: 'Audit Logs' },
    ];

    return (
        <div className="flex h-screen bg-brand-navy text-white overflow-hidden bg-grain">
            <aside className="w-64 border-r border-white/10 bg-brand-navy-light/40 flex flex-col hidden md:flex relative z-10">
                <div className="absolute inset-0 bg-gradient-to-b from-transparent to-brand-navy/80 pointer-events-none" />

                <div className="p-6 border-b border-white/10 flex items-center gap-2 relative z-20">
                    <div className="w-8 h-8 rounded bg-gold/20 flex items-center justify-center">
                        <span className="text-gold font-bold">VS</span>
                    </div>
                    <h1 className="text-xl font-bold tracking-tight">VeriSource<span className="text-gold">AI</span></h1>
                    <span className="ml-2 text-[10px] uppercase font-bold tracking-wider bg-red-500/20 text-red-400 px-1.5 py-0.5 rounded">Admin</span>
                </div>

                <div className="p-4 flex-grow relative z-20">
                    <nav className="space-y-2">
                        {navItems.map((item) => {
                            const isActive = location.pathname === item.path || (item.path !== '/admin/dashboard' && location.pathname.startsWith(item.path));
                            const Icon = item.icon;

                            return (
                                <Link
                                    key={item.path}
                                    to={item.path}
                                    className={`flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all relative ${isActive ? 'text-white' : 'text-gray-400 hover:text-white hover:bg-white/5'
                                        }`}
                                >
                                    {isActive && (
                                        <motion.div
                                            layoutId="admin-active-nav"
                                            className="absolute inset-0 bg-white/10 rounded-lg border border-white/10"
                                            initial={false}
                                            transition={{ type: "spring", stiffness: 300, damping: 30 }}
                                        />
                                    )}
                                    <Icon size={18} className={`relative z-10 ${isActive ? 'text-gold' : ''}`} />
                                    <span className="font-medium relative z-10">{item.label}</span>
                                </Link>
                            );
                        })}
                    </nav>
                </div>

                <div className="p-4 border-t border-white/10 relative z-20">
                    <div className="flex items-center gap-3 px-3 py-2 mb-2 text-sm text-gray-400">
                        <div className="w-8 h-8 rounded-full bg-brand-navy flex items-center justify-center border border-white/10 text-xs">
                            {user?.username?.[0]?.toUpperCase() || 'A'}
                        </div>
                        <div className="flex-1 truncate">
                            <p className="text-white font-medium truncate">{user?.username || 'Administrator'}</p>
                            <p className="text-xs text-red-400 font-mono">System Admin</p>
                        </div>
                    </div>
                    <button
                        onClick={handleLogout}
                        className="w-full flex items-center gap-3 px-3 py-2 text-gray-400 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-colors"
                    >
                        <LogOut size={18} />
                        <span>Terminate Session</span>
                    </button>
                </div>
            </aside>

            <main className="flex-1 flex flex-col h-full overflow-hidden relative">
                <header className="h-16 border-b border-white/10 flex items-center px-6 md:hidden justify-between bg-brand-navy-light/40 backdrop-blur-md z-20">
                    <div className="flex items-center gap-2">
                        <h1 className="text-lg font-bold tracking-tight">VeriSource<span className="text-gold">AI</span></h1>
                        <span className="text-[10px] uppercase font-bold tracking-wider bg-red-500/20 text-red-400 px-1.5 py-0.5 rounded">Admin</span>
                    </div>
                    <button onClick={handleLogout} className="text-gray-400 hover:text-red-400 transition-colors">
                        <LogOut size={20} />
                    </button>
                </header>
                <div className="flex-1 overflow-auto bg-[radial-gradient(circle_at_top_right,_var(--tw-gradient-stops))] from-brand-navy-light/20 via-brand-navy to-[#05101f] p-4 md:p-8">
                    <Outlet />
                </div>
            </main>
        </div>
    );
};

export default AdminLayout;
