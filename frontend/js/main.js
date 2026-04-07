// Main JavaScript for index.html

const API_BASE_URL = (() => {
    const { protocol, hostname } = window.location;
    const port = hostname === 'localhost' ? ':8000' : '';
    return `${protocol}//${hostname}${port}/api`;
})();

let liveTradesInterval = null;

// Populate leaderboard preview
async function loadLeaderboardPreview() {
    try {
        const response = await fetch(`${API_BASE_URL}/leaderboard?period=month&limit=5`);
        const data = await response.json();
        
        const tbody = document.getElementById('preview-leaderboard');
        tbody.innerHTML = '';
        
        data.leaderboard.forEach((bot, index) => {
            const row = document.createElement('tr');
            row.className = 'animate-fade-in-up';
            row.style.animationDelay = `${index * 0.1}s`;
            
            const rankClass = index === 0 ? 'gold' : index === 1 ? 'silver' : index === 2 ? 'bronze' : 'default';
            
            row.innerHTML = `
                <td class="py-4 px-4">
                    <div class="rank-badge ${rankClass}">${bot.rank}</div>
                </td>
                <td class="py-4 px-4 font-semibold">${bot.bot_name}</td>
                <td class="py-4 px-4">
                    <span class="px-3 py-1 bg-blue-500 bg-opacity-20 text-blue-400 rounded-full text-sm">
                        ${bot.strategy}
                    </span>
                </td>
                <td class="py-4 px-4 text-right mono ${bot.return >= 0 ? 'text-green-400' : 'text-red-400'}">
                    ${formatPercent(bot.return)}
                </td>
                <td class="py-4 px-4 text-right mono">${bot.sharpe_ratio.toFixed(2)}</td>
                <td class="py-4 px-4 text-right mono">${bot.total_trades}</td>
            `;
            
            tbody.appendChild(row);
        });
    } catch (error) {
        console.error('Error loading leaderboard:', error);
        loadMockLeaderboard();
    }
}

// Load mock data if API is not available
function loadMockLeaderboard() {
    const mockData = [
        { rank: 1, bot_name: 'AlphaBot Pro', strategy: 'ML', return: 0.247, sharpe_ratio: 2.34, total_trades: 1247 },
        { rank: 2, bot_name: 'Lightning Trader', strategy: 'HFT', return: 0.189, sharpe_ratio: 1.98, total_trades: 5892 },
        { rank: 3, bot_name: 'Sentiment King', strategy: 'Sentiment', return: 0.156, sharpe_ratio: 1.76, total_trades: 892 },
        { rank: 4, bot_name: 'TechBot X', strategy: 'Technical', return: 0.134, sharpe_ratio: 1.54, total_trades: 674 },
        { rank: 5, bot_name: 'ArbitrageX', strategy: 'Arbitrage', return: 0.112, sharpe_ratio: 1.43, total_trades: 2341 }
    ];
    
    const tbody = document.getElementById('preview-leaderboard');
    tbody.innerHTML = '';
    
    mockData.forEach((bot, index) => {
        const row = document.createElement('tr');
        row.className = 'animate-fade-in-up';
        row.style.animationDelay = `${index * 0.1}s`;
        
        const rankClass = index === 0 ? 'gold' : index === 1 ? 'silver' : index === 2 ? 'bronze' : 'default';
        
        row.innerHTML = `
            <td class="py-4 px-4">
                <div class="rank-badge ${rankClass}">${bot.rank}</div>
            </td>
            <td class="py-4 px-4 font-semibold">${bot.bot_name}</td>
            <td class="py-4 px-4">
                <span class="px-3 py-1 bg-blue-500 bg-opacity-20 text-blue-400 rounded-full text-sm">
                    ${bot.strategy}
                </span>
            </td>
            <td class="py-4 px-4 text-right mono text-green-400">
                ${formatPercent(bot.return)}
            </td>
            <td class="py-4 px-4 text-right mono">${bot.sharpe_ratio.toFixed(2)}</td>
            <td class="py-4 px-4 text-right mono">${bot.total_trades}</td>
        `;
        
        tbody.appendChild(row);
    });
}

// Populate live trades feed
async function loadLiveTrades() {
    const container = document.getElementById('live-trades');

    try {
        const response = await fetch(`${API_BASE_URL}/trades/live?limit=8`);
        if (!response.ok) throw new Error('fetch failed');
        const data = await response.json();
        container.innerHTML = '';
        data.trades.forEach((trade, index) => {
            container.appendChild(buildTradeEl(trade, index * 0.05));
        });
    } catch {
        container.innerHTML = '<p class="text-gray-500 text-sm px-4">No recent trades.</p>';
    }

    connectLiveFeedSocket(container);
}

function connectLiveFeedSocket(container) {
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsPort = window.location.hostname === 'localhost' ? ':8000' : '';
    const ws = new WebSocket(`${wsProtocol}//${window.location.hostname}${wsPort}/ws`);

    ws.onmessage = (event) => {
        const msg = JSON.parse(event.data);
        if (msg.type !== 'trade') return;
        container.insertBefore(buildTradeEl(msg.data, 0), container.firstChild);
        while (container.children.length > 10) {
            container.removeChild(container.lastChild);
        }
    };

    ws.onclose = () => setTimeout(() => connectLiveFeedSocket(container), 5000);
}

function buildTradeEl(trade, delay = 0) {
    const isBuy = trade.action === 'BUY';
    const value = trade.value != null ? formatCurrency(trade.value) : '';
    const el = document.createElement('div');
    el.className = `trade-item ${isBuy ? 'buy' : 'sell'}`;
    el.style.animationDelay = `${delay}s`;
    el.innerHTML = `
        <div class="flex items-center justify-between">
            <div class="flex items-center gap-3">
                <span class="font-semibold text-sm">${trade.bot_name}</span>
                <span class="px-2 py-1 rounded text-xs font-bold ${
                    isBuy ? 'bg-green-500 bg-opacity-20 text-green-400' : 'bg-red-500 bg-opacity-20 text-red-400'
                }">${trade.action}</span>
                <span class="mono text-sm text-gray-400">${trade.ticker}</span>
            </div>
            <span class="mono text-sm font-semibold text-gray-300">${value}</span>
        </div>
    `;
    return el;
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

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    loadLeaderboardPreview();
    loadLiveTrades();
});
