// Leaderboard JavaScript

const API_BASE_URL = 'http://localhost:8000/api';

let currentPeriod = 'month';
let currentLeague = 'global';
let ws = null;

// Initialize page
document.addEventListener('DOMContentLoaded', () => {
    setupFilters();
    loadLeaderboard();
    connectWebSocket();
});

// Setup filter buttons
function setupFilters() {
    // League filters
    document.querySelectorAll('[data-league]').forEach(btn => {
        btn.addEventListener('click', () => {
            // Update active state
            document.querySelectorAll('[data-league]').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            currentLeague = btn.dataset.league;
            loadLeaderboard();
        });
    });
    
    // Period filters
    document.querySelectorAll('[data-period]').forEach(btn => {
        btn.addEventListener('click', () => {
            // Update active state
            document.querySelectorAll('[data-period]').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            currentPeriod = btn.dataset.period;
            loadLeaderboard();
        });
    });
}

// Load leaderboard data
async function loadLeaderboard() {
    showLoading();
    
    try {
        const response = await fetch(
            `${API_BASE_URL}/leaderboard?period=${currentPeriod}&league=${currentLeague}&limit=100`
        );
        const data = await response.json();
        
        if (data.leaderboard.length === 0) {
            showEmptyState();
        } else {
            displayLeaderboard(data.leaderboard);
            updateChart(data.leaderboard.slice(0, 10));
        }
    } catch (error) {
        console.error('Error loading leaderboard:', error);
        // Load mock data
        loadMockData();
    }
}

// Display leaderboard table
function displayLeaderboard(bots) {
    const tbody = document.getElementById('leaderboard-table');
    const loading = document.getElementById('loading');
    const emptyState = document.getElementById('empty-state');
    
    loading.classList.add('hidden');
    emptyState.classList.add('hidden');
    
    tbody.innerHTML = '';
    
    bots.forEach((bot, index) => {
        const row = document.createElement('tr');
        row.className = 'animate-fade-in-up cursor-pointer';
        row.style.animationDelay = `${index * 0.02}s`;
        row.onclick = () => window.location.href = `bot.html?id=${bot.bot_id}`;
        
        const rankClass = bot.rank === 1 ? 'gold' : bot.rank === 2 ? 'silver' : bot.rank === 3 ? 'bronze' : 'default';
        
        row.innerHTML = `
            <td class="py-4 px-6">
                <div class="rank-badge ${rankClass}">${bot.rank}</div>
            </td>
            <td class="py-4 px-6">
                <div class="font-semibold text-white">${bot.bot_name}</div>
                <div class="text-xs text-gray-500 mono">ID: ${bot.bot_id.substring(0, 8)}</div>
            </td>
            <td class="py-4 px-6">
                <span class="px-3 py-1 bg-blue-500 bg-opacity-20 text-blue-400 rounded-full text-sm font-semibold">
                    ${bot.strategy}
                </span>
            </td>
            <td class="py-4 px-6 text-right mono font-bold text-lg ${bot.return >= 0 ? 'text-green-400' : 'text-red-400'}">
                ${formatPercent(bot.return)}
            </td>
            <td class="py-4 px-6 text-right mono">
                ${bot.sharpe_ratio.toFixed(2)}
            </td>
            <td class="py-4 px-6 text-right mono text-red-400">
                ${formatPercent(bot.max_drawdown)}
            </td>
            <td class="py-4 px-6 text-right mono">
                ${formatPercent(bot.win_rate)}
            </td>
            <td class="py-4 px-6 text-right mono text-gray-400">
                ${bot.total_trades.toLocaleString()}
            </td>
        `;
        
        tbody.appendChild(row);
    });
}

// Update performance chart
function updateChart(topBots) {
    const ctx = document.getElementById('performance-chart');
    
    // Destroy existing chart if any
    if (window.leaderboardChart) {
        window.leaderboardChart.destroy();
    }
    
    window.leaderboardChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: topBots.map(bot => bot.bot_name),
            datasets: [{
                label: 'Return (%)',
                data: topBots.map(bot => bot.return * 100),
                backgroundColor: topBots.map(bot => 
                    bot.return >= 0 ? 'rgba(34, 197, 94, 0.7)' : 'rgba(239, 68, 68, 0.7)'
                ),
                borderColor: topBots.map(bot => 
                    bot.return >= 0 ? 'rgba(34, 197, 94, 1)' : 'rgba(239, 68, 68, 1)'
                ),
                borderWidth: 2,
                borderRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(17, 24, 39, 0.95)',
                    titleColor: '#E5E7EB',
                    bodyColor: '#E5E7EB',
                    borderColor: '#374151',
                    borderWidth: 1,
                    padding: 12,
                    displayColors: false,
                    callbacks: {
                        label: function(context) {
                            return `Return: ${context.parsed.y.toFixed(2)}%`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    ticks: {
                        color: '#9CA3AF',
                        font: {
                            family: 'Inter'
                        }
                    },
                    grid: {
                        color: 'rgba(75, 85, 99, 0.2)'
                    }
                },
                y: {
                    ticks: {
                        color: '#9CA3AF',
                        font: {
                            family: 'JetBrains Mono'
                        },
                        callback: function(value) {
                            return value + '%';
                        }
                    },
                    grid: {
                        color: 'rgba(75, 85, 99, 0.2)'
                    }
                }
            }
        }
    });
}

// Connect to WebSocket for live updates
function connectWebSocket() {
    try {
        ws = new WebSocket('ws://localhost:8000/ws');
        
        ws.onopen = () => {
            console.log('WebSocket connected');
        };
        
        ws.onmessage = (event) => {
            const message = JSON.parse(event.data);
            
            if (message.type === 'leaderboard') {
                // Reload leaderboard on update
                loadLeaderboard();
            }
        };
        
        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };
        
        ws.onclose = () => {
            console.log('WebSocket closed, reconnecting...');
            setTimeout(connectWebSocket, 5000);
        };
    } catch (error) {
        console.error('Failed to connect WebSocket:', error);
    }
}

// Show loading state
function showLoading() {
    document.getElementById('loading').classList.remove('hidden');
    document.getElementById('empty-state').classList.add('hidden');
}

// Show empty state
function showEmptyState() {
    document.getElementById('loading').classList.add('hidden');
    document.getElementById('empty-state').classList.remove('hidden');
}

// Load mock data
function loadMockData() {
    const mockBots = Array.from({ length: 20 }, (_, i) => ({
        rank: i + 1,
        bot_id: `bot-${i + 1}`,
        bot_name: `Trading Bot ${i + 1}`,
        strategy: ['ML', 'HFT', 'Sentiment', 'Technical', 'Arbitrage'][i % 5],
        return: (Math.random() * 0.5 - 0.1),
        sharpe_ratio: Math.random() * 3,
        max_drawdown: -(Math.random() * 0.3),
        win_rate: 0.3 + Math.random() * 0.4,
        total_trades: Math.floor(Math.random() * 5000) + 100
    }))
    .sort((a, b) => b.return - a.return)
    .map((bot, i) => ({ ...bot, rank: i + 1 }));
    
    displayLeaderboard(mockBots);
    updateChart(mockBots.slice(0, 10));
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
