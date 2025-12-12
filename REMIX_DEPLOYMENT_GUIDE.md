# Complete Guide: Deploying Smart Contracts with Remix IDE

This guide will walk you through deploying a Solidity smart contract using Remix IDE, even if you're completely new to blockchain development.

---

## Prerequisites

Before you start, make sure you have:
1. **MetaMask Wallet** installed in your browser
2. **QIE Network** configured in MetaMask
3. **Some QIE tokens** in your wallet for gas fees

---

## Step 1: Open Remix IDE

1. Open your web browser (Chrome, Firefox, or Brave recommended)
2. Go to: **https://remix.ethereum.org/**
3. Wait for Remix IDE to load completely

**What you'll see:**
- A file explorer on the left
- A code editor in the center
- Various tabs at the top

---

## Step 2: Create or Import Your Smart Contract

### Option A: Create a New Contract

1. In the **File Explorer** (left sidebar), look for the "contracts" folder
2. Right-click on the "contracts" folder
3. Select **"New File"**
4. Name your file (e.g., `MyContract.sol`)
   - **Important:** Always use `.sol` extension for Solidity files

### Option B: Use an Existing Contract

1. If you already have a contract, click the **"Load from"** button
2. Choose **"Import from file"** or paste your code

### Sample Contract (if you need one to practice):

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract SimpleStorage {
    uint256 private storedData;
    
    event DataStored(uint256 data);
    
    function set(uint256 x) public {
        storedData = x;
        emit DataStored(x);
    }
    
    function get() public view returns (uint256) {
        return storedData;
    }
}
```

**Copy this sample contract** into your new file if you want to practice.

---

## Step 3: Compile Your Contract

1. Click on the **"Solidity Compiler"** icon in the left sidebar
   - It looks like an "S" with two overlapping squares
   
2. **Configure Compiler Settings:**
   - **Compiler Version:** Select a version that matches your contract's `pragma` statement
     - For the sample above, select `0.8.0` or higher
   - **Auto compile:** You can check this box for automatic compilation
   
3. Click the **"Compile"** button (big blue button)
   - If using auto-compile, it will compile automatically when you save

4. **Check for Success:**
   - ✅ **Green checkmark** = Compilation successful
   - ❌ **Red X** = Compilation failed (check errors below)
   
5. **If you see errors:**
   - Read the error messages carefully
   - Common issues:
     - Wrong compiler version
     - Missing semicolons
     - Typos in code
   - Fix the errors and compile again

---

## Step 4: Configure MetaMask for QIE Network

### 4.1: Open MetaMask

1. Click the **MetaMask extension** in your browser
2. **Unlock** your wallet if locked (enter password)

### 4.2: Switch to QIE Network

1. Click the **network dropdown** at the top of MetaMask
   - It might say "Ethereum Mainnet" by default
2. Look for **"QIE Network"** or **"QIE Testnet"** in the list
3. Click to select it

### 4.3: If QIE Network is Not Listed

You need to add it manually:

1. Click **"Add Network"** or **"Add Network Manually"**
2. Enter the following details:

```
Network Name: QIE Testnet
RPC URL: [Your QIE RPC URL - get this from your project documentation]
Chain ID: [Your QIE Chain ID - get this from your project documentation]
Currency Symbol: QIE
Block Explorer URL: [Your QIE Explorer URL - optional]
```

3. Click **"Save"**
4. Switch to the newly added QIE Network

### 4.4: Verify You Have Funds

1. Check your MetaMask balance
2. You should see some **QIE tokens**
3. If you have 0 QIE, you need to get test tokens from a faucet or transfer some

---

## Step 5: Deploy Your Contract

### 5.1: Open Deploy Tab

1. Click on the **"Deploy & Run Transactions"** icon in the left sidebar
   - It looks like an Ethereum logo with an arrow

### 5.2: Configure Environment

1. **ENVIRONMENT:** Click the dropdown
2. Select **"Injected Provider - MetaMask"**
   - This connects Remix to your MetaMask wallet
   
3. **MetaMask Popup:**
   - A MetaMask popup will appear
   - Click **"Next"** then **"Connect"**
   - This allows Remix to interact with your wallet

### 5.3: Verify Connection

After connecting, you should see:
- **Account:** Your wallet address (starts with 0x...)
- **Balance:** Your QIE token balance
- **Network:** Should show your QIE network chain ID

**Important:** Make sure the network shown matches your QIE network!

### 5.4: Select Contract to Deploy

1. Look for the **"CONTRACT"** dropdown
2. Select your contract from the list
   - For the sample, select `SimpleStorage`

### 5.5: Constructor Parameters (if any)

- If your contract has a constructor that requires parameters:
  - You'll see input fields appear
  - Enter the required values
- The sample contract has no constructor parameters, so skip this

### 5.6: Deploy!

1. Click the **"Deploy"** button (orange button)
2. **MetaMask will pop up** asking you to confirm the transaction
3. Review the transaction:
   - **Gas Fee:** Amount you'll pay for deployment
   - **Total:** Should show the gas fee
4. Click **"Confirm"** in MetaMask

### 5.7: Wait for Deployment

1. You'll see a **pending transaction** indicator
2. Wait for the transaction to be confirmed (usually 10-30 seconds)
3. **Success indicators:**
   - Green checkmark in Remix console
   - Transaction appears in "Deployed Contracts" section

---

## Step 6: Find Your Contract Address

### After Successful Deployment:

1. Look at the **"Deployed Contracts"** section (bottom of Deploy tab)
2. You'll see your contract listed with:
   - Contract name
   - **Contract address** (starts with 0x...)
   - Available functions

### Copy Your Contract Address:

1. Click the **copy icon** next to the contract address
2. **Save this address** - you'll need it to interact with your contract!

**Example:**
```
Contract Address: 0x1234567890abcdef1234567890abcdef12345678
```

---

## Step 7: Interact with Your Deployed Contract

### 7.1: View Contract Functions

In the "Deployed Contracts" section, click the **dropdown arrow** next to your contract to expand it.

You'll see all your contract's functions:
- **Orange buttons:** Functions that modify state (cost gas)
- **Blue buttons:** View/read functions (free, no gas)

### 7.2: Test Your Contract

For the sample `SimpleStorage` contract:

**Set a value:**
1. Find the `set` function (orange button)
2. Enter a number in the input field (e.g., `42`)
3. Click the **"set"** button
4. **Confirm** the transaction in MetaMask
5. Wait for confirmation

**Get the value:**
1. Find the `get` function (blue button)
2. Click the **"get"** button
3. The stored value will appear below (should be `42`)

---

## Step 8: Verify on Block Explorer (Optional)

1. Copy your **contract address**
2. Go to your **QIE Block Explorer**
3. Paste the address in the search bar
4. You can see:
   - Contract creation transaction
   - All interactions with your contract
   - Contract balance

---

## Common Issues & Solutions

### Issue 1: "Gas estimation failed"
**Solution:** 
- Check if you have enough QIE tokens
- Try increasing gas limit manually
- Check if your contract has errors

### Issue 2: "Nonce too high"
**Solution:**
- Go to MetaMask Settings → Advanced → Reset Account
- This clears transaction history

### Issue 3: "Transaction failed"
**Solution:**
- Check contract logic for errors
- Ensure you're on the correct network
- Verify you have sufficient balance

### Issue 4: MetaMask doesn't connect
**Solution:**
- Refresh Remix page
- Disconnect and reconnect MetaMask
- Try a different browser

### Issue 5: Wrong network in Remix
**Solution:**
- Switch network in MetaMask first
- Then reconnect in Remix
- Verify chain ID matches

---

## Important Tips

1. **Always test on testnet first** before deploying to mainnet
2. **Save your contract address** immediately after deployment
3. **Keep your private keys secure** - never share them
4. **Double-check network** before deploying
5. **Start with small amounts** when testing
6. **Verify contract code** on block explorer for transparency

---

## Next Steps

After deployment, you can:
1. **Interact** with your contract through Remix
2. **Build a frontend** to interact with your contract
3. **Verify** your contract source code on the block explorer
4. **Share** your contract address with others

---

## Quick Reference

| Action | Location |
|--------|----------|
| Create file | File Explorer → Right-click → New File |
| Compile | Solidity Compiler tab → Compile button |
| Deploy | Deploy tab → Set environment → Deploy |
| Contract address | Deployed Contracts section |
| Interact | Deployed Contracts → Expand contract |

---

## Need Help?

If you encounter issues:
1. Check the **Remix console** (bottom of screen) for error messages
2. Review **MetaMask transaction history** for failed transactions
3. Verify you're on the **correct network**
4. Ensure you have **sufficient QIE tokens**

---

**Congratulations!** 🎉 You now know how to deploy smart contracts using Remix IDE!
