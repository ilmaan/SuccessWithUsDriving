// static/js/script.js

// Mobile Menu Toggle
const hamburger = document.querySelector('.hamburger');
const navMenu = document.querySelector('.nav-menu');

hamburger.addEventListener('click', () => {
  navMenu.classList.toggle('active');
});

// Smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function (e) {
    e.preventDefault();
    document.querySelector(this.getAttribute('href')).scrollIntoView({
      behavior: 'smooth'
    });
  });
});

// Form submission (demo)
document.getElementById('instructorForm')?.addEventListener('submit', function(e) {
  e.preventDefault();
  alert('Thank you for your application! We will contact you soon.');
  this.reset();
});

// Animate elements on scroll
const animateOnScroll = () => {
  const elements = document.querySelectorAll('.animate-up');
  elements.forEach(el => {
    const position = el.getBoundingClientRect();
    if (position.top < window.innerHeight - 100) {
      el.style.opacity = 1;
    }
  });
};

window.addEventListener('scroll', animateOnScroll);
window.addEventListener('load', animateOnScroll);