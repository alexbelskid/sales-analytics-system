/** @type {import('tailwindcss').Config} */
module.exports = {
    darkMode: ["class"],
    content: [
        './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
        './src/components/**/*.{js,ts,jsx,tsx,mdx}',
        './src/app/**/*.{js,ts,jsx,tsx,mdx}',
    ],
    theme: {
        container: {
            center: true,
            padding: "2rem",
            screens: {
                "2xl": "1400px",
            },
        },
        extend: {
            colors: {
                // Unified color system mapped to CSS variables
                border: {
                    DEFAULT: "hsl(var(--border))",
                    muted: "hsl(var(--border-muted))",
                    emphasis: "hsl(var(--border-emphasis))",
                    focus: "hsl(var(--border-focus))",
                },
                input: "hsl(var(--input))",
                ring: "hsl(var(--ring))",
                background: {
                    DEFAULT: "hsl(var(--background))",
                    secondary: "hsl(var(--background-secondary))",
                    tertiary: "hsl(var(--background-tertiary))",
                    hover: "hsl(var(--background-hover))",
                },
                foreground: {
                    DEFAULT: "hsl(var(--foreground))",
                    secondary: "hsl(var(--foreground-secondary))",
                    muted: "hsl(var(--foreground-muted))",
                    disabled: "hsl(var(--foreground-disabled))",
                },
                brand: {
                    primary: "hsl(var(--brand-primary))",
                    'primary-hover': "hsl(var(--brand-primary-hover))",
                    secondary: "hsl(var(--brand-secondary))",
                },
                success: {
                    DEFAULT: "hsl(var(--success))",
                    muted: "hsl(var(--success-muted))",
                },
                warning: {
                    DEFAULT: "hsl(var(--warning))",
                    muted: "hsl(var(--warning-muted))",
                },
                destructive: {
                    DEFAULT: "hsl(var(--destructive))",
                    foreground: "hsl(var(--destructive-foreground))",
                    muted: "hsl(var(--destructive-muted))",
                },
                info: {
                    DEFAULT: "hsl(var(--info))",
                    muted: "hsl(var(--info-muted))",
                },
                primary: {
                    DEFAULT: "hsl(var(--primary))",
                    foreground: "hsl(var(--primary-foreground))",
                },
                secondary: {
                    DEFAULT: "hsl(var(--secondary))",
                    foreground: "hsl(var(--secondary-foreground))",
                },
                muted: {
                    DEFAULT: "hsl(var(--muted))",
                    foreground: "hsl(var(--muted-foreground))",
                },
                accent: {
                    DEFAULT: "hsl(var(--accent))",
                    foreground: "hsl(var(--accent-foreground))",
                },
                popover: {
                    DEFAULT: "hsl(var(--popover))",
                    foreground: "hsl(var(--popover-foreground))",
                },
                card: {
                    DEFAULT: "hsl(var(--card))",
                    foreground: "hsl(var(--card-foreground))",
                },
            },
            fontFamily: {
                sans: ['-apple-system', 'BlinkMacSystemFont', '"Segoe UI"', '"Inter"', 'sans-serif'],
                mono: ['"SF Mono"', '"Monaco"', '"Inconsolata"', 'monospace'],
            },
            borderRadius: {
                sm: "var(--radius-sm)",
                md: "var(--radius-md)",
                lg: "var(--radius-lg)",
                xl: "var(--radius-xl)",
                "2xl": "var(--radius-2xl)",
                full: "var(--radius-full)",
            },
            transitionDuration: {
                fast: "var(--duration-fast)",
                normal: "var(--duration-normal)",
                slow: "var(--duration-slow)",
            },
            transitionTimingFunction: {
                smooth: "var(--ease-smooth)",
                spring: "var(--ease-spring)",
            },
            backdropBlur: {
                glass: "30px",
                heavy: "40px",
                light: "20px",
            },
            keyframes: {
                "fade-in": {
                    "0%": { opacity: "0", transform: "translateY(10px)" },
                    "100%": { opacity: "1", transform: "translateY(0)" },
                },
                "slide-in": {
                    "0%": { transform: "translateX(-100%)" },
                    "100%": { transform: "translateX(0)" },
                },
                "scale-in": {
                    "0%": { opacity: "0", transform: "scale(0.95)" },
                    "100%": { opacity: "1", transform: "scale(1)" },
                },
            },
            animation: {
                "fade-in": "fade-in 0.3s ease-out",
                "slide-in": "slide-in 0.3s ease-out",
                "scale-in": "scale-in 0.2s ease-out",
            },
        },
    },
    plugins: [require("tailwindcss-animate")],
};
