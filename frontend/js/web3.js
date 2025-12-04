/**
 * Web3 Integration for QIE Nexus
 * Handles wallet connection (QIE Wallet, MetaMask, Demo Mode), network switching, and smart contract interactions
 */

// Configuration - Flexible network support
const QIE_MAINNET = {
    chainId: '0x4D2', // 1234 in hex (QIE Blockchain)
    chainName: 'QIE Blockchain',
    nativeCurrency: {
        name: 'QIE',
        symbol: 'QIE',
        decimals: 18
    },
    rpcUrls: ['https://rpc.qie.digital'],
    blockExplorerUrls: ['https://explorer.qie.digital']
};

const QIE_TESTNET = {
    chainId: '0x7BF', // 1983 in hex (QIE Testnet)
    chainName: 'QIE Testnet',
    nativeCurrency: {
        name: 'QIE',
        symbol: 'QIE',
        decimals: 18
    },
    rpcUrls: ['https://rpc1testnet.qie.digital'],
    blockExplorerUrls: ['https://testnet.qie.digital']
};

// Skip network validation - work with any network
const SKIP_NETWORK_CHECK = true;

// Contract addresses (update after deployment)
const CONTRACTS = {
    PREDICTION_CORE: '0x0000000000000000000000000000000000000000',
    ORACLE_AGGREGATOR: '0x0000000000000000000000000000000000000000',
    NEURAL_INFERENCE: '0x0000000000000000000000000000000000000000',
    QIE_TOKEN: '0x0000000000000000000000000000000000000000'
};

// Global state
let web3 = null;
let userAccount = null;
let contracts = {};

/**
 * Detect available wallets
 */
function detectWallets() {
    const wallets = {
        qieWallet: false,
        metaMask: false
    };

    // Check for QIE Wallet
    if (typeof window.ethereum !== 'undefined' && window.ethereum.isQIEWallet) {
        wallets.qieWallet = true;
    }

    // Check for MetaMask
    if (typeof window.ethereum !== 'undefined' && window.ethereum.isMetaMask) {
        wallets.metaMask = true;
    }

    // If ethereum exists but neither flag is set, assume it could be either
    if (typeof window.ethereum !== 'undefined' && !wallets.qieWallet && !wallets.metaMask) {
        // Default to MetaMask if we can't determine
        wallets.metaMask = true;
    }

    return wallets;
}

/**
 * Show wallet selection modal
 */
