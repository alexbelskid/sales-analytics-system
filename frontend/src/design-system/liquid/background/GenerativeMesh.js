class GenerativeMesh {
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this.points = [];
        this.width = window.innerWidth;
        this.height = window.innerHeight;
        this.colors = ['#00f3ff', '#bd00ff', '#00ff94']; // Neon Blue, Purple, Green

        this.init();
        this.animate();

        window.addEventListener('resize', () => this.resize());
    }

    init() {
        this.canvas.width = this.width;
        this.canvas.height = this.height;

        // Create random floating points
        for (let i = 0; i < 6; i++) {
            this.points.push({
                x: Math.random() * this.width,
                y: Math.random() * this.height,
                vx: (Math.random() - 0.5) * 0.5,
                vy: (Math.random() - 0.5) * 0.5,
                radius: Math.random() * 300 + 200,
                color: this.colors[Math.floor(Math.random() * this.colors.length)]
            });
        }
    }

    resize() {
        this.width = window.innerWidth;
        this.height = window.innerHeight;
        this.canvas.width = this.width;
        this.canvas.height = this.height;
    }

    animate() {
        this.ctx.clearRect(0, 0, this.width, this.height);

        // Dark background
        this.ctx.fillStyle = '#050510';
        this.ctx.fillRect(0, 0, this.width, this.height);

        // Draw and update points
        this.points.forEach(point => {
            point.x += point.vx;
            point.y += point.vy;

            // Bounce off walls
            if (point.x < 0 || point.x > this.width) point.vx *= -1;
            if (point.y < 0 || point.y > this.height) point.vy *= -1;

            // Draw gradient blob
            const gradient = this.ctx.createRadialGradient(
                point.x, point.y, 0,
                point.x, point.y, point.radius
            );
            gradient.addColorStop(0, point.color);
            gradient.addColorStop(1, 'transparent');

            this.ctx.globalAlpha = 0.4;
            this.ctx.fillStyle = gradient;
            this.ctx.beginPath();
            this.ctx.arc(point.x, point.y, point.radius, 0, Math.PI * 2);
            this.ctx.fill();
        });

        requestAnimationFrame(() => this.animate());
    }
}

// Auto-initialize if canvas exists
document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('generative-bg');
    if (canvas) {
        new GenerativeMesh(canvas);
    }
});
