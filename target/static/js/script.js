document.addEventListener('DOMContentLoaded', () => {
  // 1. Lógica da Navbar (Efeito de sombra ao rolar)
  const navbar = document.getElementById('navbar');

  window.addEventListener('scroll', () => {
    if (window.scrollY > 50) {
      navbar.classList.add('scrolled');
    } else {
      navbar.classList.remove('scrolled');
    }
  });

  // 2. Rolagem suave para os links do menu
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      e.preventDefault();
      
      const targetId = this.getAttribute('href');
      if (targetId === '#') return;

      const targetElement = document.querySelector(targetId);
      
      if (targetElement) {
        const headerOffset = 80;
        const elementPosition = targetElement.getBoundingClientRect().top;
        const offsetPosition = elementPosition + window.pageYOffset - headerOffset;
  
        window.scrollTo({
          top: offsetPosition,
          behavior: 'smooth'
        });
      }
    });
  });

  // 3. Lógica da Animação dos Depoimentos (Intersection Observer)
  // Observa quando os elementos com a classe .animate-left entram na tela
  const observerOptions = {
    root: null,
    rootMargin: '0px',
    threshold: 0.15 // Dispara a animação quando 15% do elemento estiver visível
  };

  const observer = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
      // Se o elemento entrou na área visível da tela
      if (entry.isIntersecting) {
        entry.target.classList.add('show');
        // Para de observar o elemento após a animação acontecer uma vez
        observer.unobserve(entry.target);
      }
    });
  }, observerOptions);

  // Seleciona todos os cards de depoimento para aplicar o observador
  const animatedElements = document.querySelectorAll('.animate-left');
  animatedElements.forEach(el => observer.observe(el));
});