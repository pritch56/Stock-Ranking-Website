// Authentication JavaScript

const API_BASE_URL = (() => {
    const { protocol, hostname } = window.location;
    const port = hostname === 'localhost' ? ':8000' : '';
    return `${protocol}//${hostname}${port}`;
})();

// Check if user is authenticated
async function checkAuth() {
    try {
        const response = await fetch(`${API_BASE_URL}/auth/check`, {
            credentials: 'include'
        });
        const data = await response.json();
        return data.authenticated ? data : null;
    } catch (error) {
        console.error('Auth check failed:', error);
        return null;
    }
}

// Get current user details
async function getCurrentUser() {
    try {
        const response = await fetch(`${API_BASE_URL}/auth/me`, {
            credentials: 'include'
        });
        if (response.ok) {
            return await response.json();
        }
        return null;
    } catch (error) {
        console.error('Failed to get current user:', error);
        return null;
    }
}

// Show auth modal (Google OAuth + email/password)
function login() {
    _ensureAuthModal();
    document.getElementById('auth-modal').classList.remove('hidden');
    _setAuthMode('signin');
}

// Logout
async function logout() {
    try {
        await fetch(`${API_BASE_URL}/auth/logout`, {
            method: 'POST',
            credentials: 'include'
        });
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
        window.location.href = '/';
    } catch (error) {
        console.error('Logout failed:', error);
    }
}

// Save token from URL (after OAuth callback)
function saveTokenFromURL() {
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');

    if (token) {
        localStorage.setItem('access_token', token);
        window.history.replaceState({}, document.title, window.location.pathname);
        return token;
    }

    return localStorage.getItem('access_token');
}

// Update UI based on auth state
async function updateAuthUI() {
    const authData = await checkAuth();

    const signInButtons = document.querySelectorAll('[data-auth="signin"]');
    const signOutButtons = document.querySelectorAll('[data-auth="signout"]');
    const userEmailElements = document.querySelectorAll('[data-user="email"]');

    if (authData) {
        signInButtons.forEach(btn => btn.style.display = 'none');
        signOutButtons.forEach(btn => btn.style.display = 'block');
        userEmailElements.forEach(el => el.textContent = authData.email);
    } else {
        signInButtons.forEach(btn => btn.style.display = 'block');
        signOutButtons.forEach(btn => btn.style.display = 'none');
        userEmailElements.forEach(el => el.textContent = '');
    }

    return authData;
}

// Require authentication (redirect to home if not authenticated)
async function requireAuth() {
    const authData = await checkAuth();
    if (!authData) {
        window.location.href = '/';
        return null;
    }
    return authData;
}

// --- Auth modal ---

