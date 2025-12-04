/**
 * Portfolio Page Logic
 * Handles displaying wallet information and portfolio data
 */

// State management
let portfolioData = {
    positions: [],
    transactions: [],
    stats: {
        activePositions: 0,
        totalStaked: 0,
        totalWon: 0,
        winRate: 0
    }
};

/**
 * Initialize portfolio page
 */
function initPortfolio() {
    // Check if wallet is connected
    const walletConnected = localStorage.getItem('walletConnected');
    const walletAddress = localStorage.getItem('walletAddress');
    const isDemoMode = localStorage.getItem('demoMode') === 'true';

    if (walletConnected === 'true' && walletAddress) {
        showConnectedProfile(walletAddress, isDemoMode);
    } else {
        showNotConnectedProfile();
    }
}

/**
 * Show not connected profile
 */
function showNotConnectedProfile() {
    document.getElementById('not-connected-section').classList.add('active');
    document.getElementById('connected-section').classList.remove('active');
}

/**
 * Show connected profile
 */
async function showConnectedProfile(address, isDemoMode) {
    document.getElementById('not-connected-section').classList.remove('active');
    document.getElementById('connected-section').classList.add('active');

    // Update wallet information
    await updateWalletInfo(address, isDemoMode);

    // Load portfolio data
    await loadPortfolioData(address, isDemoMode);

    // Update statistics
    updateStatistics();

    // Load positions
    loadPositions();

    // Load transactions
    loadTransactions();
}

/**
 * Update wallet information display
 */
async function updateWalletInfo(address, isDemoMode) {
    // Update address
    const addressText = document.getElementById('address-text');
    if (addressText) {
        addressText.textContent = formatAddress(address);
        addressText.setAttribute('data-full-address', address);
    }

    // Update balance
    let balance = '0';
    if (isDemoMode) {
        balance = localStorage.getItem('demoBalance') || '10000';
    } else if (web3 && address) {
        try {
            const balanceWei = await web3.eth.getBalance(address);
            balance = web3.utils.fromWei(balanceWei, 'ether');
        } catch (error) {
            console.error('Error getting balance:', error);
        }
    }

    const profileBalance = document.getElementById('profile-balance');
    if (profileBalance) {
        profileBalance.textContent = formatBalance(balance) + ' QIE';
    }

    // Update network - force fresh detection
    const profileNetwork = document.getElementById('profile-network');
    if (profileNetwork) {
        if (isDemoMode) {
            profileNetwork.innerHTML = '<span class="badge badge-warning">Demo Mode</span>';
        } else {
            try {
                // Force re-initialize web3 to get current network
                if (typeof window.ethereum !== 'undefined') {
                    if (!web3) {
                        web3 = new Web3(window.ethereum);
                    }
                    // Get CURRENT chain ID from wallet
                    const chainId = await web3.eth.getChainId();
                    const networkName = getNetworkName(chainId);
                    console.log('Portfolio detected network:', networkName, 'Chain ID:', chainId);
                    profileNetwork.textContent = networkName;
                } else {
                    profileNetwork.textContent = 'No wallet';
                }
            } catch (error) {
                console.error('Error detecting network:', error);
                profileNetwork.textContent = 'Unknown';
            }
        }
    }

    // Update connection type
    const connectionType = document.getElementById('connection-type');
    if (connectionType) {
        const walletType = localStorage.getItem('walletType') || 'metamask';
        if (isDemoMode) {
            connectionType.textContent = 'Demo Mode';
        } else if (walletType === 'qie') {
            connectionType.textContent = 'QIE Wallet';
        } else {
            connectionType.textContent = 'MetaMask';
        }
    }

    // Update chain ID
    const chainIdElement = document.getElementById('chain-id');
    if (chainIdElement && web3 && !isDemoMode) {
        try {
            const chainId = await web3.eth.getChainId();
            chainIdElement.textContent = chainId.toString();
        } catch (error) {
            chainIdElement.textContent = '-';
        }
    } else if (isDemoMode) {
        chainIdElement.textContent = 'Demo';
    }

    // Update member since
    const memberSince = document.getElementById('member-since');
    if (memberSince) {
        const firstConnection = localStorage.getItem('firstConnection');
        if (firstConnection) {
            const date = new Date(parseInt(firstConnection));
            memberSince.textContent = date.toLocaleDateString();
        } else {
            const now = Date.now();
            localStorage.setItem('firstConnection', now.toString());
            memberSince.textContent = new Date(now).toLocaleDateString();
        }
    }

    // Update connection status badge
    const statusBadge = document.getElementById('status-badge');
    if (statusBadge) {
        if (isDemoMode) {
            statusBadge.className = 'badge badge-warning';
            statusBadge.textContent = '🎮 Demo Mode';
        } else {
            const walletType = localStorage.getItem('walletType') || 'metamask';
            if (walletType === 'qie') {
                statusBadge.className = 'badge badge-success';
                statusBadge.textContent = '✓ QIE Wallet Connected';
            } else {
                statusBadge.className = 'badge badge-success';
                statusBadge.textContent = '✓ Connected';
            }
        }
    }
}

