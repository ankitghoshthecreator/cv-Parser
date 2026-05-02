let currentUser = null;
let regData = {};

function showView(viewId) {
    document.querySelectorAll('.view').forEach(v => v.classList.add('hidden'));
    document.getElementById(viewId).classList.remove('hidden');
}

function showToast(message) {
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.innerHTML = message;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 5000);
}

// --- Auth Handlers ---

async function handleRegister() {
    const data = {
        name: document.getElementById('reg-name').value,
        email: document.getElementById('reg-email').value,
        phone: document.getElementById('reg-phone').value,
        role: document.getElementById('reg-role').value,
        password: document.getElementById('reg-pass').value,
        confirm_password: document.getElementById('reg-confirm').value
    };

    const response = await fetch('/api/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });

    const result = await response.json();
    if (response.ok) {
        regData = data; // Save for verification
        document.getElementById('reg-step-1').classList.add('hidden');
        document.getElementById('reg-step-otp').classList.remove('hidden');
        
        // Show OTP in toast for demo
        showToast(`📬 <strong>OTP Sent!</strong><br>Your verification code is: <span style="color: var(--primary); font-size: 1.2rem;">${result.debug_otp}</span>`);
    } else {
        alert(result.error);
    }
}

async function handleVerifyOTP() {
    const otp = document.getElementById('reg-otp').value;
    const response = await fetch('/api/verify-otp', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...regData, otp })
    });

    const result = await response.json();
    if (response.ok) {
        alert(result.message);
        showView('login-view');
    } else {
        alert(result.error);
    }
}

async function handleLogin() {
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-pass').value;

    const response = await fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
    });

    const result = await response.json();
    if (response.ok) {
        const decoded = JSON.parse(atob(result.token.split('.')[1]));
        currentUser = { ...result, id: decoded.id };
        
        // Update UI
        document.getElementById('nav-links').classList.add('hidden');
        document.getElementById('user-nav').classList.remove('hidden');
        document.getElementById('user-name-display').textContent = `Hello, ${result.name}`;
        
        // Redirect based on role
        if (result.role === 'student') {
            showView('student-view');
        } else if (result.role === 'employer') {
            showView('employer-view');
        } else if (result.role === 'management') {
            showView('management-view');
            loadManagementData();
        }
    } else {
        alert(result.error);
    }
}

function logout() {
    currentUser = null;
    document.getElementById('nav-links').classList.remove('hidden');
    document.getElementById('user-nav').classList.add('hidden');
    showView('login-view');
}

// --- Employer Handlers ---

async function handlePostJob() {
    const data = {
        title: document.getElementById('job-title').value,
        category: document.getElementById('job-cat').value,
        required_skills: document.getElementById('job-skills').value,
        description: document.getElementById('job-desc').value,
        employer_id: currentUser.id
    };

    const response = await fetch('/api/jobs', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });

    const result = await response.json();
    alert(result.message);
}

// --- Student Handlers ---

async function handleCVUpload() {
    const file = document.getElementById('cv-upload').files[0];
    if (!file) return alert('Select a file first');

    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`/api/upload-cv?user_id=${currentUser.id}`, {
        method: 'POST',
        body: formData
    });

    const result = await response.json();
    if (response.ok) {
        document.getElementById('skills-found').innerHTML = `<strong>Skills found:</strong> ${result.skills.join(', ')}`;
        loadMatches();
    } else {
        alert(result.error);
    }
}

async function loadMatches() {
    const response = await fetch(`/api/matches/${currentUser.id}`);
    const matches = await response.json();
    
    const container = document.getElementById('job-recommendations');
    container.innerHTML = '';
    
    if (matches.length === 0) {
        container.innerHTML = '<p>No jobs found in the system yet.</p>';
        return;
    }

    matches.forEach(m => {
        const div = document.createElement('div');
        div.className = 'job-item';
        div.innerHTML = `
            <div>
                <div style="font-weight: 700;">${m.title}</div>
                <div style="font-size: 0.8rem; color: var(--text-gray);">${m.category}</div>
            </div>
            <div class="job-score">${m.score}% Match</div>
        `;
        container.appendChild(div);
    });
}

// --- Management Handlers ---

async function loadManagementData() {
    const response = await fetch('/api/analytics');
    const data = await response.json();
    
    const container = document.getElementById('gap-analytics-list');
    container.innerHTML = '';
    
    data.forEach(item => {
        const div = document.createElement('div');
        div.style.marginBottom = '1.5rem';
        const total = item.needed + item.available;
        const width = item.needed > 0 ? (item.available / item.needed) * 100 : 100;
        
        div.innerHTML = `
            <div style="display: flex; justify-content: space-between; font-size: 0.9rem;">
                <span>${item.skill.toUpperCase()}</span>
                <span style="color: var(--text-gray);">Demand: ${item.needed} | Available: ${item.available}</span>
            </div>
            <div class="gap-bar">
                <div class="gap-fill" style="width: ${Math.min(100, width)}%; background: ${width < 50 ? 'var(--secondary)' : 'var(--success)'};"></div>
            </div>
            ${item.gap > 0 ? `<div style="font-size: 0.75rem; color: var(--secondary); margin-top: 0.2rem;">Deficit: ${item.gap} students needed</div>` : ''}
        `;
        container.appendChild(div);
    });
}

async function downloadReport() {
    window.open('/api/report', '_blank');
}
