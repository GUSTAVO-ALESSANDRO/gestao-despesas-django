// Gerencia a alternância e persistência do tema Claro/Escuro
document.addEventListener('DOMContentLoaded', () => {
    const savedTheme = localStorage.getItem('app-theme') || 'light';
    applyTheme(savedTheme);

    // Injeta dinamicamente o botão de alternância de tema no cabeçalho do Django Admin
    if (window.location.pathname.startsWith('/admin') && !document.getElementById('btn-theme-toggle')) {
        const navbarNav = document.querySelector('.navbar-nav.ml-auto, .navbar-nav.ms-auto');
        if (navbarNav) {
            const li = document.createElement('li');
            li.className = 'nav-item align-self-center';
            // Adicionado estilo com margem lateral para afastar do botão de deslogar
            li.style.marginRight = '12px';
            li.style.marginLeft = '12px';
            li.innerHTML = `
                <button class="btn btn-outline-secondary btn-sm rounded-circle" 
                id="btn-theme-toggle" onclick="toggleTheme()" title="Alternar Tema">
                    <i class="fa-solid ${savedTheme === 'dark' ? 'fa-sun' : 'fa-moon'}" id="theme-icon"></i>
                </button>
            `;
            navbarNav.prepend(li);
        }
    }

    // Insere o link de atalho "Ir para o Site" na barra lateral
    if (window.location.pathname.startsWith('/admin')) {
        // Busca o link de usuários na sidebar
        const userLink = document.querySelector('a[href*="/accounts/customuser/"]');
        if (userLink) {
            const userLi = userLink.closest('li');
            if (userLi && !document.getElementById('sidebar-main-site-link')) {
                const newLi = document.createElement('li');
                newLi.className = 'nav-item';
                newLi.id = 'sidebar-main-site-link';
                newLi.innerHTML = `
                    <a href="/" class="nav-link">
                        <i class="nav-icon fa-solid fa-house"></i>
                        <p>Ir para o Site</p>
                    </a>
                `;
                userLi.parentNode.insertBefore(newLi, userLi.nextSibling);
            }
        }
    }
});

// Aplica o tema selecionado (claro ou escuro) ao elemento raiz, atualiza o armazenamento local e altera o ícone visual
function applyTheme(theme) {
    const htmlEl = document.documentElement;
    htmlEl.setAttribute('data-bs-theme', theme);
    localStorage.setItem('app-theme', theme);

    if (theme === 'dark') {
        document.body.classList.add('dark-mode');
    } else {
        document.body.classList.remove('dark-mode');
    }

    const themeIcon = document.getElementById('theme-icon');
    if (themeIcon) {
        if (theme === 'dark') {
            themeIcon.classList.remove('fa-moon');
            themeIcon.classList.add('fa-sun');
        } else {
            themeIcon.classList.remove('fa-sun');
            themeIcon.classList.add('fa-moon');
        }
    }
}

// Alterna o estado atual do tema entre claro e escuro chamando a função de aplicação
function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-bs-theme') || 'light';
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    applyTheme(newTheme);
}