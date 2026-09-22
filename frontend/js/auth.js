let currentTab = 'signin';
let selectedRole = 'client'; // default

function switchTab(tab) {
    currentTab = tab;
    const signinBtn = document.getElementById('tab-signin');
    const signupBtn = document.getElementById('tab-signup');
    const fieldName = document.getElementById('field-name');
    const fieldCompany = document.getElementById('field-company');
    const fieldRole = document.getElementById('field-role');
    const title = document.getElementById('card-title');
    const subtitle = document.getElementById('card-subtitle');
    const submitBtn = document.getElementById('submit-btn');
    const switchLink = document.getElementById('switch-link');
    const forgotLink = document.getElementById('forgot-link');
    const errorMsg = document.getElementById('error-msg');

    errorMsg.classList.add('hidden');

    if (tab === 'signin') {
        signinBtn.className = 'pb-3 mr-6 text-sm font-semibold tab-active';
        signupBtn.className = 'pb-3 text-sm font-semibold tab-inactive';
        fieldName.classList.add('hidden');
        fieldCompany.classList.add('hidden');
        fieldRole.classList.add('hidden'); // Role is fetched from DB on signin
        title.textContent = 'Welcome back';
        subtitle.textContent = 'Sign in to your Wisdom Group account';
        submitBtn.textContent = 'Sign In';
        switchLink.innerHTML = `Don't have an account? <button type="button" onclick="switchTab('signup')" class="text-indigo-600 hover:text-indigo-700 font-bold transition-colors ml-1">Create one</button>`;
        forgotLink.classList.remove('hidden');
    } else {
        signinBtn.className = 'pb-3 mr-6 text-sm font-semibold tab-inactive';
        signupBtn.className = 'pb-3 text-sm font-semibold tab-active';
        fieldName.classList.remove('hidden');
        fieldCompany.classList.remove('hidden');
        fieldRole.classList.remove('hidden');
        title.textContent = 'Create an account';
        subtitle.textContent = 'Join Wisdom Group matchmaking platform';
        submitBtn.textContent = 'Create Account';
        switchLink.innerHTML = `Already have an account? <button type="button" onclick="switchTab('signin')" class="text-indigo-600 hover:text-indigo-700 font-bold transition-colors ml-1">Sign in</button>`;
        forgotLink.classList.add('hidden');
    }
}

function selectRole(role, el) {
    selectedRole = role;
    document.querySelectorAll('.role-card').forEach(card => card.classList.remove('selected'));
    el.classList.add('selected');
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    const clientCard = document.querySelector('[data-role="client"]');
    if (clientCard) clientCard.classList.add('selected');
    switchTab('signin');
});

document.getElementById('auth-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value.trim();
    const err = document.getElementById('error-msg');
    const submitBtn = document.getElementById('submit-btn');
    
    let name = '';
    let company = '';
    if (currentTab === 'signup') {
        name = document.getElementById('name').value.trim();
        company = document.getElementById('company').value.trim();
        if (!name || !company) {
            err.innerHTML = '<span>Please enter your full name and company name.</span>';
            err.classList.remove('hidden');
            return;
        }
    }

    if (!email || !password) {
        err.innerHTML = '<span>Please fill in email and password.</span>';
        err.classList.remove('hidden');
        return;
    }

    err.classList.add('hidden');
    submitBtn.disabled = true;

    try {
        if (currentTab === 'signup') {
            const res = await fetch('/api/auth/signup', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    full_name: name,
                    email: email,
                    password: password,
                    role: selectedRole,
                    company_name: company
                })
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || 'Signup failed');
            localStorage.setItem('profile_id', data.id);
            localStorage.setItem('role', data.role);
            redirectRole(data.role);
        } else {
            const res = await fetch('/api/auth/signin', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    email: email,
                    password: password
                })
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || 'Signin failed');
            localStorage.setItem('profile_id', data.id);
            localStorage.setItem('role', data.role);
            redirectRole(data.role);
        }
    } catch(error) {
        err.innerHTML = `<span>${error.message}</span>`;
        err.classList.remove('hidden');
    } finally {
        submitBtn.disabled = false;
    }
});

function redirectRole(role) {
    if (role === 'admin') {
        window.location.href = '/admin/dashboard';
    } else if (role === 'client') {
        window.location.href = '/client/dashboard';
    } else if (role === 'supplier') {
        window.location.href = '/supplier/dashboard';
    } else {
        window.location.href = '/';
    }
}