function _ensureAuthModal() {
    if (document.getElementById('auth-modal')) return;

    document.body.insertAdjacentHTML('beforeend', `
        <div id="auth-modal" class="hidden fixed inset-0 z-[100] flex items-center justify-center p-4" style="background:rgba(0,0,0,0.7)">
            <div class="relative w-full max-w-md rounded-2xl border border-gray-700 p-8" style="background:#111827">
                <button id="auth-modal-close" class="absolute top-4 right-4 text-gray-500 hover:text-white text-xl leading-none">&times;</button>

                <h2 id="auth-modal-title" class="text-2xl font-bold mb-6 text-white">Sign In</h2>

                <!-- Google OAuth -->
                <a id="auth-google-btn" href="${API_BASE_URL}/auth/login"
                   class="flex items-center justify-center gap-3 w-full py-3 rounded-lg border border-gray-600 hover:border-gray-400 text-white font-semibold transition mb-6">
                    <svg width="18" height="18" viewBox="0 0 48 48"><path fill="#EA4335" d="M24 9.5c3.5 0 6.6 1.2 9 3.2l6.7-6.7C35.8 2.5 30.3 0 24 0 14.6 0 6.6 5.5 2.7 13.5l7.8 6C12.4 13.2 17.8 9.5 24 9.5z"/><path fill="#4285F4" d="M46.5 24.5c0-1.6-.1-3.1-.4-4.5H24v8.5h12.7c-.6 3-2.3 5.5-4.8 7.2l7.5 5.8c4.4-4.1 7.1-10.1 7.1-17z"/><path fill="#FBBC05" d="M10.5 28.5A14.3 14.3 0 0 1 9.5 24c0-1.6.3-3.1.8-4.5l-7.8-6A23.9 23.9 0 0 0 0 24c0 3.9.9 7.5 2.7 10.7l7.8-6.2z"/><path fill="#34A853" d="M24 48c6.3 0 11.6-2.1 15.5-5.7l-7.5-5.8c-2.1 1.4-4.8 2.2-8 2.2-6.2 0-11.5-3.7-13.5-9l-7.8 6.1C6.6 42.5 14.6 48 24 48z"/></svg>
                    Continue with Google
                </a>

                <div class="flex items-center gap-4 mb-6">
                    <hr class="flex-1 border-gray-700">
                    <span class="text-gray-500 text-sm">or</span>
                    <hr class="flex-1 border-gray-700">
                </div>

                <form id="auth-password-form" class="space-y-4">
                    <input id="auth-email" type="email" placeholder="Email address" required
                           class="w-full px-4 py-3 rounded-lg border border-gray-700 bg-gray-900 text-white placeholder-gray-500 focus:outline-none focus:border-blue-500">
                    <input id="auth-password" type="password" placeholder="Password" required
                           class="w-full px-4 py-3 rounded-lg border border-gray-700 bg-gray-900 text-white placeholder-gray-500 focus:outline-none focus:border-blue-500">
                    <input id="auth-confirm-password" type="password" placeholder="Confirm password" required
                           class="hidden w-full px-4 py-3 rounded-lg border border-gray-700 bg-gray-900 text-white placeholder-gray-500 focus:outline-none focus:border-blue-500">
                    <p id="auth-error" class="text-red-400 text-sm hidden"></p>
                    <button type="submit" id="auth-submit-btn"
                            class="w-full py-3 bg-blue-600 hover:bg-blue-700 rounded-lg font-semibold text-white transition">
                        Sign In
                    </button>
                </form>

                <p class="text-center text-sm text-gray-500 mt-4">
                    <span id="auth-toggle-text">Don't have an account?</span>
                    <button id="auth-mode-toggle" class="text-blue-400 hover:text-blue-300 ml-1">Create account</button>
                </p>
            </div>
        </div>
    `);

    document.getElementById('auth-modal-close').addEventListener('click', () => {
        document.getElementById('auth-modal').classList.add('hidden');
    });

    document.getElementById('auth-modal').addEventListener('click', (e) => {
        if (e.target === document.getElementById('auth-modal')) {
            document.getElementById('auth-modal').classList.add('hidden');
        }
    });

    document.getElementById('auth-mode-toggle').addEventListener('click', () => {
        const isSignin = document.getElementById('auth-modal-title').textContent === 'Sign In';
        _setAuthMode(isSignin ? 'register' : 'signin');
    });

    document.getElementById('auth-password-form').addEventListener('submit', _handlePasswordSubmit);
}

function _setAuthMode(mode) {
    const isRegister = mode === 'register';
    document.getElementById('auth-modal-title').textContent = isRegister ? 'Create Account' : 'Sign In';
    document.getElementById('auth-submit-btn').textContent = isRegister ? 'Create Account' : 'Sign In';
    document.getElementById('auth-toggle-text').textContent = isRegister ? 'Already have an account?' : "Don't have an account?";
    document.getElementById('auth-mode-toggle').textContent = isRegister ? 'Sign in' : 'Create account';

    const confirmField = document.getElementById('auth-confirm-password');
    if (isRegister) {
        confirmField.classList.remove('hidden');
        confirmField.required = true;
    } else {
        confirmField.classList.add('hidden');
        confirmField.required = false;
    }

    document.getElementById('auth-error').classList.add('hidden');
}

async function _handlePasswordSubmit(e) {
    e.preventDefault();

    const isRegister = document.getElementById('auth-modal-title').textContent === 'Create Account';
    const email = document.getElementById('auth-email').value.trim();
    const password = document.getElementById('auth-password').value;
    const errorEl = document.getElementById('auth-error');
    const submitBtn = document.getElementById('auth-submit-btn');

    if (isRegister) {
        const confirm = document.getElementById('auth-confirm-password').value;
        if (password !== confirm) {
            errorEl.textContent = 'Passwords do not match.';
            errorEl.classList.remove('hidden');
            return;
        }
    }

    submitBtn.disabled = true;
    submitBtn.textContent = '...';
    errorEl.classList.add('hidden');

    const endpoint = isRegister ? '/auth/register' : '/auth/login/password';

    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ email, password }),
        });

        if (response.ok) {
            document.getElementById('auth-modal').classList.add('hidden');
            await updateAuthUI();
            window.location.href = '/dashboard.html';
        } else {
            const data = await response.json();
            errorEl.textContent = data.detail || 'Authentication failed.';
            errorEl.classList.remove('hidden');
        }
    } catch {
        errorEl.textContent = 'Could not reach the server.';
        errorEl.classList.remove('hidden');
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = isRegister ? 'Create Account' : 'Sign In';
    }
}

// Initialize auth on page load
document.addEventListener('DOMContentLoaded', () => {
    saveTokenFromURL();
    updateAuthUI();
});
