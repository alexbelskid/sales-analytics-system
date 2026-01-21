import type { Metadata, Viewport } from 'next';
import './globals.css';
// import LayoutWrapper from '@/components/layout/LayoutWrapper'; // REMOVED: Legacy Shell
import { Toaster } from "@/components/ui/toaster";
import { SpeedInsights } from "@vercel/speed-insights/next"
import AuroraBackground from '@/components/ui/AuroraBackground';
import GlassDock from '@/components/ui/GlassDock';

export const metadata: Metadata = {
    title: 'Visual M',
    description: 'Next Gen Sales Analytics',
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
            <body className="bg-gray-900 text-gray-50 antialiased selection:bg-gray-700/30 overflow-x-hidden min-h-screen">
                <AuroraBackground />
                <div className="film-grain" />

                {/* GLASS CATHEDRAL Layout Structure */}
                <main className="relative z-10 flex min-h-screen w-full flex-col items-center">
                    {/* Centered Grid / Content Area - The "Corset" */}
                    <div className="w-full max-w-[1100px] mx-auto flex flex-col relative pt-[40px] pb-[120px]">
                        {children}
                    </div>

                    {/* Navigation Dock */}
                    <GlassDock />
                </main>

                <Toaster />
                <SpeedInsights />
            </body>
        </html>
    );
}
