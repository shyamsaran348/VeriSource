import React from 'react';
import { Outlet, useNavigate } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';
import { FileText, LogOut } from 'lucide-react';

const StudentLayout = () => {
    const { user, logout } = useAuth();
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    return (
        <div className="flex h-screen bg-brand-navy text-white overflow-hidden bg-grain">
            {/* Sidebar - Placeholder for actual Sidebar component */}
            <aside className="w-64 border-r border-white/10 bg-brand-navy-light/50 flex flex-col hidden md:flex">
                <div className="p-6 border-b border-white/10 flex items-center gap-2">
                    <div className="w-8 h-8 rounded bg-gold/20 flex items-center justify-center">
                        <span className="text-gold font-bold">VS</span>
                    </div>
                    <h1 className="text-xl font-bold tracking-tight">VeriSource<span className="text-gold">AI</span></h1>
                </div>

                <div className="p-4 flex-grow">
                    {/* Main navigation in student layout will typically just be the dashboard */}
                    <nav className="space-y-1">
                        <div className="flex items-center gap-3 px-3 py-2 bg-white/5 rounded-lg text-white">
                            <FileText size={18} className="text-gold" />
                            <span className="font-medium">Verification</span>
                        </div>
                    </nav>
                </div>

                <div className="p-4 border-t border-white/10">
                    <div className="flex items-center gap-3 px-3 py-2 mb-2 text-sm text-gray-400">
                        <div className="w-8 h-8 rounded-full bg-brand-navy flex items-center justify-center border border-white/10 text-xs">
                            {user?.username?.[0]?.toUpperCase() || 'S'}
                        </div>
                        <div className="flex-1 truncate">
                            <p className="text-white font-medium truncate">{user?.username || 'Student'}</p>
                            <p className="text-xs text-gray-500 capitalize">{user?.role}</p>
                        </div>
                    </div>
                    <button
                        onClick={handleLogout}
                        className="w-full flex items-center gap-3 px-3 py-2 text-gray-400 hover:text-white hover:bg-white/5 rounded-lg transition-colors"
                    >
                        <LogOut size={18} />
                        <span>Sign Out</span>
                    </button>
                </div>
            </aside>

            <main className="flex-1 flex flex-col h-full overflow-hidden relative">
                <header className="h-16 border-b border-white/10 flex items-center px-6 md:hidden justify-between">
                    <h1 className="text-lg font-bold tracking-tight">VeriSource<span className="text-gold">AI</span></h1>
                    <button onClick={handleLogout} className="text-gray-400 hover:text-white">
                        <LogOut size={20} />
                    </button>
                </header>
                <div className="flex-1 overflow-auto bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-brand-navy-light/30 via-brand-navy to-brand-navy">
                    <Outlet />
                </div>
            </main>
        </div>
    );
};

export default StudentLayout;
