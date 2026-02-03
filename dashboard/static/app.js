const API_BASE = '/api';
const DEFAULT_ENV_KEYS = [
    'TG_BOT_TOKEN', 'VK_BOT_TOKEN', 'TG_CHAT_ID', 'VK_CHAT_ID', 'VK_GROUP_ID'
];

let currentUser = null;
let clients = [];

const loginScreen = document.getElementById('login-screen');
const dashboardScreen = document.getElementById('dashboard-screen');
const loginForm = document.getElementById('login-form');
const clientList = document.getElementById('client-list');
const clientModal = document.getElementById('client-modal');
const clientForm = document.getElementById('client-form');
const envList = document.getElementById('env-list');

checkAuth();

loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const user = document.getElementById('username').value;
    const pass = document.getElementById('password').value;

    const headers = new Headers();
    headers.set('Authorization', 'Basic ' + btoa(user + ":" + pass));

    try {
        const res = await fetch(API_BASE + '/login', { headers });
        if (res.ok) {
            localStorage.setItem('auth', btoa(user + ":" + pass));
            showDashboard();
        } else {
            alert('Неверный логин или пароль');
        }
    } catch (err) {
        alert('Ошибка сети');
    }
});

document.getElementById('logout-btn').addEventListener('click', () => {
    localStorage.removeItem('auth');
    location.reload();
});

document.getElementById('add-client-btn').addEventListener('click', () => {
    openModal();
});

document.getElementById('add-env-btn').addEventListener('click', () => {
    addEnvRow('', '');
});

clientForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const id = document.getElementById('edit-id').value;
    const name = document.getElementById('edit-name').value;

    const env = {};
    document.querySelectorAll('.env-row').forEach(row => {
        const k = row.querySelector('.key').value;
        const v = row.querySelector('.val').value;
        if (k) env[k] = v;
    });

    const payload = { id, name, env };
    await apiCall('/save', 'POST', payload);
    closeModal();
    loadClients();
});

async function checkAuth() {
    const auth = localStorage.getItem('auth');
    if (auth) {
        showDashboard();
    }
}

function showDashboard() {
    loginScreen.classList.add('hidden');
    dashboardScreen.classList.remove('hidden');
    loadClients();
    setInterval(loadClients, 5000);
}

async function apiCall(endpoint, method = 'GET', body = null) {
    const auth = localStorage.getItem('auth');
    if (!auth) return null;

    const opts = {
        method,
        headers: {
            'Authorization': 'Basic ' + auth,
            'Content-Type': 'application/json'
        }
    };
    if (body) opts.body = JSON.stringify(body);

    const res = await fetch(API_BASE + endpoint, opts);
    if (res.status === 401) {
        localStorage.removeItem('auth');
        location.reload();
        return;
    }
    return res.json();
}

async function loadClients() {
    const res = await apiCall('/clients');
    if (res && res.success) {
        clients = res.data;
        renderClients();
    }
}

function renderClients() {
    clientList.innerHTML = '';
    clients.forEach(c => {
        const div = document.createElement('div');
        div.className = `client-card ${c.status}`;

        let actionsHtml = '';
        if (c.status === 'running') {
            actionsHtml = `
                <button class="secondary" onclick="clientAction('${c.id}', 'stop')">Стоп</button>
                <button class="secondary" onclick="clientAction('${c.id}', 'restart')">Рестарт</button>
            `;
        } else {
            actionsHtml = `
                <button onclick="clientAction('${c.id}', 'start')">Запуск</button>
            `;
        }

        div.innerHTML = `
            <h3>${c.name}</h3>
            <div><span class="status-badge ${c.status}">${c.status?.toUpperCase() || 'UNKNOWN'}</span></div>
            <div class="stats">CPU/Mem: ${c.stats || 'N/A'}</div>
            <div class="stats">ID: ${c.container_id?.substring(0, 12) || '-'}</div>
            
            <div class="actions">
                ${actionsHtml}
                <button class="secondary" onclick="editClient('${c.id}')">⚙️</button>
                <button class="danger" onclick="clientAction('${c.id}', 'delete')">🗑️</button>
            </div>
        `;
        clientList.appendChild(div);
    });
}

async function clientAction(id, action) {
    if (action === 'delete' && !confirm('Удалить этого клиента?')) return;
    if (action === 'restart') {
        await clientAction(id, 'stop');
        action = 'start';
    }

    await apiCall(`/action?id=${id}&action=${action}`, 'POST');
    loadClients();
}

function openModal(client = null) {
    clientModal.classList.remove('hidden');
    envList.innerHTML = '';

    if (client) {
        document.getElementById('edit-id').value = client.id;
        document.getElementById('edit-name').value = client.name;

        if (client.env) {
            Object.entries(client.env).forEach(([k, v]) => addEnvRow(k, v));
        }
    } else {
        document.getElementById('edit-id').value = '';
        document.getElementById('edit-name').value = '';
        DEFAULT_ENV_KEYS.forEach(k => addEnvRow(k, ''));
    }
}

function addEnvRow(key, val) {
    const div = document.createElement('div');
    div.className = 'env-row';
    div.innerHTML = `
        <input type="text" class="key" placeholder="VAR_NAME" value="${key}" style="width: 40%">
        <input type="text" class="val" placeholder="Value" value="${val}" style="width: 60%">
        <button type="button" class="danger" onclick="this.parentElement.remove()" style="width: auto; padding: 0 0.5rem; margin:0;">x</button>
    `;
    envList.appendChild(div);
}

function editClient(id) {
    const c = clients.find(x => x.id === id);
    if (c) openModal(c);
}

function closeModal() {
    clientModal.classList.add('hidden');
}
