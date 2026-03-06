// Dashboard JavaScript

const API_BASE_URL = 'http://localhost:8000/api';

// Mock user ID (in production, get from auth)
const USER_ID = 'user-123';

// Initialize page
document.addEventListener('DOMContentLoaded', () => {
    loadDashboard();
    setupCreateBotForm();
});

// Load dashboard data
async function loadDashboard() {
    try {
        // Load user's bots
        const response = await fetch(`${API_BASE_URL}/users/${USER_ID}/bots`);
        const data = await response.json();
        
        if (data.bots.length === 0) {
            showEmptyBots();
        } else {
            displayBots(data.bots);
            updateStats(data.bots);
            loadRecentTrades(data.bots);
            displayApiKeys(data.bots);
        }
    } catch (error) {
        console.error('Error loading dashboard:', error);
        loadMockData();
    }
}

// Display bots
function displayBots(bots) {
    const grid = document.getElementById('bots-grid');
    const emptyState = document.getElementById('empty-bots');
    
    grid.classList.remove('hidden');
    emptyState.classList.add('hidden');
    
    grid.innerHTML = '';
    
    bots.forEach((bot, index) => {
        const botCard = document.createElement('div');
        botCard.className = 'bot-card';
        botCard.style.animationDelay = `${index * 0.1}s`;
        
        const returnPct = (bot.current_capital - 100000) / 100000;
        
        botCard.innerHTML = `
            <div class="flex items-start justify-between mb-4">
                <div>
                    <h3 class="text-xl font-bold mb-1">${bot.name}</h3>
                    <p class="text-sm text-gray-400">${bot.strategy_type}</p>
                </div>
                <div class="flex items-center gap-2">
                    <div class="w-2 h-2 rounded-full ${bot.is_active ? 'bg-green-500' : 'bg-gray-500'}"></div>
                    <span class="text-xs ${bot.is_active ? 'text-green-400' : 'text-gray-400'}">
                        ${bot.is_active ? 'Active' : 'Inactive'}
                    </span>
                </div>
            </div>
            
            <div class="space-y-3 mb-4">
                <div class="flex justify-between">
                    <span class="text-sm text-gray-400">Return</span>
                    <span class="mono font-bold ${returnPct >= 0 ? 'text-green-400' : 'text-red-400'}">
                        ${formatPercent(returnPct)}
                    </span>
                </div>
                <div class="flex justify-between">
                    <span class="text-sm text-gray-400">Capital</span>
                    <span class="mono font-semibold">${formatCurrency(bot.current_capital)}</span>
                </div>
            </div>
            
            <div class="flex gap-2 pt-4 border-t border-gray-700">
                <button onclick="viewBot('${bot.bot_id}')" class="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-sm font-semibold transition">
                    View
                </button>
                <button onclick="toggleBot('${bot.bot_id}', ${bot.is_active})" class="flex-1 px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg text-sm font-semibold transition">
                    ${bot.is_active ? 'Pause' : 'Activate'}
                </button>
            </div>
        `;
        
        grid.appendChild(botCard);
    });
}

// Update statistics
function updateStats(bots) {
    const totalBots = bots.length;
    const avgReturn = bots.reduce((sum, bot) => {
        return sum + ((bot.current_capital - 100000) / 100000);
    }, 0) / bots.length;
    
    const totalTrades = Math.floor(Math.random() * 10000); // Mock data
    const bestRank = Math.floor(Math.random() * 100) + 1; // Mock data
    
    document.getElementById('total-bots').textContent = totalBots;
    document.getElementById('avg-return').textContent = formatPercent(avgReturn);
    document.getElementById('avg-return').className = `text-3xl font-bold mono ${avgReturn >= 0 ? 'text-green-400' : 'text-red-400'}`;
    document.getElementById('total-trades').textContent = totalTrades.toLocaleString();
    document.getElementById('best-rank').textContent = `#${bestRank}`;
}

// Load recent trades
async function loadRecentTrades(bots) {
    const tbody = document.getElementById('recent-trades');
    
    // Mock trades data
    const mockTrades = Array.from({ length: 10 }, (_, i) => ({
        time: new Date(Date.now() - i * 3600000).toISOString(),
        bot: bots[Math.floor(Math.random() * bots.length)],
        ticker: ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN', 'BTC', 'ETH'][Math.floor(Math.random() * 7)],
        action: Math.random() > 0.5 ? 'BUY' : 'SELL',
        price: Math.random() * 1000 + 100,
        quantity: Math.floor(Math.random() * 100) + 1
    }));
    
    tbody.innerHTML = '';
    
    mockTrades.forEach((trade, index) => {
        const row = document.createElement('tr');
        row.style.animationDelay = `${index * 0.05}s`;
        row.className = 'animate-fade-in-up';
        
        const value = trade.price * trade.quantity;
        
        row.innerHTML = `
            <td class="py-3 px-6 text-sm text-gray-400">
                ${formatTime(trade.time)}
            </td>
            <td class="py-3 px-6 text-sm font-semibold">
                ${trade.bot.name}
            </td>
            <td class="py-3 px-6 mono font-semibold">
                ${trade.ticker}
            </td>
            <td class="py-3 px-6">
                <span class="px-2 py-1 rounded text-xs font-bold ${
                    trade.action === 'BUY' ? 'bg-green-500 bg-opacity-20 text-green-400' : 'bg-red-500 bg-opacity-20 text-red-400'
                }">
                    ${trade.action}
                </span>
            </td>
            <td class="py-3 px-6 text-right mono">
                ${formatCurrency(trade.price)}
            </td>
            <td class="py-3 px-6 text-right mono">
                ${trade.quantity}
            </td>
            <td class="py-3 px-6 text-right mono font-semibold">
                ${formatCurrency(value)}
            </td>
        `;
        
        tbody.appendChild(row);
    });
}

