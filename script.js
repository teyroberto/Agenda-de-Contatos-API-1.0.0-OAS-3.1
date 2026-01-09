const API_URL = 'https://agenda-de-contatos-api-100-oas-31-production.up.railway.app';

// Elementos
const loginScreen = document.getElementById('loginScreen');
const registerScreen = document.getElementById('registerScreen');
const mainContent = document.getElementById('mainContent');
const contactsList = document.getElementById('contactsList');
const modal = document.getElementById('contactModal');
const closeBtn = document.querySelector('.close-btn');
const contactForm = document.getElementById('contactForm');
const modalTitle = document.getElementById('modalTitle');
const editNomeOriginal = document.getElementById('editNomeOriginal');
const userGreeting = document.getElementById('userGreeting');

// Verifica se já está logado
let token = localStorage.getItem('token');
if (token) {
  showMainContent();
  loadContacts();
} else {
  showLogin();
}

// Funções de tela
function showLogin() {
  loginScreen.style.display = 'block';
  registerScreen.style.display = 'none';
  mainContent.style.display = 'none';
}

function showRegister() {
  loginScreen.style.display = 'none';
  registerScreen.style.display = 'block';
  mainContent.style.display = 'none';
}

function showMainContent() {
  loginScreen.style.display = 'none';
  registerScreen.style.display = 'none';
  mainContent.style.display = 'block';
}

// Cadastro corrigido
document.getElementById('registerForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const nome = document.getElementById('registerNome').value.trim();
  const email = document.getElementById('registerEmail').value.trim();
  const password = document.getElementById('registerPassword').value.trim();

  try {
    const res = await fetch(`${API_URL}/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify({ nome, email, password })
    });

    const data = await res.json();

    if (!res.ok) {
      // Mensagem real do backend (ex: email já existe)
      throw new Error(data.detail || 'Erro desconhecido no servidor');
    }

    alert(data.message || 'Cadastro realizado com sucesso! Faça login.');
    showLogin();
  } catch (err) {
    // Erro claro: rede, CORS, etc.
    console.error('Erro completo no cadastro:', err);
    alert(`Erro no cadastro: ${err.message}\nVerifique console (F12) para detalhes.`);
  }
});

// Login corrigido (similar)
document.getElementById('loginForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const email = document.getElementById('loginEmail').value.trim();
  const password = document.getElementById('loginPassword').value.trim();

  try {
    const res = await fetch(`${API_URL}/token`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
      },
      body: `username=${encodeURIComponent(email)}&password=${encodeURIComponent(password)}`
    });

    if (!res.ok) {
      const errData = await res.json();
      throw new Error(errData.detail || 'Email ou senha incorretos');
    }

    const data = await res.json();
    localStorage.setItem('token', data.access_token);
    token = data.access_token;
    showMainContent();
    loadContacts();
    alert('Login realizado!');
  } catch (err) {
    console.error('Erro completo no login:', err);
    alert(`Erro no login: ${err.message}`);
  }
});

// Toggle telas
document.getElementById('showRegister')?.addEventListener('click', showRegister);
document.getElementById('showLogin')?.addEventListener('click', showLogin);

// Logout
document.getElementById('logoutBtn')?.addEventListener('click', () => {
  localStorage.removeItem('token');
  token = null;
  showLogin();
});

// Carregar contatos protegidos
async function loadContacts() {
  if (!token) return showLogin();

  try {
    const res = await fetch(`${API_URL}/contatos`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });

    if (!res.ok) {
      if (res.status === 401) {
        localStorage.removeItem('token');
        showLogin();
        alert('Sessão expirada. Faça login novamente.');
      }
      throw new Error('Erro ao carregar contatos');
    }

    const data = await res.json();
    contactsList.innerHTML = '';
    data.forEach(contact => {
      const card = document.createElement('div');
      card.className = 'contact-card';
      card.innerHTML = `
        <h3>${contact.nome}</h3>
        <p>Telefone: ${contact.telefone}</p>
        ${contact.email ? `<p>Email: ${contact.email}</p>` : ''}
        <div class="card-actions">
          <button class="btn edit-btn" onclick="editContact('${contact.nome}')">Editar</button>
          <button class="btn delete-btn" onclick="deleteContact('${contact.nome}')">Excluir</button>
        </div>
      `;
      contactsList.appendChild(card);
    });
  } catch (err) {
    alert('Erro: ' + err.message);
  }
}

// ... (mantenha as funções addBtn, editContact, deleteContact, contactForm.submit como no código anterior, mas sempre adicionando o header 'Authorization': `Bearer ${token}` nas fetch)

async function editContact(nome) {
  if (!token) return showLogin();
  // ... (mesmo código anterior, mas com header Authorization)
}

async function deleteContact(nome) {
  if (!token) return showLogin();
  // ... (mesmo código anterior, com header)
}

// Submit do formulário de contato
contactForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  if (!token) return showLogin();
  // ... (mesmo código anterior, com header Authorization)
});

// Botão + Novo Contato
document.getElementById('addBtn')?.addEventListener('click', () => {
  if (!token) return showLogin();
  modalTitle.textContent = 'Adicionar Contato';
  contactForm.reset();
  editNomeOriginal.value = '';
  modal.style.display = 'flex';
});

// Fechar modal
closeBtn.addEventListener('click', () => modal.style.display = 'none');
window.addEventListener('click', (e) => {
  if (e.target === modal) modal.style.display = 'none';
});

// Carregar ao iniciar
if (token) loadContacts();

