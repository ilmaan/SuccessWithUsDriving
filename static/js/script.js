// Modern JavaScript for Success Driving School
class DrivingSchoolApp {
  constructor() {
    this.init();
  }

  init() {
    this.setupEventListeners();
    this.initAnimations();
    this.initScrollEffects();
    this.initParallax();
    this.initCounters();
    this.initMobileMenu();
    this.initSmoothScrolling();
    this.initFormHandling();
    this.initLoadingStates();
  }

  setupEventListeners() {
    // Navbar scroll effect
    window.addEventListener('scroll', () => {
      this.handleNavbarScroll();
    });

    // Mobile menu toggle
    const hamburger = document.querySelector('.hamburger');
    if (hamburger) {
      hamburger.addEventListener('click', () => {
        this.toggleMobileMenu();
      });
    }

    // Close mobile menu when clicking outside
    document.addEventListener('click', (e) => {
      if (!e.target.closest('.navbar')) {
        this.closeMobileMenu();
      }
    });

    // Form submissions
    this.setupFormHandlers();
  }

  handleNavbarScroll() {
    const navbar = document.querySelector('.navbar');
    if (window.scrollY > 100) {
      navbar?.classList.add('scrolled');
    } else {
      navbar?.classList.remove('scrolled');
    }
  }

  toggleMobileMenu() {
    const hamburger = document.querySelector('.hamburger');
    const navMenu = document.querySelector('.nav-menu');
    
    hamburger?.classList.toggle('active');
    navMenu?.classList.toggle('active');
    
    // Prevent body scroll when menu is open
    document.body.style.overflow = navMenu?.classList.contains('active') ? 'hidden' : '';
  }

  closeMobileMenu() {
const hamburger = document.querySelector('.hamburger');
const navMenu = document.querySelector('.nav-menu');

    hamburger?.classList.remove('active');
    navMenu?.classList.remove('active');
    document.body.style.overflow = '';
  }

