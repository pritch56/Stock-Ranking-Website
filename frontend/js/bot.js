// Bot Profile JavaScript

const API_BASE_URL = (() => {
    const { protocol, hostname } = window.location;
    const port = hostname === 'localhost' ? ':8000' : '';
    return `${protocol}//${hostname}${port}/api`;
})();

let currentPeriod = 'month';
let botId = null;

// Initialize page
document.addEventListener('DOMContentLoaded', () => {
    // Get bot ID from URL
    const urlParams = new URLSearchParams(window.location.search);
    botId = urlParams.get('id');
    
    if (!botId) {
        alert('No bot ID provided');
        window.location.href = 'dashboard.html';
        return;
    }
    
    loadBotProfile();
    setupPeriodFilters();
});

// Setup period filters
function setupPeriodFilters() {
    document.querySelectorAll('.period-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.period-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            currentPeriod = btn.dataset.period;
            loadPerformanceData();
        });
    });
}

// Load bot profile
async function loadBotProfile() {
    try {
        // Load bot details
        const botResponse = await fetch(`${API_BASE_URL}/bots/${botId}`);
        const bot = await botResponse.json();
        
        displayBotHeader(bot);
        loadPerformanceData();
        loadTradeHistory();
        loadPositions();
        loadRankings();
    } catch (error) {
        console.error('Error loading bot profile:', error);
        loadMockData();
    }
}

// Display bot header
function displayBotHeader(bot) {
    document.getElementById('bot-name').textContent = bot.name;
    document.getElementById('bot-strategy').textContent = bot.strategy_type;
    document.getElementById('bot-description').textContent = bot.description || 'No description provided.';
    
    const statusIndicator = document.getElementById('bot-status-indicator');
    const statusText = document.getElementById('bot-status-text');
    
    if (bot.is_active) {
        statusIndicator.className = 'w-2 h-2 rounded-full bg-green-500 animate-pulse';
        statusText.textContent = 'Active';
        statusText.className = 'text-sm text-green-400';
    } else {
        statusIndicator.className = 'w-2 h-2 rounded-full bg-gray-500';
        statusText.textContent = 'Inactive';
        statusText.className = 'text-sm text-gray-400';
    }
}

// Load performance data
async function loadPerformanceData() {
    try {
        const response = await fetch(`${API_BASE_URL}/bots/${botId}/performance?period=${currentPeriod}`);
        const performance = await response.json();
        
        displayPerformanceMetrics(performance);
        updateEquityChart(performance);
        updateReturnsChart(performance);
    } catch (error) {
        console.error('Error loading performance:', error);
        displayMockPerformance();
    }
}

// Display performance metrics
function displayPerformanceMetrics(performance) {
    document.getElementById('metric-return').textContent = formatPercent(performance.total_return);
    document.getElementById('metric-return').className = `text-3xl font-bold mono ${
        performance.total_return >= 0 ? 'text-green-400' : 'text-red-400'
    }`;
    
    document.getElementById('metric-sharpe').textContent = performance.sharpe_ratio.toFixed(2);
    document.getElementById('metric-drawdown').textContent = formatPercent(Math.abs(performance.max_drawdown));
    document.getElementById('metric-winrate').textContent = formatPercent(performance.win_rate);
    document.getElementById('metric-trades').textContent = performance.total_trades.toLocaleString();
}

