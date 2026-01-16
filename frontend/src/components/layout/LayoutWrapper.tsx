'use client';

import { useState } from 'react';
import Sidebar from '@/components/layout/Sidebar';
import MobileHeader from '@/components/layout/MobileHeader';

interface LayoutWrapperProps {
    children: React.ReactNode;
}

export default function LayoutWrapper({ children }: LayoutWrapperProps) {
    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

    return (
        <div className="flex h-screen bg-[#202020] overflow-hidden">
            {/* Sidebar - handles both desktop and mobile */}
            <Sidebar
                isMobileOpen={isMobileMenuOpen}
                onMobileClose={() => setIsMobileMenuOpen(false)}
            />

            {/* Main content area */}
            <div className="flex flex-1 flex-col overflow-hidden min-w-0">
                {/* Mobile Header - only visible on mobile */}
                <MobileHeader onMenuClick={() => setIsMobileMenuOpen(true)} />

                {/* Page content */}
                <main className="flex-1 overflow-y-auto overflow-x-hidden p-4 md:p-6 lg:p-8 mobile-safe">
                    {children}
                </main>
            </div>
        </div>
    );
}
