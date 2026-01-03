import type { Metadata, Viewport } from 'next';
import './globals.css';
import LayoutWrapper from '@/components/layout/LayoutWrapper';
import { Toaster } from "@/components/ui/toaster";
import { SpeedInsights } from "@vercel/speed-insights/next"

export const metadata: Metadata = {
    title: 'Alterini AI - Аналитика продаж',
    description: 'Система аналитики продаж с AI-автоответами и прогнозированием',
};

export const viewport: Viewport = {
    width: 'device-width',
    initialScale: 1,
    maximumScale: 5,
    userScalable: true,
};

export default function RootLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <html lang="ru" className="dark">
            <body className="overflow-hidden">
                <LayoutWrapper>
                    {children}
                </LayoutWrapper>
                <Toaster />
                <SpeedInsights />
            </body>
        </html>
    );
}