// Update equity curve chart
function updateEquityChart(performance) {
    const ctx = document.getElementById('equity-chart');
    
    // Generate mock equity data
    const days = currentPeriod === 'week' ? 7 : currentPeriod === 'month' ? 30 : currentPeriod === 'year' ? 365 : 1825;
    const equityData = generateEquityCurve(100000, performance.total_return, days);
    
    if (window.equityChart) {
        window.equityChart.destroy();
    }
    
    window.equityChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: equityData.map((_, i) => i),
            datasets: [{
                label: 'Equity',
                data: equityData,
                borderColor: performance.total_return >= 0 ? '#22C55E' : '#EF4444',
                backgroundColor: performance.total_return >= 0 
                    ? 'rgba(34, 197, 94, 0.1)' 
                    : 'rgba(239, 68, 68, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4,
                pointRadius: 0,
                pointHoverRadius: 6,
                pointHoverBackgroundColor: performance.total_return >= 0 ? '#22C55E' : '#EF4444',
                pointHoverBorderColor: '#fff',
                pointHoverBorderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                intersect: false,
                mode: 'index'
            },
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
                            return `Equity: ${formatCurrency(context.parsed.y)}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    display: false
                },
                y: {
                    ticks: {
                        color: '#9CA3AF',
                        font: {
                            family: 'JetBrains Mono'
                        },
                        callback: function(value) {
                            return formatCurrency(value);
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

// Update returns distribution chart
function updateReturnsChart(performance) {
    const ctx = document.getElementById('returns-chart');
    
    // Generate mock returns distribution
    const returns = generateReturnsDistribution(performance.win_rate);
    
    if (window.returnsChart) {
        window.returnsChart.destroy();
    }
    
    window.returnsChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['-5%', '-4%', '-3%', '-2%', '-1%', '0%', '1%', '2%', '3%', '4%', '5%'],
            datasets: [{
                label: 'Frequency',
                data: returns,
                backgroundColor: returns.map((_, i) => 
                    i < 5 ? 'rgba(239, 68, 68, 0.7)' : 'rgba(34, 197, 94, 0.7)'
                ),
                borderColor: returns.map((_, i) => 
                    i < 5 ? '#EF4444' : '#22C55E'
                ),
                borderWidth: 2,
                borderRadius: 6
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
                    padding: 12
                }
            },
            scales: {
                x: {
                    ticks: {
                        color: '#9CA3AF',
                        font: {
                            family: 'JetBrains Mono'
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
                            family: 'Inter'
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

// Load trade history
async function loadTradeHistory() {
    try {
        const response = await fetch(`${API_BASE_URL}/bots/${botId}/trades?limit=50`);
        const data = await response.json();
        
        displayTradeHistory(data.trades);
    } catch (error) {
        console.error('Error loading trades:', error);
        displayMockTrades();
    }
}

// Display trade history
function displayTradeHistory(trades) {
    const tbody = document.getElementById('trade-history');
    tbody.innerHTML = '';
    
    trades.forEach((trade, index) => {
        const row = document.createElement('tr');
        row.style.animationDelay = `${index * 0.02}s`;
        row.className = 'animate-fade-in-up';
        
        const pl = Math.random() * 1000 - 300; // Mock P/L
        
        row.innerHTML = `
            <td class="py-3 px-6 text-sm text-gray-400">
                ${formatTime(trade.timestamp)}
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
                ${trade.quantity.toFixed(2)}
            </td>
            <td class="py-3 px-6 text-right mono font-semibold">
                ${formatCurrency(trade.value)}
            </td>
            <td class="py-3 px-6 text-right mono font-semibold ${pl >= 0 ? 'text-green-400' : 'text-red-400'}">
                ${pl >= 0 ? '+' : ''}${formatCurrency(pl)}
            </td>
        `;
        
        tbody.appendChild(row);
    });
}

// Load positions
async function loadPositions() {
    try {
        const response = await fetch(`${API_BASE_URL}/bots/${botId}/positions`);
        const data = await response.json();
        
        displayPositions(data.positions);
    } catch (error) {
        console.error('Error loading positions:', error);
        displayMockPositions();
    }
}

// Display positions
function displayPositions(positions) {
    const grid = document.getElementById('positions-grid');
    const noPositions = document.getElementById('no-positions');
    
    if (!positions || Object.keys(positions).length === 0) {
        grid.classList.add('hidden');
        noPositions.classList.remove('hidden');
        return;
    }
    
    grid.classList.remove('hidden');
    noPositions.classList.add('hidden');
    grid.innerHTML = '';
    
    Object.entries(positions).forEach(([ticker, position]) => {
        const positionCard = document.createElement('div');
        positionCard.className = 'bg-gray-900 p-4 rounded-lg border border-gray-700';
        
        const currentValue = position.quantity * position.avg_price * (1 + Math.random() * 0.1 - 0.05);
        const pl = currentValue - position.total_cost;
        const plPct = pl / position.total_cost;
        
        positionCard.innerHTML = `
            <div class="flex justify-between items-start mb-3">
                <h4 class="text-lg font-bold mono">${ticker}</h4>
                <span class="text-xs px-2 py-1 bg-blue-500 bg-opacity-20 text-blue-400 rounded">
                    ${position.quantity > 0 ? 'LONG' : 'SHORT'}
                </span>
            </div>
            <div class="space-y-2 text-sm">
                <div class="flex justify-between">
                    <span class="text-gray-400">Quantity</span>
                    <span class="mono font-semibold">${position.quantity.toFixed(2)}</span>
                </div>
                <div class="flex justify-between">
                    <span class="text-gray-400">Avg Price</span>
                    <span class="mono font-semibold">${formatCurrency(position.avg_price)}</span>
                </div>
                <div class="flex justify-between pt-2 border-t border-gray-700">
                    <span class="text-gray-400">P/L</span>
                    <span class="mono font-semibold ${pl >= 0 ? 'text-green-400' : 'text-red-400'}">
                        ${pl >= 0 ? '+' : ''}${formatCurrency(pl)} (${formatPercent(plPct)})
                    </span>
                </div>
            </div>
        `;
        
        grid.appendChild(positionCard);
    });
}

// Load rankings
async function loadRankings() {
    try {
        const response = await fetch(`${API_BASE_URL}/leaderboard/bot/${botId}?period=${currentPeriod}`);
        const data = await response.json();
        
        displayRankings(data.rankings);
    } catch (error) {
        console.error('Error loading rankings:', error);
        displayMockRankings();
    }
}

// Display rankings
function displayRankings(rankings) {
    const grid = document.getElementById('rankings-grid');
    grid.innerHTML = '';
    
    const mockRankings = [
        { league: 'Global', rank: 15 },
        { league: 'ML League', rank: 7 },
        { league: 'Technical', rank: 23 }
    ];
    
    (rankings.length > 0 ? rankings : mockRankings).forEach(ranking => {
        const rankCard = document.createElement('div');
        rankCard.className = 'bg-gray-800 p-4 rounded-lg border border-gray-700 text-center';
        
        rankCard.innerHTML = `
            <p class="text-sm text-gray-400 mb-2">${ranking.league}</p>
            <p class="text-2xl font-bold mono text-blue-400">#${ranking.rank}</p>
        `;
        
        grid.appendChild(rankCard);
    });
}

// Generate mock equity curve
function generateEquityCurve(initial, totalReturn, days) {
    const data = [initial];
    let currentValue = initial;
    const dailyReturn = Math.pow(1 + totalReturn, 1 / days);
    
    for (let i = 1; i < days; i++) {
        const randomness = 1 + (Math.random() - 0.5) * 0.02;
        currentValue = currentValue * dailyReturn * randomness;
        data.push(currentValue);
    }
    
    return data;
}

// Generate returns distribution
function generateReturnsDistribution(winRate) {
    const data = [];
    for (let i = 0; i < 11; i++) {
        if (i < 5) {
            data.push(Math.random() * (1 - winRate) * 100);
        } else {
            data.push(Math.random() * winRate * 100);
        }
    }
    return data;
}

// Load mock data
function loadMockData() {
    const mockBot = {
        name: 'Demo Trading Bot',
        strategy_type: 'ML',
        description: 'A machine learning based trading bot using advanced algorithms.',
        is_active: true
    };
    
    displayBotHeader(mockBot);
    displayMockPerformance();
    displayMockTrades();
    displayMockPositions();
    displayMockRankings();
}

function displayMockPerformance() {
    const mockPerformance = {
        total_return: 0.247,
        sharpe_ratio: 2.34,
        max_drawdown: -0.08,
        win_rate: 0.64,
        total_trades: 1247
    };
    
    displayPerformanceMetrics(mockPerformance);
    updateEquityChart(mockPerformance);
    updateReturnsChart(mockPerformance);
}

function displayMockTrades() {
    const mockTrades = Array.from({ length: 20 }, (_, i) => ({
        timestamp: new Date(Date.now() - i * 7200000).toISOString(),
        ticker: ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN'][i % 5],
        action: i % 2 === 0 ? 'BUY' : 'SELL',
        price: Math.random() * 500 + 100,
        quantity: Math.floor(Math.random() * 50) + 1,
        value: 0
    }));
    
    mockTrades.forEach(t => t.value = t.price * t.quantity);
    displayTradeHistory(mockTrades);
}

function displayMockPositions() {
    const mockPositions = {
        'AAPL': { quantity: 10, avg_price: 175.5, total_cost: 1755 },
        'GOOGL': { quantity: 5, avg_price: 140.2, total_cost: 701 },
        'BTC': { quantity: 0.5, avg_price: 45000, total_cost: 22500 }
    };
    
    displayPositions(mockPositions);
}

function displayMockRankings() {
    displayRankings([]);
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
    return date.toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}
