import type { Metadata } from 'next';
import { Playfair_Display, DM_Sans, JetBrains_Mono } from 'next/font/google';
import './globals.css';
import Sidebar from '@/components/layout/Sidebar';
import Header from '@/components/layout/Header';
import { Toaster } from "@/components/ui/toaster";

const playfair = Playfair_Display({
    subsets: ['latin', 'cyrillic'],
    variable: '--font-display',
    display: 'swap',
});

const dmSans = DM_Sans({
    subsets: ['latin', 'cyrillic'],
    variable: '--font-body',
    display: 'swap',
});

const jetbrainsMono = JetBrains_Mono({
    subsets: ['latin'],
    variable: '--font-mono',
    display: 'swap',
});

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
            <body className={`${playfair.variable} ${dmSans.variable} ${jetbrainsMono.variable}`}>
                <div className="flex h-screen bg-obsidian">
                    <Sidebar />
                    <div className="flex flex-1 flex-col overflow-hidden">
                        <Header />
                        <main className="flex-1 overflow-y-auto p-6">
                            {children}
                        </main>
                    </div>
                </div>
                <Toaster />
            </body>
        </html>
    );
}