function showWalletSelectionModal() {
    return new Promise((resolve) => {
        const wallets = detectWallets();

        // Create modal
        const modal = document.createElement('div');
        modal.id = 'wallet-selection-modal';
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.9);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10000;
            animation: fadeIn 0.3s ease-out;
        `;

        const modalContent = document.createElement('div');
        modalContent.style.cssText = `
            background: var(--bg-card);
            padding: 40px;
            border-radius: var(--radius-2xl);
            max-width: 500px;
            width: 90%;
            border: 1px solid rgba(233, 30, 140, 0.3);
        `;

        modalContent.innerHTML = `
            <h2 style="margin-bottom: 10px; color: var(--text-primary);">Connect Your Wallet</h2>
            <p style="color: var(--text-secondary); margin-bottom: 30px;">Choose how you want to connect to QIE Nexus</p>
            
            <div id="wallet-options" style="display: flex; flex-direction: column; gap: 15px;">
                ${wallets.qieWallet ? `
                <button class="wallet-option" data-wallet="qie" style="
                    display: flex;
                    align-items: center;
                    gap: 15px;
                    padding: 20px;
                    background: var(--bg-secondary);
                    border: 2px solid rgba(233, 30, 140, 0.3);
                    border-radius: var(--radius-lg);
                    cursor: pointer;
                    transition: all 0.3s;
                    width: 100%;
                ">
                    <div style="font-size: 2rem;">🔮</div>
                    <div style="text-align: left; flex: 1;">
                        <div style="font-weight: 600; font-size: var(--text-lg); color: var(--text-primary);">QIE Wallet</div>
                        <div style="font-size: var(--text-sm); color: var(--text-secondary);">Official QIE Wallet Extension</div>
                    </div>
                    <div style="color: var(--success);">✓ Detected</div>
                </button>
                ` : `
                <button class="wallet-option-disabled" style="
                    display: flex;
                    align-items: center;
                    gap: 15px;
                    padding: 20px;
                    background: var(--bg-secondary);
                    border: 2px solid rgba(255, 255, 255, 0.1);
                    border-radius: var(--radius-lg);
                    opacity: 0.5;
                    width: 100%;
                ">
                    <div style="font-size: 2rem;">🔮</div>
                    <div style="text-align: left; flex: 1;">
                        <div style="font-weight: 600; font-size: var(--text-lg); color: var(--text-primary);">QIE Wallet</div>
                        <div style="font-size: var(--text-sm); color: var(--text-secondary);">
                            <a href="https://www.qiewallet.me/" target="_blank" style="color: var(--qie-primary);">Install QIE Wallet →</a>
                        </div>
                    </div>
                </button>
                `}

                ${wallets.metaMask ? `
                <button class="wallet-option" data-wallet="metamask" style="
                    display: flex;
                    align-items: center;
                    gap: 15px;
                    padding: 20px;
                    background: var(--bg-secondary);
                    border: 2px solid rgba(233, 30, 140, 0.3);
                    border-radius: var(--radius-lg);
                    cursor: pointer;
                    transition: all 0.3s;
                    width: 100%;
                ">
                    <div style="font-size: 2rem;">🦊</div>
                    <div style="text-align: left; flex: 1;">
                        <div style="font-weight: 600; font-size: var(--text-lg); color: var(--text-primary);">MetaMask</div>
                        <div style="font-size: var(--text-sm); color: var(--text-secondary);">Popular Ethereum Wallet</div>
                    </div>
                    <div style="color: var(--success);">✓ Detected</div>
                </button>
                ` : `
                <button class="wallet-option-disabled" style="
                    display: flex;
                    align-items: center;
                    gap: 15px;
                    padding: 20px;
                    background: var(--bg-secondary);
                    border: 2px solid rgba(255, 255, 255, 0.1);
                    border-radius: var(--radius-lg);
                    opacity: 0.5;
                    width: 100%;
                ">
                    <div style="font-size: 2rem;">🦊</div>
                    <div style="text-align: left; flex: 1;">
                        <div style="font-weight: 600; font-size: var(--text-lg); color: var(--text-primary);">MetaMask</div>
                        <div style="font-size: var(--text-sm); color: var(--text-secondary);">
                            <a href="https://metamask.io/" target="_blank" style="color: var(--qie-primary);">Install MetaMask →</a>
                        </div>
                    </div>
                </button>
                `}

                <button class="wallet-option" data-wallet="demo" style="
                    display: flex;
                    align-items: center;
                    gap: 15px;
                    padding: 20px;
                    background: var(--bg-secondary);
                    border: 2px solid rgba(233, 30, 140, 0.3);
                    border-radius: var(--radius-lg);
                    cursor: pointer;
                    transition: all 0.3s;
                    width: 100%;
                ">
                    <div style="font-size: 2rem;">🎮</div>
                    <div style="text-align: left; flex: 1;">
                        <div style="font-weight: 600; font-size: var(--text-lg); color: var(--text-primary);">Demo Mode</div>
                        <div style="font-size: var(--text-sm); color: var(--text-secondary);">Try without a wallet (10,000 QIE)</div>
                    </div>
                </button>
            </div>

            <button id="cancel-wallet-selection" style="
                margin-top: 20px;
                width: 100%;
                padding: 12px;
                background: transparent;
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: var(--radius-md);
                color: var(--text-secondary);
                cursor: pointer;
                transition: all 0.3s;
            ">Cancel</button>
        `;

        modal.appendChild(modalContent);
        document.body.appendChild(modal);

        // Add hover effects
        const style = document.createElement('style');
        style.textContent = `
            .wallet-option:hover {
                border-color: var(--qie-primary) !important;
                transform: translateY(-2px);
                box-shadow: 0 10px 30px rgba(233, 30, 140, 0.3);
            }
            #cancel-wallet-selection:hover {
                background: rgba(255, 255, 255, 0.05);
                border-color: rgba(255, 255, 255, 0.4);
            }
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }
        `;
        document.head.appendChild(style);

        // Handle wallet selection
        const walletOptions = modalContent.querySelectorAll('.wallet-option');
        walletOptions.forEach(option => {
            option.addEventListener('click', () => {
                const walletType = option.getAttribute('data-wallet');
                modal.remove();
                style.remove();
                resolve(walletType);
            });
        });

        // Handle cancel
        document.getElementById('cancel-wallet-selection').addEventListener('click', () => {
            modal.remove();
            style.remove();
            resolve(null);
        });
    });
}

/**
 * Get the best available wallet provider
 * Prioritizes QIE Wallet over MetaMask
 */
function getWalletProvider() {
    // Check for multiple providers
    const providers = [];
    
    console.log('🔍 Detecting wallet providers...');
    console.log('window.ethereum:', typeof window.ethereum !== 'undefined' ? 'exists' : 'undefined');
    
    // Check for QIE Wallet (highest priority)
    if (typeof window.ethereum !== 'undefined') {
        console.log('window.ethereum.isQIEWallet:', window.ethereum.isQIEWallet);
        console.log('window.ethereum.isMetaMask:', window.ethereum.isMetaMask);
        console.log('window.ethereum.providers:', window.ethereum.providers ? 'exists' : 'undefined');
        
        if (window.ethereum.isQIEWallet === true) {
            console.log('✅ QIE Wallet detected as primary provider');
            providers.push({ provider: window.ethereum, name: 'QIE Wallet', isQIE: true });
        } else if (window.ethereum.providers && Array.isArray(window.ethereum.providers)) {
            // Multiple providers detected
            console.log(`Found ${window.ethereum.providers.length} providers`);
            for (const provider of window.ethereum.providers) {
                if (provider.isQIEWallet === true) {
                    console.log('✅ QIE Wallet found in providers array');
                    providers.push({ provider, name: 'QIE Wallet', isQIE: true });
                } else if (provider.isMetaMask) {
                    console.log('🦊 MetaMask found in providers array');
                    providers.push({ provider, name: 'MetaMask', isQIE: false });
                }
            }
        } else if (window.ethereum.isMetaMask) {
            console.log('🦊 MetaMask detected as primary provider');
            providers.push({ provider: window.ethereum, name: 'MetaMask', isQIE: false });
        } else {
            // Unknown provider but ethereum exists
            console.log('⚠️ Unknown wallet provider detected');
            providers.push({ provider: window.ethereum, name: 'Wallet', isQIE: false });
        }
    } else {
        console.log('❌ No wallet provider detected');
    }

    // Return QIE Wallet if available, otherwise return first provider
    const qieWallet = providers.find(p => p.isQIE);
    if (qieWallet) {
        console.log('🎯 Using QIE Wallet');
        return qieWallet;
    }
    
    if (providers.length > 0) {
        console.log(`🎯 Using ${providers[0].name}`);
        return providers[0];
    }
    
    console.log('❌ No wallet provider available');
    return null;
}

/**
 * Connect wallet - INSTANT connection (no modal delay)
 * Opens QIE Wallet extension when available, falls back to MetaMask
 */
async function connectWallet() {
    try {
        // Get the best available wallet provider
        const walletInfo = getWalletProvider();
        
        if (!walletInfo) {
            // No wallet detected - offer demo mode
            const useDemoMode = confirm(
                '⚠️ No wallet detected!\n\n' +
                'Would you like to use DEMO MODE?\n\n' +
                '✓ Test all features\n' +
                '✓ No real transactions\n' +
                '✓ 10,000 QIE balance\n\n' +
                'Click OK for Demo Mode, or Cancel to install QIE Wallet.'
            );

            if (useDemoMode) {
                return connectDemoWallet();
            } else {
                window.open('https://www.qiewallet.me/', '_blank');
                showNotification('Please install QIE Wallet to continue', 'info');
                return null;
            }
        }

        const { provider, name: walletName, isQIE: isQIEWallet } = walletInfo;
        
        // Set the provider as the active ethereum provider
        window.ethereum = provider;

        // Initialize Web3 with the selected provider
        web3 = new Web3(provider);
        console.log(`✅ Web3 initialized with ${walletName} provider`);

        // Skip checking existing accounts - always request to ensure popup opens
        // This ensures the extension popup always appears for user interaction
        console.log('ℹ️ Skipping eth_accounts check - will directly request connection');
        console.log('ℹ️ This ensures the wallet popup always opens');

        // Request connection - this should open the extension popup
        console.log(`🔌 Requesting connection to ${walletName}...`);
        console.log(`📝 Provider details:`, {
            isQIEWallet: provider.isQIEWallet,
            isMetaMask: provider.isMetaMask,
            hasRequest: typeof provider.request === 'function',
            requestMethod: typeof provider.request
        });
        
        showNotification(`Opening ${walletName} extension...\nPlease check your browser for the popup!`, 'info');

        // Request account access - this opens the wallet extension popup
        // The wallet extension will pop up for user to approve connection
        console.log(`📞 Calling eth_requestAccounts on ${walletName} provider...`);
        console.log('⚠️ If the popup does not appear, check:');
        console.log('   1. Browser popup blocker settings');
        console.log('   2. Extension is enabled and unlocked');
        console.log('   3. Extension icon in browser toolbar');
        console.log('   4. Look for a notification in the extension icon');
        
        let accounts = [];
        try {
            // Add a small delay to ensure the notification is visible
            await new Promise(resolve => setTimeout(resolve, 100));
            
            console.log('⏳ Sending request now...');
            const requestStartTime = Date.now();
            
            accounts = await provider.request({
                method: 'eth_requestAccounts'
            });
            
            const requestDuration = Date.now() - requestStartTime;
            console.log(`✅ ${walletName} request completed in ${requestDuration}ms`);
            console.log(`✅ Accounts received:`, accounts);
            
            if (!accounts || accounts.length === 0) {
                showNotification('No accounts returned. Please unlock your wallet and try again.', 'warning');
                return null;
            }
        } catch (error) {
            console.error(`❌ Error requesting accounts from ${walletName}:`, error);
            console.error('Error details:', {
                code: error.code,
                message: error.message,
                stack: error.stack
            });
            
            // If user rejects, handle gracefully
            if (error.code === 4001) {
                showNotification('Connection rejected. Please try again.', 'warning');
                return null;
            }
            
            // If popup was blocked or other error
            showNotification(`Failed to open ${walletName}: ${error.message}\nPlease check your browser settings.`, 'danger');
            throw error;
        }

        if (!accounts || accounts.length === 0) {
            showNotification('No accounts found. Please unlock your wallet.', 'warning');
            return null;
        }

        userAccount = accounts[0];

        // Determine wallet type automatically
        const walletType = isQIEWallet ? 'qie' : 'metamask';

        // Try to resolve QIE domain name
        let domainName = null;
        if (isQIEWallet) {
            try {
                domainName = await resolveAddressToDomain(userAccount);
            } catch (error) {
                console.log('Domain resolution not available:', error);
            }
        }

        // Get balance from whatever network the wallet is connected to
        let balance = '0';
        let networkName = 'Unknown';
        try {
            // Get current chain ID
            const chainId = await web3.eth.getChainId();
            networkName = getNetworkName(chainId);
            console.log('Connected to network:', networkName, 'Chain ID:', chainId);

            // Get balance from current network
            const balanceWei = await web3.eth.getBalance(userAccount);
            balance = web3.utils.fromWei(balanceWei, 'ether');
            console.log('Balance fetched:', balance);
        } catch (error) {
            console.log('Could not fetch balance:', error.message);
            // Use a placeholder balance - wallet still connects!
            balance = '0';
        }

        // Update UI with domain name if available
        updateWalletUI(userAccount, balance, domainName);

        // Store in localStorage
        localStorage.setItem('walletConnected', 'true');
        localStorage.setItem('walletAddress', userAccount);
        localStorage.setItem('walletType', walletType);
        localStorage.setItem('demoMode', 'false');

        if (domainName) {
            localStorage.setItem('qieDomain', domainName);
        }

        const displayName = domainName || formatAddress(userAccount);
        const balanceDisplay = balance !== '0' ? `${formatBalance(balance)} QIE` : 'Connected';
        showNotification(`${walletName} connected: ${displayName}\nNetwork: ${networkName}\nBalance: ${balanceDisplay} 🎉`, 'success');

        // Trigger portfolio refresh if on portfolio page
        if (typeof showConnectedProfile === 'function') {
            const isDemoMode = false;
            setTimeout(() => showConnectedProfile(userAccount, isDemoMode), 100);
        } else if (typeof initPortfolio === 'function') {
            setTimeout(() => initPortfolio(), 100);
        }

        // Dispatch custom event for other pages to listen
        window.dispatchEvent(new CustomEvent('walletConnected', { 
            detail: { address: userAccount, walletType, domainName } 
        }));

        return userAccount;
    } catch (error) {
        console.error('Error connecting wallet:', error);

        // Handle user rejection
        if (error.code === 4001) {
            showNotification('Connection rejected. Please try again.', 'warning');
        } else {
            showNotification('Failed to connect: ' + error.message, 'danger');
        }

        return null;
    }
}

/**
 * Connect demo wallet (for testing without MetaMask)
 */
function connectDemoWallet() {
    // Generate a demo address
    const demoAddress = '0xDemo' + Math.random().toString(36).substring(2, 15).toUpperCase();
    const demoBalance = '10000'; // 10,000 QIE for demo

    userAccount = demoAddress;

    // Update UI
    updateWalletUI(demoAddress, demoBalance);

    // Store in localStorage
    localStorage.setItem('walletConnected', 'true');
    localStorage.setItem('walletAddress', demoAddress);
    localStorage.setItem('walletType', 'demo');
    localStorage.setItem('demoMode', 'true');
    localStorage.setItem('demoBalance', demoBalance);

    showNotification('🎮 Demo Mode Activated! Balance: 10,000 QIE', 'success');

    return demoAddress;
}

/**
 * Disconnect wallet
 */
function disconnectWallet() {
    userAccount = null;
    localStorage.removeItem('walletConnected');
    localStorage.removeItem('walletAddress');
    localStorage.removeItem('walletType');
    localStorage.removeItem('demoMode');
    localStorage.removeItem('demoBalance');
    updateWalletUI(null, 0);
    showNotification('Wallet disconnected', 'info');
}

/**
 * Switch to QIE network
 */
async function switchNetwork(useTestnet = false) {
    const network = useTestnet ? QIE_TESTNET : QIE_MAINNET;

    try {
        await window.ethereum.request({
            method: 'wallet_switchEthereumChain',
            params: [{ chainId: network.chainId }],
        });

        showNotification(`Switched to ${network.chainName}`, 'success');
    } catch (switchError) {
        // Network not added, try adding it
        if (switchError.code === 4902) {
            try {
                await window.ethereum.request({
                    method: 'wallet_addEthereumChain',
                    params: [network],
                });
                showNotification(`Added ${network.chainName}`, 'success');
            } catch (addError) {
                console.error('Error adding network:', addError);
                showNotification('Failed to add network', 'danger');
            }
        } else {
            console.error('Error switching network:', switchError);
            showNotification('Failed to switch network', 'danger');
        }
    }
}

/**
 * Get QIE token balance
 */
async function getQIEBalance(address) {
    try {
        const balance = await web3.eth.getBalance(address);
        return web3.utils.fromWei(balance, 'ether');
    } catch (error) {
        console.error('Error getting balance:', error);
        return '0';
    }
}

/**
 * Resolve QIE domain to address
 * Converts domain names like "nexus.qie" to wallet addresses
 */
async function resolveDomainToAddress(domain) {
    try {
        // Check if QIE Wallet provider has domain resolution
        if (window.ethereum && window.ethereum.isQIEWallet) {
            // Try to use QIE Wallet's domain resolution API
            const address = await window.ethereum.request({
                method: 'qie_resolveDomain',
                params: [domain]
            });
            return address;
        }

        // Fallback: If no native support, return null
        console.log('QIE domain resolution not available');
        return null;
    } catch (error) {
        console.error('Error resolving domain:', error);
        return null;
    }
}

/**
 * Resolve address to QIE domain
 * Converts wallet addresses to domain names like "nexus.qie"
 */
async function resolveAddressToDomain(address) {
    try {
        // Check if QIE Wallet provider has reverse domain resolution
        if (window.ethereum && window.ethereum.isQIEWallet) {
            // Try to use QIE Wallet's reverse resolution API
            const domain = await window.ethereum.request({
                method: 'qie_resolveAddress',
                params: [address]
            });
            return domain;
        }

        // Fallback: Check localStorage for manually entered domain
        const savedDomain = localStorage.getItem('qieDomain');
        if (savedDomain) {
            return savedDomain;
        }

        return null;
    } catch (error) {
        console.error('Error resolving address to domain:', error);
        return null;
    }
}

/**
 * Load contract instance
 */
function loadContract(name, address, abi) {
    if (!web3) return null;
    contracts[name] = new web3.eth.Contract(abi, address);
    return contracts[name];
}

/**
 * Stake on prediction
 */
async function stakeOnPrediction(marketId, choice, amount) {
    try {
        if (!userAccount) {
            showNotification('Please connect your wallet first', 'warning');
            return null;
        }

        const contract = contracts['PREDICTION_CORE'];
        if (!contract) {
            showNotification('Contract not loaded', 'danger');
            return null;
        }

        // Convert amount to wei
        const amountWei = web3.utils.toWei(amount.toString(), 'ether');

        // Show transaction modal
        showTransactionModal('Staking...', 'Please confirm the transaction in your wallet');

        // Call contract
        const tx = await contract.methods.stakePrediction(
            marketId,
            choice,
            amountWei
        ).send({
            from: userAccount,
            value: 0 // Assuming ERC20 token, not native
        });

        // Wait for confirmation
        showTransactionModal('Confirming...', 'Waiting for blockchain confirmation');

        // Success
        hideTransactionModal();
        showNotification('Stake successful!', 'success');

        return tx.transactionHash;
    } catch (error) {
        console.error('Error staking:', error);
        hideTransactionModal();
        showNotification('Stake failed: ' + error.message, 'danger');
        return null;
    }
}

/**
 * Claim rewards
 */
async function claimRewards(marketId) {
    try {
        if (!userAccount) {
            showNotification('Please connect your wallet first', 'warning');
            return null;
        }

        const contract = contracts['PREDICTION_CORE'];
        if (!contract) {
            showNotification('Contract not loaded', 'danger');
            return null;
        }

        showTransactionModal('Claiming...', 'Please confirm the transaction in your wallet');

        const tx = await contract.methods.claimRewards(marketId).send({
            from: userAccount
        });

        hideTransactionModal();
        showNotification('Rewards claimed successfully!', 'success');

        // Refresh balance
        const balance = await getQIEBalance(userAccount);
        updateWalletUI(userAccount, balance);

        return tx.transactionHash;
    } catch (error) {
        console.error('Error claiming rewards:', error);
        hideTransactionModal();
        showNotification('Claim failed: ' + error.message, 'danger');
        return null;
    }
}

/**
 * Create market
 */
async function createMarket(question, deadline, oracleAddress) {
    try {
        if (!userAccount) {
            showNotification('Please connect your wallet first', 'warning');
            return null;
        }

        const contract = contracts['PREDICTION_CORE'];
        if (!contract) {
            showNotification('Contract not loaded', 'danger');
            return null;
        }

        showTransactionModal('Creating Market...', 'Please confirm the transaction in your wallet');

        const tx = await contract.methods.createMarket(
            question,
            deadline,
            oracleAddress
        ).send({
            from: userAccount
        });

        hideTransactionModal();
        showNotification('Market created successfully!', 'success');

        return tx.transactionHash;
    } catch (error) {
        console.error('Error creating market:', error);
        hideTransactionModal();
        showNotification('Market creation failed: ' + error.message, 'danger');
        return null;
    }
}

/**
 * Listen to market events
 */
function listenToMarketEvents(callback) {
    const contract = contracts['PREDICTION_CORE'];
    if (!contract) return;

    // MarketCreated event
    contract.events.MarketCreated({
        fromBlock: 'latest'
    })
        .on('data', (event) => {
            console.log('MarketCreated:', event);
            callback('MarketCreated', event.returnValues);
        })
        .on('error', console.error);

    // PredictionStaked event
    contract.events.PredictionStaked({
        fromBlock: 'latest'
    })
        .on('data', (event) => {
            console.log('PredictionStaked:', event);
            callback('PredictionStaked', event.returnValues);
        })
        .on('error', console.error);

    // MarketSettled event
    contract.events.MarketSettled({
        fromBlock: 'latest'
    })
        .on('data', (event) => {
            console.log('MarketSettled:', event);
            callback('MarketSettled', event.returnValues);
        })
        .on('error', console.error);
}

/**
 * Helper: Format address
 */
function formatAddress(address) {
    if (!address) return '';
    return `${address.substring(0, 6)}...${address.substring(address.length - 4)}`;
}

/**
 * Helper: Format balance
 */
function formatBalance(balance) {
    return parseFloat(balance).toFixed(4);
}

/**
 * Update wallet UI
 */
function updateWalletUI(address, balance, domainName = null) {
    const walletBtn = document.getElementById('wallet-btn');
    const walletAddress = document.getElementById('wallet-address');
    const walletBalance = document.getElementById('wallet-balance');

    if (address) {
        // Use domain name if available, otherwise use formatted address
        const displayName = domainName || formatAddress(address);

        if (walletBtn) {
            walletBtn.textContent = displayName;
            // Add special styling for domain names
            if (domainName) {
                walletBtn.style.background = 'linear-gradient(135deg, #E91E8C 0%, #9333EA 100%)';
            }
        }

        if (walletAddress) walletAddress.textContent = displayName;
        if (walletBalance) walletBalance.textContent = formatBalance(balance) + ' QIE';
    } else {
        if (walletBtn) {
            walletBtn.textContent = 'Connect Wallet';
            walletBtn.style.background = ''; // Reset styling
        }
        if (walletAddress) walletAddress.textContent = 'Not connected';
        if (walletBalance) walletBalance.textContent = '0 QIE';
    }
}

/**
 * Show notification
 */
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;

    // Color mapping for new QIE.digital theme
    const colors = {
        'success': '#10B981',
        'danger': '#EF4444',
        'warning': '#F59E0B',
        'info': '#E91E8C' // Pink/Magenta for info
    };

    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 16px 24px;
        background: ${colors[type] || colors.info};
        color: white;
        border-radius: 12px;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.8), 0 0 30px ${colors[type] || colors.info}40;
        z-index: 10000;
        animation: slideIn 0.3s ease-out;
        font-weight: 600;
        max-width: 400px;
    `;
    notification.textContent = message;

    document.body.appendChild(notification);

    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

