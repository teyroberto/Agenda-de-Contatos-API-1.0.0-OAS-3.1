const API_URL = 'https://agenda-de-contatos-api-100-oas-31-production.up.railway.app';

const contactsList = document.getElementById('contactsList');
const modal = document.getElementById('contactModal');
const closeBtn = document.querySelector('.close-btn');
const form = document.getElementById('contactForm');
const modalTitle = document.getElementById('modalTitle');
const editNomeOriginal = document.getElementById('editNomeOriginal');

// Abrir modal
document.getElementById('addBtn').addEventListener('click', () => {
  modalTitle.textContent = 'Adicionar Contato';
  form.reset();
  editNomeOriginal.value = '';
  modal.style.display = 'flex';
});

// Fechar modal
closeBtn.addEventListener('click', () => modal.style.display = 'none');
window.addEventListener('click', (e) => {
  if (e.target === modal) modal.style.display = 'none';
});

// Carregar contatos
async function loadContacts() {
  try {
    const res = await fetch(`${API_URL}/contatos`);
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
  }
}

// Adicionar ou editar contato
form.addEventListener('submit', async (e) => {
  e.preventDefault();

  const nome = document.getElementById('nome').value.trim();
  const telefone = document.getElementById('telefone').value.trim();
  const email = document.getElementById('email').value.trim();

  const contact = { nome, telefone, email: email || null };

  const originalNome = editNomeOriginal.value;

  try {
    let res;
    if (originalNome) {
      // Editar (PUT)
      res = await fetch(`${API_URL}/contatos/${encodeURIComponent(originalNome)}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(contact)
      });
    } else {
      // Adicionar (POST)
      res = await fetch(`${API_URL}/contatos`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(contact)
      });
    }

    if (!res.ok) throw new Error('Erro na requisição');
    modal.style.display = 'none';
    loadContacts();
  } catch (err) {
    alert('Erro: ' + err.message);
  }
});

// Editar contato
async function editContact(nome) {
  try {
    const res = await fetch(`${API_URL}/contatos/${encodeURIComponent(nome)}`);
    if (!res.ok) throw new Error('Contato não encontrado');
    const contact = await res.json();

    modalTitle.textContent = 'Editar Contato';
    document.getElementById('nome').value = contact.nome;
    document.getElementById('telefone').value = contact.telefone;
    document.getElementById('email').value = contact.email || '';
    editNomeOriginal.value = contact.nome; // Para saber qual nome original atualizar

    modal.style.display = 'flex';
  } catch (err) {
    alert('Erro ao carregar contato: ' + err.message);
  }
}

// Excluir contato
async function deleteContact(nome) {
  if (!confirm(`Tem certeza que deseja excluir ${nome}?`)) return;

  try {
    const res = await fetch(`${API_URL}/contatos/${encodeURIComponent(nome)}`, {
      method: 'DELETE'
    });
    if (!res.ok) throw new Error('Erro ao excluir');
    loadContacts();
  } catch (err) {
    alert('Erro ao excluir: ' + err.message);
  }
}

// Carregar ao iniciar
loadContacts();