/**
 * Load portfolio data from backend or demo data
 */
async function loadPortfolioData(address, isDemoMode) {
    if (isDemoMode) {
        // Load demo data
        portfolioData = {
            positions: generateDemoPositions(),
            transactions: generateDemoTransactions(),
            stats: {
                activePositions: 3,
                totalStaked: 1500,
                totalWon: 2250,
                winRate: 66.7
            }
        };
    } else {
        // Load real data from backend
        try {
            const response = await fetch(`/api/portfolio/${address}`);
            if (response.ok) {
                portfolioData = await response.json();
            }
        } catch (error) {
            console.error('Error loading portfolio data:', error);
            // Use empty data if fetch fails
            portfolioData = {
                positions: [],
                transactions: [],
                stats: {
                    activePositions: 0,
                    totalStaked: 0,
                    totalWon: 0,
                    winRate: 0
                }
            };
        }
    }
}

/**
 * Update statistics display
 */
function updateStatistics() {
    const stats = portfolioData.stats;

    const statPositions = document.getElementById('stat-positions');
    if (statPositions) statPositions.textContent = stats.activePositions;

    const statStaked = document.getElementById('stat-staked');
    if (statStaked) statStaked.textContent = formatBalance(stats.totalStaked) + ' QIE';

    const statWon = document.getElementById('stat-won');
    if (statWon) statWon.textContent = formatBalance(stats.totalWon) + ' QIE';

    const statWinrate = document.getElementById('stat-winrate');
    if (statWinrate) statWinrate.textContent = stats.winRate.toFixed(1) + '%';

    // Update total transactions
    const totalTx = document.getElementById('total-tx');
    if (totalTx) totalTx.textContent = portfolioData.transactions.length;
}

/**
 * Load and display positions
 */
function loadPositions() {
    const container = document.getElementById('positions-container');
    if (!container) return;

    if (portfolioData.positions.length === 0) {
        container.innerHTML = `
            <div style="text-align: center; padding: var(--spacing-xl); color: var(--text-secondary);">
                <p>No active positions yet. Start predicting to see your positions here!</p>
                <a href="dashboard.html" class="btn btn-primary" style="margin-top: var(--spacing-md);">Browse Markets</a>
            </div>
        `;
        return;
    }

    container.innerHTML = portfolioData.positions.map(position => `
        <div class="position-card">
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: var(--spacing-md);">
                <div>
                    <h4 style="margin-bottom: var(--spacing-xs);">${position.question}</h4>
                    <div style="color: var(--text-secondary); font-size: var(--text-sm);">
                        Market ID: ${position.marketId}
                    </div>
                </div>
                <span class="badge badge-${position.status === 'active' ? 'success' : 'warning'}">
                    ${position.status.toUpperCase()}
                </span>
            </div>
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--spacing-md);">
                <div>
                    <div class="info-label">Your Prediction</div>
                    <div class="info-value" style="font-size: var(--text-md);">${position.prediction}</div>
                </div>
                <div>
                    <div class="info-label">Staked Amount</div>
                    <div class="info-value" style="font-size: var(--text-md);">${formatBalance(position.amount)} QIE</div>
                </div>
                <div>
                    <div class="info-label">Potential Win</div>
                    <div class="info-value" style="font-size: var(--text-md); color: var(--success);">
                        ${formatBalance(position.potentialWin)} QIE
                    </div>
                </div>
            </div>
            <div style="margin-top: var(--spacing-md); padding-top: var(--spacing-md); border-top: 1px solid rgba(255,255,255,0.1);">
                <div style="color: var(--text-secondary); font-size: var(--text-sm);">
                    Deadline: ${new Date(position.deadline).toLocaleString()}
                </div>
            </div>
        </div>
    `).join('');
}

/**
 * Load and display transactions
 */
function loadTransactions() {
    const container = document.getElementById('transactions-container');
    if (!container) return;

    if (portfolioData.transactions.length === 0) {
        container.innerHTML = `
            <div style="text-align: center; padding: var(--spacing-xl); color: var(--text-secondary);">
                <p>No transactions yet. Your transaction history will appear here.</p>
            </div>
        `;
        return;
    }

    container.innerHTML = portfolioData.transactions.map(tx => `
        <div class="transaction-item">
            <div>
                <div style="font-weight: 600; margin-bottom: 4px;">${tx.type}</div>
                <div style="color: var(--text-secondary); font-size: var(--text-sm);">
                    ${new Date(tx.timestamp).toLocaleString()}
                </div>
            </div>
            <div style="text-align: right;">
                <div style="font-weight: 600; color: ${tx.amount > 0 ? 'var(--success)' : 'var(--text-primary)'};">
                    ${tx.amount > 0 ? '+' : ''}${formatBalance(Math.abs(tx.amount))} QIE
                </div>
                <div style="color: var(--text-secondary); font-size: var(--text-sm);">
                    ${formatAddress(tx.hash)}
                </div>
            </div>
        </div>
    `).join('');
}

