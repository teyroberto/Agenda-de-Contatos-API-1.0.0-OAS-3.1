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
const token = localStorage.getItem('token');
if (token) {
  showMainContent();
  loadUserInfo();
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

// Login
document.getElementById('loginForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const email = document.getElementById('loginEmail').value;
  const password = document.getElementById('loginPassword').value;

  try {
    const res = await fetch(`${API_URL}/token`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: `username=${encodeURIComponent(email)}&password=${encodeURIComponent(password)}`
    });
    if (!res.ok) throw new Error('Email ou senha incorretos');
    const data = await res.json();
    localStorage.setItem('token', data.access_token);
    showMainContent();
    loadUserInfo();
    loadContacts();
  } catch (err) {
    alert('Erro no login: ' + err.message);
  }
});

// Cadastro
document.getElementById('registerForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const nome = document.getElementById('registerNome').value;
  const email = document.getElementById('registerEmail').value;
  const password = document.getElementById('registerPassword').value;

  try {
    const res = await fetch(`${API_URL}/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ nome, email, password })
    });
    if (!res.ok) throw new Error('Erro ao cadastrar (email já existe?)');
    alert('Cadastro realizado! Agora faça login.');
    showLogin();
  } catch (err) {
    alert('Erro no cadastro: ' + err.message);
  }
});

// Toggle entre login e cadastro
document.getElementById('showRegister').addEventListener('click', showRegister);
document.getElementById('showLogin').addEventListener('click', showLogin);

// Logout
document.getElementById('logoutBtn').addEventListener('click', () => {
  localStorage.removeItem('token');
  showLogin();
});

// Carregar nome do usuário (simples, pode melhorar depois)
async function loadUserInfo() {
  userGreeting.textContent = 'Bem-vindo(a)!'; // Pode buscar nome real da API depois
}

// Carregar contatos (com token)
async function loadContacts() {
  const token = localStorage.getItem('token');
  if (!token) return;

  try {
    const res = await fetch(`${API_URL}/contatos`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    if (!res.ok) throw new Error('Sessão expirada ou erro');
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
    alert('Erro ao carregar contatos: ' + err.message);
    localStorage.removeItem('token');
    showLogin();
  }
}

// ... (mantenha as funções addBtn, modal, editContact, deleteContact e contactForm.submit do código anterior, mas adicione o header Authorization em todas as fetch)

async function editContact(nome) {
  const token = localStorage.getItem('token');
  try {
    const res = await fetch(`${API_URL}/contatos/${encodeURIComponent(nome)}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    if (!res.ok) throw new Error('Erro ao carregar contato');
    const contact = await res.json();

    modalTitle.textContent = 'Editar Contato';
    document.getElementById('nome').value = contact.nome;
    document.getElementById('telefone').value = contact.telefone;
    document.getElementById('email').value = contact.email || '';
    editNomeOriginal.value = contact.nome;

    modal.style.display = 'flex';
  } catch (err) {
    alert('Erro: ' + err.message);
  }
}

async function deleteContact(nome) {
  if (!confirm(`Tem certeza que deseja excluir ${nome}?`)) return;
  const token = localStorage.getItem('token');
  try {
    const res = await fetch(`${API_URL}/contatos/${encodeURIComponent(nome)}`, {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${token}` }
    });
    if (!res.ok) throw new Error('Erro ao excluir');
    loadContacts();
  } catch (err) {
    alert('Erro ao excluir: ' + err.message);
  }
}

// Submit do formulário de contato (com token)
contactForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const token = localStorage.getItem('token');
  const nome = document.getElementById('nome').value.trim();
  const telefone = document.getElementById('telefone').value.trim();
  const email = document.getElementById('email').value.trim();
  const originalNome = editNomeOriginal.value;

  const contact = { nome, telefone, email: email || null };

  try {
    let res;
    if (originalNome) {
      // Editar
      res = await fetch(`${API_URL}/contatos/${encodeURIComponent(originalNome)}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(contact)
      });
    } else {
      // Adicionar
      res = await fetch(`${API_URL}/contatos`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(contact)
      });
    }

    if (!res.ok) throw new Error('Erro na operação');
    modal.style.display = 'none';
    loadContacts();
  } catch (err) {
    alert('Erro: ' + err.message);
  }
});

// Botão + Novo Contato
document.getElementById('addBtn').addEventListener('click', () => {
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

// Carregar ao iniciar (se já logado)
if (token) loadContacts();
