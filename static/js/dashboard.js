// Dashboard-specific JavaScript
document.addEventListener('DOMContentLoaded', function() {
    
    // Animate stat cards on scroll
    const observerOptions = {
        threshold: 0.2,
        rootMargin: '0px 0px -100px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '0';
                entry.target.style.transform = 'translateY(20px)';
                
                setTimeout(() => {
                    entry.target.style.transition = 'all 0.6s ease';
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }, 100);
                
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    // Observe all stat cards
    document.querySelectorAll('.stat-card').forEach(card => {
        observer.observe(card);
    });
    
    // Observe timeline items
    document.querySelectorAll('.timeline-item').forEach((item, index) => {
        item.style.opacity = '0';
        item.style.transform = 'translateX(-20px)';
        
        setTimeout(() => {
            item.style.transition = 'all 0.5s ease';
            item.style.opacity = '1';
            item.style.transform = 'translateX(0)';
        }, 200 * index);
    });
    
    // Add counter animation to stat values
    function animateValue(element, start, end, duration) {
        let startTimestamp = null;
        const step = (timestamp) => {
            if (!startTimestamp) startTimestamp = timestamp;
            const progress = Math.min((timestamp - startTimestamp) / duration, 1);
            const value = Math.floor(progress * (end - start) + start);
            element.textContent = value;
            if (progress < 1) {
                window.requestAnimationFrame(step);
            }
        };
        window.requestAnimationFrame(step);
    }
    
    // Animate stat values when they come into view
    const statObserver = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const valueElement = entry.target.querySelector('.stat-value');
                const finalValue = parseInt(valueElement.textContent);
                animateValue(valueElement, 0, finalValue, 2000);
                statObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.5 });
    
    document.querySelectorAll('.stat-card').forEach(card => {
        statObserver.observe(card);
    });
    
    // Add pulse effect to hero bars
    const bars = document.querySelectorAll('.bar');
    bars.forEach((bar, index) => {
        setInterval(() => {
            bar.style.opacity = '0.7';
            setTimeout(() => {
                bar.style.transition = 'opacity 0.5s ease';
                bar.style.opacity = '1';
            }, 100);
        }, 3000 + (index * 500));
    });
    
    // Interactive timeline markers
    document.querySelectorAll('.timeline-marker').forEach(marker => {
        marker.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.5)';
            this.style.transition = 'transform 0.3s ease';
        });
        
        marker.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
        });
    });
    
    // Add parallax effect to inspiration section
    window.addEventListener('scroll', function() {
        const inspirationSection = document.querySelector('.inspiration-section');
        if (inspirationSection) {
            const scrolled = window.pageYOffset;
            const rate = scrolled * 0.3;
            inspirationSection.style.transform = `translateY(${rate}px)`;
        }
    });
    
    console.log('Dashboard initialized successfully!');
});