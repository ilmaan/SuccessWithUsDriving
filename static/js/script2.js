// Mobile menu toggle
        const mobileMenuToggle = document.getElementById('mobile-menu-toggle');
        const navMenu = document.getElementById('nav-menu');

        mobileMenuToggle.addEventListener('click', () => {
            navMenu.classList.toggle('active');
        });

        // Header scroll effect
        window.addEventListener('scroll', () => {
            const header = document.getElementById('header');
            if (window.scrollY > 100) {
                header.classList.add('scrolled');
            } else {
                header.classList.remove('scrolled');
            }
        });

        // Smooth scrolling
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });

        // Animate on scroll
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animated');
                }
            });
        }, observerOptions);

        document.querySelectorAll('.animate-on-scroll').forEach(el => {
            observer.observe(el);
        });

        // Chatbot functionality
        const chatbotToggle = document.getElementById('chatbot-toggle');
        const chatbot = document.getElementById('chatbot');
        const closeChatbot = document.getElementById('close-chatbot');
        const chatbotInput = document.getElementById('chatbot-input');
        const sendMessage = document.getElementById('send-message');
        const chatbotMessages = document.getElementById('chatbot-messages');

        chatbotToggle.addEventListener('click', () => {
            chatbot.style.display = chatbot.style.display === 'flex' ? 'none' : 'flex';
        });

        closeChatbot.addEventListener('click', () => {
            chatbot.style.display = 'none';
        });

        function addMessage(message, isUser = false) {
            const messageDiv = document.createElement('div');
            messageDiv.classList.add('message');
            messageDiv.classList.add(isUser ? 'user' : 'bot');
            messageDiv.textContent = message;
            chatbotMessages.appendChild(messageDiv);
            chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
        }

        function getBotResponse(userMessage) {
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
        }

        function sendChatMessage() {
            const message = chatbotInput.value.trim();
            if (message) {
                addMessage(message, true);
                chatbotInput.value = '';
                
                setTimeout(() => {
                    const response = getBotResponse(message);
                    addMessage(response);
                }, 1000);
            }
        }

        sendMessage.addEventListener('click', sendChatMessage);
        chatbotInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                sendChatMessage();
            }
        });

        // Contact form submission
        document.getElementById('contact-form').addEventListener('submit', (e) => {
            e.preventDefault();
            alert('Thank you for your message! We will get back to you soon.');
            e.target.reset();
        });

        // Add floating animation to cards
        document.querySelectorAll('.feature-card, .plan-card').forEach(card => {
            card.addEventListener('mouseenter', () => {
                card.style.transform = 'translateY(-10px) rotateY(5deg)';
            });
            
            card.addEventListener('mouseleave', () => {
                card.style.transform = 'translateY(0) rotateY(0)';
            });
        });

        // Dynamic typing effect for hero
        const heroTitle = document.querySelector('.hero h1');
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

        // // Parallax effect for hero background
        // window.addEventListener('scroll', () => {
        //     const scrolled = window.pageYOffset;
        //     const hero = document.querySelector('.hero');
        //     hero.style.transform = `translateY(${scrolled * 0.5}px)`;
        // });

        // Counter animation for stats
        function animateCounter(element, target) {
            let current = 0;
            const increment = target / 100;
            const timer = setInterval(() => {
                current += increment;
                if (current >= target) {
                    element.textContent = target + (element.textContent.includes('%') ? '%' : element.textContent.includes('+') ? '+' : element.textContent.includes('⭐') ? '⭐' : '');
                    clearInterval(timer);
                } else {
                    element.textContent = Math.floor(current) + (element.textContent.includes('%') ? '%' : element.textContent.includes('+') ? '+' : '');
                }
            }, 20);
        }

        // Trigger counter animation when stats come into view
        const statsObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const statNumbers = entry.target.querySelectorAll('.stat-number');
                    statNumbers.forEach(stat => {
                        const text = stat.textContent;
                        const number = parseInt(text);
                        if (!isNaN(number)) {
                            stat.textContent = '0';
                            animateCounter(stat, number);
                        }
                    });
                    statsObserver.unobserve(entry.target);
                }
            });
        });

        const statsSection = document.querySelector('.stats');
        if (statsSection) {
            statsObserver.observe(statsSection);
        }