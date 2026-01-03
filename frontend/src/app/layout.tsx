import type { Metadata } from 'next';
import './globals.css';
import Sidebar from '@/components/layout/Sidebar';
import Header from '@/components/layout/Header';
import { Toaster } from "@/components/ui/toaster";
import { SpeedInsights } from "@vercel/speed-insights/next"

export const metadata: Metadata = {
    title: 'SalesAI - Аналитика продаж',
    description: 'Система аналитики продаж с AI-автоответами и прогнозированием',
};

export default function RootLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <html lang="ru" className="dark">
            <body>
                <div className="flex h-screen bg-[#0A0A0A]">
                    <Sidebar />
                    <div className="flex flex-1 flex-col overflow-hidden">
                        <Header />
                        <main className="flex-1 overflow-y-auto p-8">
                            {children}
                        </main>
                    </div>
                </div>
                <Toaster />
                <SpeedInsights />
            </body>
        </html>
    );
}
