// Main JavaScript for index.html

const API_BASE_URL = 'http://localhost:8000/api';

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
function loadLiveTrades() {
    const tradesContainer = document.getElementById('live-trades');
    
    // Mock trade data
    const mockTrades = [
        { bot: 'AlphaBot Pro', action: 'BUY', ticker: 'BTC', change: '+0.4%' },
        { bot: 'Lightning Trader', action: 'SELL', ticker: 'AAPL', change: '-0.2%' },
        { bot: 'Sentiment King', action: 'BUY', ticker: 'ETH', change: '+1.1%' },
        { bot: 'TechBot X', action: 'BUY', ticker: 'TSLA', change: '+0.7%' },
        { bot: 'ArbitrageX', action: 'SELL', ticker: 'SPY', change: '-0.3%' },
        { bot: 'DeepTrader', action: 'BUY', ticker: 'GOOGL', change: '+0.5%' },
        { bot: 'QuickBot', action: 'SELL', ticker: 'MSFT', change: '-0.1%' },
        { bot: 'SmartTrader', action: 'BUY', ticker: 'AMZN', change: '+0.8%' }
    ];
    
    mockTrades.forEach((trade, index) => {
        const tradeElement = document.createElement('div');
        tradeElement.className = `trade-item ${trade.action.toLowerCase()}`;
        tradeElement.style.animationDelay = `${index * 0.1}s`;
        
        tradeElement.innerHTML = `
            <div class="flex items-center justify-between">
                <div class="flex items-center gap-3">
                    <span class="font-semibold text-sm">${trade.bot}</span>
                    <span class="px-2 py-1 rounded text-xs font-bold ${
                        trade.action === 'BUY' ? 'bg-green-500 bg-opacity-20 text-green-400' : 'bg-red-500 bg-opacity-20 text-red-400'
                    }">${trade.action}</span>
                    <span class="mono text-sm text-gray-400">${trade.ticker}</span>
                </div>
                <span class="mono text-sm font-semibold ${
                    trade.change.startsWith('+') ? 'text-green-400' : 'text-red-400'
                }">${trade.change}</span>
            </div>
        `;
        
        tradesContainer.appendChild(tradeElement);
    });
    
    // Simulate new trades coming in
    setInterval(() => {
        const randomTrade = mockTrades[Math.floor(Math.random() * mockTrades.length)];
        const tradeElement = document.createElement('div');
        tradeElement.className = `trade-item ${randomTrade.action.toLowerCase()}`;
        
        tradeElement.innerHTML = `
            <div class="flex items-center justify-between">
                <div class="flex items-center gap-3">
                    <span class="font-semibold text-sm">${randomTrade.bot}</span>
                    <span class="px-2 py-1 rounded text-xs font-bold ${
                        randomTrade.action === 'BUY' ? 'bg-green-500 bg-opacity-20 text-green-400' : 'bg-red-500 bg-opacity-20 text-red-400'
                    }">${randomTrade.action}</span>
                    <span class="mono text-sm text-gray-400">${randomTrade.ticker}</span>
                </div>
                <span class="mono text-sm font-semibold ${
                    randomTrade.change.startsWith('+') ? 'text-green-400' : 'text-red-400'
                }">${randomTrade.change}</span>
            </div>
        `;
        
        tradesContainer.insertBefore(tradeElement, tradesContainer.firstChild);
        
        // Remove old trades to keep feed manageable
        if (tradesContainer.children.length > 10) {
            tradesContainer.removeChild(tradesContainer.lastChild);
        }
    }, 5000);
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