  initAnimations() {
    // Intersection Observer for scroll animations
    const observerOptions = {
      threshold: 0.1,
      rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          
          // Add staggered animations for child elements
          const animatedChildren = entry.target.querySelectorAll('.animate-fade-in-up, .animate-fade-in-left, .animate-fade-in-right, .animate-scale-in');
          animatedChildren.forEach((child, index) => {
            child.style.animationDelay = `${index * 0.1}s`;
            child.style.opacity = '1';
          });
        }
      });
    }, observerOptions);

    // Observe all scroll-trigger elements
    document.querySelectorAll('.scroll-trigger, .feature-card, .pricing-card, .stat-box').forEach(el => {
      observer.observe(el);
    });
  }

  initScrollEffects() {
    // Parallax scrolling for hero section
    window.addEventListener('scroll', () => {
      const scrolled = window.pageYOffset;
      const hero = document.querySelector('.hero');
      if (hero) {
        const rate = scrolled * -0.5;
        hero.style.transform = `translateY(${rate}px)`;
      }
    });

    // Smooth reveal animations
    const revealElements = document.querySelectorAll('.reveal');
    revealElements.forEach(element => {
      const elementTop = element.getBoundingClientRect().top;
      const elementVisible = 150;
      
      if (elementTop < window.innerHeight - elementVisible) {
        element.classList.add('active');
      }
    });
  }

  initParallax() {
    // Parallax effect for background elements
    const parallaxElements = document.querySelectorAll('[data-parallax]');
    
    window.addEventListener('scroll', () => {
      const scrolled = window.pageYOffset;
      
      parallaxElements.forEach(element => {
        const speed = element.dataset.parallax || 0.5;
        const yPos = -(scrolled * speed);
        element.style.transform = `translateY(${yPos}px)`;
      });
    });
  }

  initCounters() {
    // Animated counters for stats
    const counters = document.querySelectorAll('.stat-number');
    
    const animateCounter = (counter) => {
      const text = counter.textContent;
      const target = parseInt(counter.getAttribute('data-target') || text);
      const duration = 2000;
      const step = target / (duration / 16);
      let current = 0;
      
      // Check for special characters to preserve
      const hasPercent = text.includes('%');
      const hasPlus = text.includes('+');
      const hasStar = text.includes('⭐');
      
      counter.textContent = '0';
      
      const timer = setInterval(() => {
        current += step;
        if (current >= target) {
          current = target;
          clearInterval(timer);
        }
        
        // Add back special characters if they existed
        let suffix = '';
        if (hasPercent) suffix = '%';
        if (hasPlus) suffix = '+';
        if (hasStar) suffix = '⭐';
        
        counter.textContent = Math.floor(current).toLocaleString() + suffix;
      }, 16);
    };

    // Observe counters and animate when visible
    const counterObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          animateCounter(entry.target);
          counterObserver.unobserve(entry.target);
        }
      });
    }, { threshold: 0.5 });

    counters.forEach(counter => {
      counterObserver.observe(counter);
    });
    
    // Also observe stats section as a whole
    const statsSection = document.querySelector('.stats');
    if (statsSection) {
      const statsSectionObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            const statNumbers = entry.target.querySelectorAll('.stat-number');
            statNumbers.forEach(stat => {
              animateCounter(stat);
            });
            statsSectionObserver.unobserve(entry.target);
          }
        });
      }, { threshold: 0.5 });
      
      statsSectionObserver.observe(statsSection);
    }
  }

  initMobileMenu() {
    // Enhanced mobile menu with smooth transitions
    const mobileMenuItems = document.querySelectorAll('.nav-menu a');
    
    mobileMenuItems.forEach((item, index) => {
      item.style.transitionDelay = `${index * 0.1}s`;
      
      item.addEventListener('click', () => {
        this.closeMobileMenu();
      });
    });
  }

  initSmoothScrolling() {
// Smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function (e) {
    e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
          const offsetTop = target.offsetTop - 80; // Account for fixed navbar
          
          window.scrollTo({
            top: offsetTop,
      behavior: 'smooth'
    });
        }
  });
});
  }

  setupFormHandlers() {
    // Enhanced form handling with validation and animations
    const forms = document.querySelectorAll('form');

    forms.forEach(form => {
      form.addEventListener('submit', (e) => {
  e.preventDefault();
        this.handleFormSubmission(form);
      });

      // Real-time validation
      const inputs = form.querySelectorAll('input, textarea, select');
      inputs.forEach(input => {
        input.addEventListener('blur', () => {
          this.validateField(input);
        });
        
        input.addEventListener('input', () => {
          this.clearFieldError(input);
        });
      });
    });
  }

  handleFormSubmission(form) {
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn?.textContent;
    
    // Show loading state
    if (submitBtn) {
      submitBtn.textContent = 'Sending...';
      submitBtn.disabled = true;
      submitBtn.classList.add('loading');
    }

    // Simulate form submission (replace with actual API call)
    setTimeout(() => {
      // Show success message
      this.showNotification('Form submitted successfully!', 'success');
      
      // Reset form
      form.reset();
      
      // Reset button
      if (submitBtn) {
        submitBtn.textContent = originalText;
        submitBtn.disabled = false;
        submitBtn.classList.remove('loading');
      }
    }, 2000);
  }

  validateField(field) {
    const value = field.value.trim();
    let isValid = true;
    let errorMessage = '';

    // Remove existing error
    this.clearFieldError(field);

    // Validation rules
    if (field.hasAttribute('required') && !value) {
      isValid = false;
      errorMessage = 'This field is required';
    } else if (field.type === 'email' && value && !this.isValidEmail(value)) {
      isValid = false;
      errorMessage = 'Please enter a valid email address';
    } else if (field.type === 'tel' && value && !this.isValidPhone(value)) {
      isValid = false;
      errorMessage = 'Please enter a valid phone number';
    }

    if (!isValid) {
      this.showFieldError(field, errorMessage);
    }
  }

  isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  isValidPhone(phone) {
    const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;
    return phoneRegex.test(phone.replace(/[\s\-\(\)]/g, ''));
  }

  showFieldError(field, message) {
    field.classList.add('error');
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'field-error';
    errorDiv.textContent = message;
    errorDiv.style.cssText = `
      color: #ef4444;
      font-size: 0.875rem;
      margin-top: 0.25rem;
      animation: fadeInUp 0.3s ease;
    `;
    
    field.parentNode.appendChild(errorDiv);
  }

  clearFieldError(field) {
    field.classList.remove('error');
    const errorDiv = field.parentNode.querySelector('.field-error');
    if (errorDiv) {
      errorDiv.remove();
    }
  }

  showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    // Style the notification
    notification.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      padding: 1rem 1.5rem;
      border-radius: 8px;
      color: white;
      font-weight: 500;
      z-index: 10000;
      transform: translateX(100%);
      transition: transform 0.3s ease;
      max-width: 300px;
      box-shadow: 0 10px 25px rgba(0,0,0,0.2);
    `;

    // Set background color based on type
    const colors = {
      success: '#10b981',
      error: '#ef4444',
      warning: '#f59e0b',
      info: '#3b82f6'
    };
    notification.style.background = colors[type] || colors.info;

    // Add to DOM
    document.body.appendChild(notification);

    // Animate in
    setTimeout(() => {
      notification.style.transform = 'translateX(0)';
    }, 100);

    // Auto remove after 5 seconds
    setTimeout(() => {
      notification.style.transform = 'translateX(100%)';
      setTimeout(() => {
        notification.remove();
      }, 300);
    }, 5000);
  }

  initLoadingStates() {
    // Add loading states to buttons and forms
    const loadingElements = document.querySelectorAll('.loading');
    
    loadingElements.forEach(element => {
      element.addEventListener('click', () => {
        element.classList.add('loading');
        setTimeout(() => {
          element.classList.remove('loading');
        }, 2000);
      });
    });
  }
}

// Enhanced utility functions
const Utils = {
  // Debounce function for performance
  debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  },

  // Throttle function for scroll events
  throttle(func, limit) {
    let inThrottle;
    return function() {
      const args = arguments;
      const context = this;
      if (!inThrottle) {
        func.apply(context, args);
        inThrottle = true;
        setTimeout(() => inThrottle = false, limit);
      }
    };
  },

  // Smooth scroll to element
  scrollToElement(element, offset = 0) {
    const elementPosition = element.getBoundingClientRect().top;
    const offsetPosition = elementPosition + window.pageYOffset - offset;

    window.scrollTo({
      top: offsetPosition,
      behavior: 'smooth'
    });
  },

  // Check if element is in viewport
  isInViewport(element) {
    const rect = element.getBoundingClientRect();
    return (
      rect.top >= 0 &&
      rect.left >= 0 &&
      rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
      rect.right <= (window.innerWidth || document.documentElement.clientWidth)
    );
  }
};

// Enhanced scroll animations
const ScrollAnimations = {
  init() {
    this.setupScrollTriggers();
    this.setupParallaxEffects();
  },

  setupScrollTriggers() {
    const elements = document.querySelectorAll('[data-scroll]');
    
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const animation = entry.target.dataset.scroll;
          entry.target.classList.add(animation);
        }
      });
    }, { threshold: 0.1 });

    elements.forEach(el => observer.observe(el));
  },

  setupParallaxEffects() {
    const parallaxElements = document.querySelectorAll('[data-parallax]');
    
    window.addEventListener('scroll', Utils.throttle(() => {
      const scrolled = window.pageYOffset;
      
      parallaxElements.forEach(element => {
        const speed = parseFloat(element.dataset.parallax) || 0.5;
        const yPos = -(scrolled * speed);
        element.style.transform = `translateY(${yPos}px)`;
      });
    }, 16));
  }
};

// Enhanced mobile menu
const MobileMenu = {
  init() {
    this.setupEventListeners();
    this.setupAnimations();
  },

  setupEventListeners() {
    const hamburger = document.querySelector('.hamburger');
    const navMenu = document.querySelector('.nav-menu');
    const overlay = document.querySelector('.mobile-overlay');

    if (hamburger) {
      hamburger.addEventListener('click', () => this.toggle());
    }

    // Close on overlay click
    if (overlay) {
      overlay.addEventListener('click', () => this.close());
    }

    // Close on escape key
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') this.close();
    });
  },

  setupAnimations() {
    const menuItems = document.querySelectorAll('.nav-menu a');
    
    menuItems.forEach((item, index) => {
      item.style.transitionDelay = `${index * 0.1}s`;
    });
  },

  toggle() {
    const hamburger = document.querySelector('.hamburger');
    const navMenu = document.querySelector('.nav-menu');
    const body = document.body;

    hamburger?.classList.toggle('active');
    navMenu?.classList.toggle('active');
    body.style.overflow = navMenu?.classList.contains('active') ? 'hidden' : '';
  },

  close() {
    const hamburger = document.querySelector('.hamburger');
    const navMenu = document.querySelector('.nav-menu');
    const body = document.body;

    hamburger?.classList.remove('active');
    navMenu?.classList.remove('active');
    body.style.overflow = '';
  }
};

// Enhanced form handling
const FormHandler = {
  init() {
    this.setupValidation();
    this.setupAutoSave();
  },

  setupValidation() {
    const forms = document.querySelectorAll('form[data-validate]');
    
    forms.forEach(form => {
      const inputs = form.querySelectorAll('input, textarea, select');
      
      inputs.forEach(input => {
        input.addEventListener('blur', () => this.validateField(input));
        input.addEventListener('input', () => this.clearFieldError(input));
      });
    });
  },

  setupAutoSave() {
    const forms = document.querySelectorAll('form[data-autosave]');
    
    forms.forEach(form => {
      const inputs = form.querySelectorAll('input, textarea, select');
      
      inputs.forEach(input => {
        input.addEventListener('input', Utils.debounce(() => {
          this.saveFormData(form);
        }, 1000));
      });
    });
  },

  validateField(field) {
    // Enhanced validation logic
    const value = field.value.trim();
    const rules = field.dataset.validation?.split('|') || [];
    
    for (const rule of rules) {
      const [ruleName, ruleValue] = rule.split(':');
      
      if (!this.validateRule(ruleName, value, ruleValue)) {
        this.showFieldError(field, this.getErrorMessage(ruleName, ruleValue));
        return false;
      }
    }
    
    this.clearFieldError(field);
    return true;
  },

  validateRule(rule, value, ruleValue) {
    switch (rule) {
      case 'required':
        return value.length > 0;
      case 'min':
        return value.length >= parseInt(ruleValue);
      case 'max':
        return value.length <= parseInt(ruleValue);
      case 'email':
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
      case 'phone':
        return /^[\+]?[1-9][\d]{0,15}$/.test(value.replace(/[\s\-\(\)]/g, ''));
      default:
        return true;
    }
  },

  getErrorMessage(rule, ruleValue) {
    const messages = {
      required: 'This field is required',
      min: `Minimum ${ruleValue} characters required`,
      max: `Maximum ${ruleValue} characters allowed`,
      email: 'Please enter a valid email address',
      phone: 'Please enter a valid phone number'
    };
    return messages[rule] || 'Invalid input';
  },

  showFieldError(field, message) {
    this.clearFieldError(field);
    
    field.classList.add('error');
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'field-error';
    errorDiv.textContent = message;
    
    field.parentNode.appendChild(errorDiv);
  },

  clearFieldError(field) {
    field.classList.remove('error');
    const errorDiv = field.parentNode.querySelector('.field-error');
    if (errorDiv) errorDiv.remove();
  },

  saveFormData(form) {
    const formData = new FormData(form);
    const data = Object.fromEntries(formData);
    
    // Save to localStorage
    localStorage.setItem(`form_${form.dataset.autosave}`, JSON.stringify(data));
  },

  loadFormData(form) {
    const saved = localStorage.getItem(`form_${form.dataset.autosave}`);
    if (saved) {
      const data = JSON.parse(saved);
      
      Object.keys(data).forEach(key => {
        const field = form.querySelector(`[name="${key}"]`);
        if (field) field.value = data[key];
      });
    }
  }
};

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  // Initialize main app
  new DrivingSchoolApp();
  
  // Initialize additional modules
  ScrollAnimations.init();
  MobileMenu.init();
  FormHandler.init();
  ChatbotHandler.init();
  
  // Add some fun interactive elements
  addInteractiveElements();
  
  // Initialize dynamic typing effect for hero
  initDynamicTyping();
});

// Chatbot functionality
const ChatbotHandler = {
  init() {
    this.setupEventListeners();
  },
  
  setupEventListeners() {
    const chatbotToggle = document.getElementById('chatbot-toggle');
    const chatbot = document.getElementById('chatbot');
    const closeChatbot = document.getElementById('close-chatbot');
    const chatbotInput = document.getElementById('chatbot-input');
    const sendMessage = document.getElementById('send-message');
    const chatbotMessages = document.getElementById('chatbot-messages');
    
    if (chatbotToggle) {
      chatbotToggle.addEventListener('click', () => {
        if (chatbot) {
          chatbot.classList.toggle('active');
        }
      });
    }
    
    if (closeChatbot) {
      closeChatbot.addEventListener('click', () => {
        if (chatbot) {
          chatbot.classList.remove('active');
        }
      });
    }
    
    if (sendMessage && chatbotInput) {
      sendMessage.addEventListener('click', () => this.sendChatMessage(chatbotInput, chatbotMessages));
      
      chatbotInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
          this.sendChatMessage(chatbotInput, chatbotMessages);
        }
      });
    }
  },
  
  addMessage(message, isUser = false, chatbotMessages) {
    if (!chatbotMessages) return;
    
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message');
    messageDiv.classList.add(isUser ? 'user-message' : 'bot-message');
    messageDiv.textContent = message;
    chatbotMessages.appendChild(messageDiv);
    chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
  },
  
  getBotResponse(userMessage) {
    const message = userMessage.toLowerCase();
    
    if (message.includes('price') || message.includes('cost') || message.includes('plan')) {
      return "Our plans range from $160 for 2 hours to $650 for 10 hours. The most popular 8-hour package is $560. Would you like more details about a specific plan?";
    } else if (message.includes('schedule') || message.includes('book')) {
      return "You can easily schedule lessons through our online booking system. Simply register for an account and choose your preferred time slots. Our instructors are available Monday-Friday 8AM-7PM and weekends 9AM-5PM.";
    } else if (message.includes('dmv') || message.includes('test')) {
      return "We offer comprehensive DMV test preparation including behind-the-wheel test prep, written exam practice, and guidance on paperwork and test routes. Our pass rate is 95%!";
    } else if (message.includes('instructor')) {
      return "All our instructors are certified professionals with years of experience. You can request a specific instructor when booking, and we'll do our best to accommodate your preference.";
    } else if (message.includes('location') || message.includes('address')) {
      return "We're located in Santa Clara, California. We serve the entire Santa Clara area and surrounding regions.";
    } else if (message.includes('cancel')) {
      return "You can cancel lessons without charge if done 24+ hours in advance. Cancellations within 24 hours will result in a 50% credit deduction.";
    } else {
      return "I'm here to help with questions about our driving school, pricing, scheduling, DMV test prep, and more. What specific information would you like to know?";
    }
  },
  
  sendChatMessage(chatbotInput, chatbotMessages) {
    if (!chatbotInput || !chatbotMessages) return;
    
    const message = chatbotInput.value.trim();
    if (message) {
      this.addMessage(message, true, chatbotMessages);
      chatbotInput.value = '';
      
      setTimeout(() => {
        const response = this.getBotResponse(message);
        this.addMessage(response, false, chatbotMessages);
      }, 1000);
    }
  }
};

// Dynamic typing effect for hero
function initDynamicTyping() {
  const heroTitle = document.querySelector('.hero h1');
  if (!heroTitle) return;
  
  const originalText = heroTitle.textContent;
  heroTitle.textContent = '';
  
  let i = 0;
  function typeWriter() {
    if (i < originalText.length) {
      heroTitle.textContent += originalText.charAt(i);
      i++;
      setTimeout(typeWriter, 100);
    }
  }
  
  setTimeout(typeWriter, 1000);
}

// Add some fun interactive elements
function addInteractiveElements() {
  // Floating action button
  const fab = document.createElement('div');
  fab.className = 'floating-action-btn';
  fab.innerHTML = '<i class="fas fa-car"></i>';
  fab.style.cssText = `
    position: fixed;
    bottom: 30px;
    right: 30px;
    width: 60px;
    height: 60px;
    background: var(--gradient-primary);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 1.5rem;
    cursor: pointer;
    box-shadow: var(--shadow-xl);
    transition: all 0.3s ease;
    z-index: 1000;
    animation: float 3s ease-in-out infinite;
  `;
  
  fab.addEventListener('click', () => {
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });
  
  fab.addEventListener('mouseenter', () => {
    fab.style.transform = 'scale(1.1) rotate(5deg)';
  });
  
  fab.addEventListener('mouseleave', () => {
    fab.style.transform = 'scale(1) rotate(0deg)';
  });
  
  document.body.appendChild(fab);
  
  // Add some particle effects to hero section
  addParticleEffects();
}

// Add particle effects to hero section
function addParticleEffects() {
  const hero = document.querySelector('.hero');
  if (!hero) return;
  
  for (let i = 0; i < 50; i++) {
    const particle = document.createElement('div');
    particle.className = 'particle';
    particle.style.cssText = `
      position: absolute;
      width: 4px;
      height: 4px;
      background: rgba(255, 255, 255, 0.3);
      border-radius: 50%;
      pointer-events: none;
      animation: float ${3 + Math.random() * 4}s ease-in-out infinite;
      animation-delay: ${Math.random() * 2}s;
    `;
    
    particle.style.left = Math.random() * 100 + '%';
    particle.style.top = Math.random() * 100 + '%';
    
    hero.appendChild(particle);
  }
}

// Add CSS for new interactive elements
const additionalStyles = `
  .floating-action-btn:hover {
    transform: scale(1.1) rotate(5deg) !important;
    box-shadow: 0 25px 50px -12px rgba(0,0,0,0.4) !important;
  }
  
  .particle {
    animation: float 3s ease-in-out infinite;
  }
  
  .field-error {
    color: #ef4444;
    font-size: 0.875rem;
    margin-top: 0.25rem;
    animation: fadeInUp 0.3s ease;
  }
  
  .error {
    border-color: #ef4444 !important;
    box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1) !important;
  }
  
  .notification {
    animation: slideInRight 0.3s ease;
  }
  
  @keyframes slideInRight {
    from {
      transform: translateX(100%);
      opacity: 0;
    }
    to {
      transform: translateX(0);
      opacity: 1;
    }
  }
`;

// Inject additional styles
const styleSheet = document.createElement('style');
styleSheet.textContent = additionalStyles;
document.head.appendChild(styleSheet);
