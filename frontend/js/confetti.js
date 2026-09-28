// Confetti Particle Explosion Effect
const Confetti = (function () {
  let canvas = null;
  let ctx = null;
  let particles = [];
  let animId = null;

  function init() {
    if (!canvas) {
      canvas = document.createElement('canvas');
      canvas.id = 'confetti-canvas';
      canvas.style.position = 'fixed';
      canvas.style.top = '0';
      canvas.style.left = '0';
      canvas.style.width = '100vw';
      canvas.style.height = '100vh';
      canvas.style.pointerEvents = 'none';
      canvas.style.zIndex = '9999';
      document.body.appendChild(canvas);
      ctx = canvas.getContext('2d');
      resize();
      window.addEventListener('resize', resize);
    }
  }

  function resize() {
    if (canvas) {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    }
  }

  function createParticles(count = 90) {
    const colors = ['#6366F1', '#EC4899', '#10B981', '#F59E0B', '#3B82F6', '#8B5CF6', '#F43F5E'];
    const w = canvas.width;
    const h = canvas.height;
    particles = [];

    for (let i = 0; i < count; i++) {
      particles.push({
        x: w / 2 + (Math.random() - 0.5) * 200,
        y: h / 2 + (Math.random() - 0.5) * 100,
        vx: (Math.random() - 0.5) * 14,
        vy: -Math.random() * 12 - 4,
        size: Math.random() * 8 + 4,
        color: colors[Math.floor(Math.random() * colors.length)],
        rotation: Math.random() * 360,
        vRot: (Math.random() - 0.5) * 10,
        alpha: 1,
        gravity: 0.35,
        decay: Math.random() * 0.015 + 0.008
      });
    }
  }

  function render() {
    if (!ctx) return;
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    let activeCount = 0;
    particles.forEach(p => {
      p.x += p.vx;
      p.y += p.vy;
      p.vy += p.gravity;
      p.rotation += p.vRot;
      p.alpha -= p.decay;

      if (p.alpha > 0) {
        activeCount++;
        ctx.save();
        ctx.globalAlpha = Math.max(0, p.alpha);
        ctx.translate(p.x, p.y);
        ctx.rotate((p.rotation * Math.PI) / 180);
        ctx.fillStyle = p.color;
        ctx.fillRect(-p.size / 2, -p.size / 2, p.size, p.size * 0.6);
        ctx.restore();
      }
    });

    if (activeCount > 0) {
      animId = requestAnimationFrame(render);
    } else {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      cancelAnimationFrame(animId);
      animId = null;
    }
  }

  return {
    burst: () => {
      init();
      if (animId) cancelAnimationFrame(animId);
      createParticles(110);
      render();
    }
  };
})();