/**
 * Show transaction modal
 */
function showTransactionModal(title, message) {
    let modal = document.getElementById('tx-modal');

    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'tx-modal';
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.8);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 9999;
        `;

        modal.innerHTML = `
            <div style="background: var(--bg-card); padding: 40px; border-radius: var(--radius-2xl); text-align: center; max-width: 400px;">
                <div class="spinner" style="margin: 0 auto 20px;"></div>
                <h3 id="tx-modal-title">${title}</h3>
                <p id="tx-modal-message">${message}</p>
            </div>
        `;

        document.body.appendChild(modal);
    } else {
        document.getElementById('tx-modal-title').textContent = title;
        document.getElementById('tx-modal-message').textContent = message;
        modal.style.display = 'flex';
    }
}

/**
 * Hide transaction modal
 */
function hideTransactionModal() {
    const modal = document.getElementById('tx-modal');
    if (modal) {
        modal.style.display = 'none';
    }
}

/**
 * Auto-connect on page load
 */
window.addEventListener('load', async () => {
    const wasConnected = localStorage.getItem('walletConnected');
    if (wasConnected === 'true') {
        const walletType = localStorage.getItem('walletType');
        const isDemoMode = localStorage.getItem('demoMode') === 'true';

        if (isDemoMode) {
            // Reconnect demo wallet
            connectDemoWallet();
        } else {
            // Auto-reconnect real wallet
            try {
                if (typeof window.ethereum !== 'undefined') {
                    web3 = new Web3(window.ethereum);
                    const accounts = await window.ethereum.request({ method: 'eth_accounts' });

                    if (accounts.length > 0) {
                        userAccount = accounts[0];

                        // Try to get balance, but don't fail if RPC is down
                        let balance = '0';
                        try {
                            balance = await getQIEBalance(userAccount);
                        } catch (error) {
                            console.log('Could not fetch balance on auto-reconnect:', error.message);
                            balance = '...';
                        }

                        // Restore domain name if available
                        const savedDomain = localStorage.getItem('qieDomain');
                        updateWalletUI(userAccount, balance, savedDomain);
                    }
                }
            } catch (error) {
                console.error('Auto-connect failed:', error);
            }
        }
    }

    // Listen for account changes
    if (window.ethereum) {
        window.ethereum.on('accountsChanged', (accounts) => {
            if (accounts.length === 0) {
                disconnectWallet();
            } else {
                userAccount = accounts[0];
                connectWallet();
            }
        });

        // Listen for chain changes
        window.ethereum.on('chainChanged', () => {
            window.location.reload();
        });
    }
});
