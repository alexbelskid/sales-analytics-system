'use client';

import React from 'react';

const AuroraBackground = () => {
    return (
        <div className="fixed inset-0 -z-20 bg-[#050505] pointer-events-none overflow-hidden">
            {/* Top Center Subtle Light (Sky Blue) */}
            <div
                className="absolute top-0 left-1/2 -translate-x-1/2 w-[120vw] h-[60vh] opacity-[0.4]"
                style={{
                    background: 'radial-gradient(circle at 50% 0%, rgba(56, 189, 248, 0.08) 0%, transparent 60%)'
                }}
            />

            {/* Bottom Right Faint Glow (Purple) */}
            <div
                className="absolute bottom-[-10%] right-[-10%] w-[80vw] h-[80vh] opacity-[0.3]"
                style={{
                    background: 'radial-gradient(circle at 80% 80%, rgba(124, 58, 237, 0.05) 0%, transparent 50%)'
                }}
            />
        </div>
    );
};

export default AuroraBackground;
