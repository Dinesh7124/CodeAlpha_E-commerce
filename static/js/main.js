/* ============ MAIN JS — Interactivity ============ */

// ===== 1. Confetti on Order Success =====
document.addEventListener('DOMContentLoaded', () => {
    if (document.querySelector('.success-page')) {
        createConfetti();
    }
});

function createConfetti() {
    const colors = ['#10b981', '#8b5cf6', '#f59e0b', '#ef4444', '#3b82f6', '#ec4899'];
    const container = document.createElement('div');
    container.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:9999;';
    document.body.appendChild(container);

    for (let i = 0; i < 80; i++) {
        const piece = document.createElement('div');
        const color = colors[Math.floor(Math.random() * colors.length)];
        const left = Math.random() * 100;
        const delay = Math.random() * 2;
        const duration = 2 + Math.random() * 2;
        const size = 6 + Math.random() * 8;
        piece.style.cssText = `position:absolute;top:-20px;left:${left}%;width:${size}px;height:${size}px;background:${color};border-radius:${Math.random() > 0.5 ? '50%' : '2px'};animation:confettiFall ${duration}s ${delay}s linear forwards;`;
        container.appendChild(piece);
    }
    setTimeout(() => container.remove(), 5000);
}

// ===== 2. Toast Notifications =====
window.showToast = function(message, type = 'info') {
    let toast = document.querySelector('.toast');
    if (!toast) {
        toast = document.createElement('div');
        toast.className = 'toast';
        document.body.appendChild(toast);
    }
    const icon = { success: '✅', error: '❌', info: 'ℹ️', warning: '⚠️' }[type] || 'ℹ️';
    toast.className = `toast toast-${type} anim-slide-right`;
    toast.innerHTML = `<span class="toast-icon">${icon}</span><span>${message}</span>`;
    toast.classList.add('show');
    clearTimeout(window._toastTimer);
    window._toastTimer = setTimeout(() => toast.classList.remove('show'), 3000);
};

// Auto-convert Django messages to toasts
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.alert').forEach((alert, i) => {
        const type = alert.classList.contains('alert-success') ? 'success'
            : alert.classList.contains('alert-danger') ? 'error'
            : alert.classList.contains('alert-warning') ? 'warning' : 'info';
        setTimeout(() => showToast(alert.textContent.trim(), type), i * 300);
        alert.style.display = 'none';
    });
});

// ===== 3. Scroll Animations =====
document.addEventListener('DOMContentLoaded', () => {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, { threshold: 0.1, rootMargin: '0px 0px -80px 0px' });

    document.querySelectorAll('.scroll-anim').forEach(el => observer.observe(el));
});

// ===== 4. Counter Animation =====
function animateCounter(el, target, duration = 1500, prefix = '', suffix = '') {
    const startTime = performance.now();
    const isDecimal = target % 1 !== 0;

    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3);
        const current = target * eased;
        el.textContent = prefix + (isDecimal ? current.toFixed(2) : Math.floor(current).toLocaleString('en-IN')) + suffix;
        if (progress < 1) requestAnimationFrame(update);
        else el.textContent = prefix + (isDecimal ? target.toFixed(2) : target.toLocaleString('en-IN')) + suffix;
    }
    requestAnimationFrame(update);
}

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('[data-count]').forEach(el => {
        const target = parseFloat(el.dataset.count);
        const prefix = el.dataset.prefix || '';
        const suffix = el.dataset.suffix || '';
        const obs = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    animateCounter(el, target, 1800, prefix, suffix);
                    obs.unobserve(el);
                }
            });
        }, { threshold: 0.5 });
        obs.observe(el);
    });
});

// ===== 5. Sticky Header on Scroll =====
document.addEventListener('DOMContentLoaded', () => {
    const header = document.querySelector('header');
    window.addEventListener('scroll', () => {
        const y = window.scrollY;
        if (y > 20) header.classList.add('scrolled');
        else header.classList.remove('scrolled');
    });
});

// ===== 6. Ripple Effect =====
document.addEventListener('click', (e) => {
    const btn = e.target.closest('.btn, .btn-primary, .btn-secondary, .btn-success');
    if (!btn) return;
    const rect = btn.getBoundingClientRect();
    const ripple = document.createElement('span');
    ripple.className = 'ripple';
    ripple.style.cssText = `position:absolute;left:${e.clientX - rect.left}px;top:${e.clientY - rect.top}px;width:20px;height:20px;background:rgba(255,255,255,0.5);border-radius:50%;transform:scale(0);animation:ripple 0.6s ease-out;pointer-events:none;`;
    btn.style.position = 'relative';
    btn.style.overflow = 'hidden';
    btn.appendChild(ripple);
    setTimeout(() => ripple.remove(), 600);
});

// ===== 7. Product Card 3D Tilt =====
document.addEventListener('DOMContentLoaded', () => {
    if (window.matchMedia('(hover: none)').matches) return;
    document.querySelectorAll('.product-card').forEach(card => {
        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = (e.clientX - rect.left) / rect.width - 0.5;
            const y = (e.clientY - rect.top) / rect.height - 0.5;
            card.style.transform = `perspective(900px) rotateY(${x * 6}deg) rotateX(${-y * 6}deg) translateY(-6px)`;
        });
        card.addEventListener('mouseleave', () => {
            card.style.transform = '';
        });
    });
});

// ===== 8. Smooth Scroll =====
document.querySelectorAll('a[href^="#"]').forEach(link => {
    link.addEventListener('click', (e) => {
        const target = document.querySelector(link.getAttribute('href'));
        if (target) {
            e.preventDefault();
            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    });
});

console.log('✨ MyShop interactive layer loaded v2.1');
