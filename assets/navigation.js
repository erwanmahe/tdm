document.addEventListener('DOMContentLoaded', function() {
    // Ne rien faire sur la page d'accueil
    if (window.location.pathname === '/index.html' || window.location.pathname === '/') {
        return;
    }

    // Récupérer tous les liens du menu de navigation
    const navLinks = Array.from(document.querySelectorAll('.nav a.link'));
    
    // Trouver le lien actif
    const currentLink = document.querySelector('.nav a.link.active');
    
    if (!currentLink) return;
    
    // Trouver l'index du lien actif
    const currentIndex = navLinks.findIndex(link => link === currentLink);
    
    // Trouver le prochain lien (sauter les séparateurs)
    let nextIndex = currentIndex + 1;
    while (nextIndex < navLinks.length && 
           (navLinks[nextIndex].classList.contains('section') || 
            !navLinks[nextIndex].getAttribute('href'))) {
        nextIndex++;
    }
    
    // Si on a trouvé un lien suivant valide
    if (nextIndex < navLinks.length && !navLinks[nextIndex].classList.contains('section')) {
        const nextLink = navLinks[nextIndex];
        const nextUrl = nextLink.getAttribute('href');
        const nextText = nextLink.textContent;
        
        // Créer le lien "Ville suivante"
        let nextPageLink = document.createElement('a');
        nextPageLink.href = nextUrl;
        nextPageLink.textContent = `Ville suivante : ${nextText} →`;
        nextPageLink.style.textDecoration = 'none';
        nextPageLink.style.color = 'var(--md-primary)';
        nextPageLink.style.fontWeight = '500';
        
        // Créer un conteneur pour les liens de navigation en bas de page
        let navContainer = document.createElement('div');
        navContainer.style.display = 'flex';
        navContainer.style.justifyContent = 'space-between';
        navContainer.style.alignItems = 'center';
        navContainer.style.marginTop = '40px';
        navContainer.style.paddingTop = '20px';
        navContainer.style.borderTop = '1px solid var(--md-border)';
        
        // Créer un conteneur pour le lien "Retour en haut"
        const backToTopLink = document.createElement('a');
        backToTopLink.href = '#';
        backToTopLink.textContent = '↑ Retour en haut';
        backToTopLink.style.textDecoration = 'none';
        backToTopLink.style.color = 'var(--md-primary)';
        backToTopLink.style.fontWeight = '500';
        backToTopLink.onclick = function(e) {
            e.preventDefault();
            window.scrollTo({top: 0, behavior: 'smooth'});
        };
        
        // Ajouter les liens au conteneur
        navContainer.appendChild(backToTopLink);
        navContainer.appendChild(nextPageLink);
        
        // Ajouter le conteneur en bas de la page
        const mainContent = document.querySelector('.content');
        if (mainContent) {
            mainContent.appendChild(navContainer);
        }
    }
});