/**
 * Copy address to clipboard
 */
function copyAddress() {
    const addressText = document.getElementById('address-text');
    if (!addressText) return;

    const fullAddress = addressText.getAttribute('data-full-address');
    if (!fullAddress) return;

    navigator.clipboard.writeText(fullAddress).then(() => {
        showNotification('Address copied to clipboard!', 'success');
    }).catch(err => {
        console.error('Failed to copy:', err);
        showNotification('Failed to copy address', 'danger');
    });
}

/**
 * Get network name from chain ID
 */
function getNetworkName(chainId) {
    const networks = {
        1: 'Ethereum Mainnet',
        5: 'Goerli Testnet',
        11155111: 'Sepolia Testnet',
        1234: 'QIE Mainnet',
        1983: 'QIE Testnet'  // Correct Chain ID for QIE Testnet
    };
    return networks[chainId] || `Chain ID: ${chainId}`;
}

/**
 * Generate demo positions
 */
function generateDemoPositions() {
    return [
        {
            marketId: 'DEMO-001',
            question: 'Will Bitcoin reach $100,000 by end of 2024?',
            prediction: 'YES',
            amount: 500,
            potentialWin: 750,
            status: 'active',
            deadline: Date.now() + 30 * 24 * 60 * 60 * 1000 // 30 days from now
        },
        {
            marketId: 'DEMO-002',
            question: 'Will Ethereum 2.0 launch successfully?',
            prediction: 'YES',
            amount: 750,
            potentialWin: 1125,
            status: 'active',
            deadline: Date.now() + 15 * 24 * 60 * 60 * 1000 // 15 days from now
        },
        {
            marketId: 'DEMO-003',
            question: 'Will AI surpass human intelligence in 2024?',
            prediction: 'NO',
            amount: 250,
            potentialWin: 375,
            status: 'active',
            deadline: Date.now() + 60 * 24 * 60 * 60 * 1000 // 60 days from now
        }
    ];
}

/**
 * Generate demo transactions
 */
function generateDemoTransactions() {
    return [
        {
            type: 'Stake Placed',
            amount: -500,
            timestamp: Date.now() - 5 * 24 * 60 * 60 * 1000,
            hash: '0xDemo' + Math.random().toString(36).substring(2, 15)
        },
        {
            type: 'Stake Placed',
            amount: -750,
            timestamp: Date.now() - 3 * 24 * 60 * 60 * 1000,
            hash: '0xDemo' + Math.random().toString(36).substring(2, 15)
        },
        {
            type: 'Rewards Claimed',
            amount: 1200,
            timestamp: Date.now() - 2 * 24 * 60 * 60 * 1000,
            hash: '0xDemo' + Math.random().toString(36).substring(2, 15)
        },
        {
            type: 'Stake Placed',
            amount: -250,
            timestamp: Date.now() - 1 * 24 * 60 * 60 * 1000,
            hash: '0xDemo' + Math.random().toString(36).substring(2, 15)
        }
    ];
}

/**
 * Override connectWallet to refresh profile after connection
 */
const originalConnectWallet = window.connectWallet;
window.connectWallet = async function () {
    const result = await originalConnectWallet();
    if (result) {
        // Refresh the profile page
        const isDemoMode = localStorage.getItem('demoMode') === 'true';
        await showConnectedProfile(result, isDemoMode);
    }
    return result;
};

/**
 * Override disconnectWallet to show not connected state
 */
const originalDisconnectWallet = window.disconnectWallet;
window.disconnectWallet = function () {
    originalDisconnectWallet();
    showNotConnectedProfile();
};

// Listen for wallet connection events (from other pages or direct connection)
window.addEventListener('walletConnected', async (event) => {
    const { address, walletType } = event.detail;
    const isDemoMode = localStorage.getItem('demoMode') === 'true';
    if (address) {
        await showConnectedProfile(address, isDemoMode);
    }
});

// Listen for account changes from wallet extension
if (window.ethereum) {
    window.ethereum.on('accountsChanged', async (accounts) => {
        if (accounts.length === 0) {
            showNotConnectedProfile();
        } else {
            const isDemoMode = localStorage.getItem('demoMode') === 'true';
            await showConnectedProfile(accounts[0], isDemoMode);
        }
    });
}

// Initialize on page load
window.addEventListener('load', () => {
    initPortfolio();
});