// Display API keys
function displayApiKeys(bots) {
    const container = document.getElementById('api-keys-list');
    container.innerHTML = '';
    
    bots.forEach(bot => {
        const keyItem = document.createElement('div');
        keyItem.className = 'flex items-center justify-between p-4 bg-gray-900 rounded-lg border border-gray-700';
        
        keyItem.innerHTML = `
            <div>
                <p class="font-semibold mb-1">${bot.name}</p>
                <code class="mono text-sm text-gray-400">${bot.api_key ? bot.api_key.substring(0, 20) + '...' : 'Loading...'}</code>
            </div>
            <button onclick="copyApiKey('${bot.api_key}')" class="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg text-sm font-semibold transition">
                Copy
            </button>
        `;
        
        container.appendChild(keyItem);
    });
}

// Setup create bot form
function setupCreateBotForm() {
    const form = document.getElementById('create-bot-form');
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const botData = {
            user_id: USER_ID,
            name: document.getElementById('bot-name').value,
            strategy_type: document.getElementById('strategy-type').value,
            description: document.getElementById('bot-description').value,
            initial_capital: parseFloat(document.getElementById('initial-capital').value)
        };
        
        try {
            const response = await fetch(`${API_BASE_URL}/bots`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(botData)
            });
            
            if (response.ok) {
                const newBot = await response.json();
                alert(`Bot created successfully! API Key: ${newBot.api_key}`);
                hideCreateBotModal();
                loadDashboard();
            } else {
                alert('Failed to create bot');
            }
        } catch (error) {
            console.error('Error creating bot:', error);
            alert('Error creating bot. Using mock data for demo.');
            hideCreateBotModal();
        }
    });
}

// Modal functions
function showCreateBotModal() {
    document.getElementById('create-bot-modal').classList.remove('hidden');
}

function hideCreateBotModal() {
    document.getElementById('create-bot-modal').classList.add('hidden');
    document.getElementById('create-bot-form').reset();
}

// Bot actions
function viewBot(botId) {
    window.location.href = `bot.html?id=${botId}`;
}

async function toggleBot(botId, isActive) {
    const endpoint = isActive ? 'deactivate' : 'activate';
    
    try {
        const response = await fetch(`${API_BASE_URL}/bots/${botId}/${endpoint}`, {
            method: 'PATCH'
        });
        
        if (response.ok) {
            loadDashboard();
        }
    } catch (error) {
        console.error('Error toggling bot:', error);
    }
}

function copyApiKey(apiKey) {
    navigator.clipboard.writeText(apiKey);
    alert('API key copied to clipboard!');
}

// Show empty state
function showEmptyBots() {
    document.getElementById('bots-grid').classList.add('hidden');
    document.getElementById('empty-bots').classList.remove('hidden');
}

// Load mock data
function loadMockData() {
    const mockBots = [
        {
            bot_id: 'bot-1',
            name: 'AlphaBot Pro',
            strategy_type: 'ML',
            is_active: true,
            current_capital: 124500,
            api_key: 'abc123def456ghi789jkl012mno345pqr678'
        },
        {
            bot_id: 'bot-2',
            name: 'Lightning Trader',
            strategy_type: 'HFT',
            is_active: true,
            current_capital: 118900,
            api_key: 'xyz987wvu654tsr321qpo098nml765kji432'
        },
        {
            bot_id: 'bot-3',
            name: 'Sentiment King',
            strategy_type: 'Sentiment',
            is_active: false,
            current_capital: 95600,
            api_key: 'fed321dcb098aze876yvu543wts210rqp109'
        }
    ];
    
    displayBots(mockBots);
    updateStats(mockBots);
    loadRecentTrades(mockBots);
    displayApiKeys(mockBots);
}

// Helper functions
function formatPercent(value) {
    const percent = (value * 100).toFixed(2);
    return `${value >= 0 ? '+' : ''}${percent}%`;
}

function formatCurrency(value) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(value);
}

function formatTime(isoString) {
    const date = new Date(isoString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    
    if (diffMins < 60) {
        return `${diffMins}m ago`;
    } else if (diffHours < 24) {
        return `${diffHours}h ago`;
    } else {
        return date.toLocaleDateString();
    }
}
