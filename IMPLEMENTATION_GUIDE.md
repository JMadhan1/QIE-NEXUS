# 🚀 NEURAL ORACLE - Complete Implementation Guide

## 📋 Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Setup Instructions](#setup-instructions)
4. [Development Workflow](#development-workflow)
5. [Testing Guide](#testing-guide)
6. [Deployment Guide](#deployment-guide)
7. [Hackathon Submission](#hackathon-submission)

---

## 🎯 Project Overview

**Neural Oracle** is a revolutionary AI-powered prediction market platform built on QIE Blockchain featuring:

### Key Features
- ⚡ **On-Chain AI Inference**: Quantized neural networks running directly on blockchain
- 🔗 **7 Oracle Integration**: Real-time data from forex, commodities, and crypto markets
- 🚀 **3-Second Finality**: Lightning-fast transactions on QIE Blockchain
- 🧠 **Self-Learning**: Federated learning for continuous model improvement
- 🏛️ **DAO Governance**: Community-controlled platform evolution

### Tech Stack
- **Blockchain**: Solidity 0.8.20, OpenZeppelin, QIE Blockchain
- **Backend**: Flask, Web3.py, ONNX Runtime, Redis, IPFS
- **Frontend**: Vanilla HTML/CSS/JS, Web3.js, Chart.js
- **AI/ML**: PyTorch, ONNX, INT8 Quantization

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     FRONTEND (HTML/CSS/JS)              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐│
│  │Dashboard │  │  Market  │  │Portfolio │  │Governance││
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬────┘│
│       │             │              │             │     │
│       └─────────────┴──────────────┴─────────────┘     │
│                         │                              │
│                    Web3.js / API Client                │
└─────────────────────────┬───────────────────────────────┘
                          │
        ┌─────────────────┴─────────────────┐
        │                                   │
┌───────▼──────────┐              ┌────────▼────────┐
│  SMART CONTRACTS │              │  BACKEND (Flask)│
│  ┌─────────────┐ │              │  ┌────────────┐ │
│  │Prediction   │ │              │  │Blockchain  │ │
│  │Core         │ │◄─────────────┼──┤Service     │ │
│  └─────────────┘ │              │  └────────────┘ │
│  ┌─────────────┐ │              │  ┌────────────┐ │
│  │Oracle       │ │◄─────────────┼──┤Oracle      │ │
│  │Aggregator   │ │              │  │Service     │ │
│  └─────────────┘ │              │  └────────────┘ │
│  ┌─────────────┐ │              │  ┌────────────┐ │
│  │Neural       │ │◄─────────────┼──┤AI Inference│ │
│  │Inference    │ │              │  │Service     │ │
│  └─────────────┘ │              │  └────────────┘ │
└──────────────────┘              └─────────────────┘
         │                                 │
         │                                 │
    ┌────▼────┐                      ┌────▼────┐
    │   QIE   │                      │  IPFS   │
    │Blockchain│                      │ (Models)│
    └─────────┘                      └─────────┘
```

---

## 🛠️ Setup Instructions

### Prerequisites
- Node.js v18+
- Python 3.9+
- Git
- MetaMask browser extension

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/neural-oracle.git
cd neural-oracle
```

### 2. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings
```

### 3. Smart Contracts Setup
```bash
cd contracts

# Initialize npm
npm init -y

# Install dependencies
npm install --save-dev hardhat @nomiclabs/hardhat-ethers ethers
npm install @openzeppelin/contracts

# Initialize Hardhat
npx hardhat init
# Choose "Create a JavaScript project"

# Copy contract files to contracts/ directory
# Update hardhat.config.js with QIE network settings
```

### 4. Frontend Setup
```bash
cd frontend

# No build step needed for vanilla JS
# Just serve the files with any static server

# Option 1: Python
python -m http.server 8000

# Option 2: Node.js
npx http-server -p 8000

# Option 3: VS Code Live Server extension
```

---

## 💻 Development Workflow

### Running the Backend
```bash
cd backend
venv\Scripts\activate  # Windows
python app.py
```

Backend runs on `http://localhost:5000`

### Testing API Endpoints
```bash
# Health check
curl http://localhost:5000/health

# Get oracle prices
curl http://localhost:5000/api/oracles/prices

# Get markets
curl http://localhost:5000/api/markets

# Get AI prediction
curl http://localhost:5000/api/ai/predict/1
```

### Compiling Smart Contracts
```bash
cd contracts
npx hardhat compile
```

### Running Tests
```bash
# Smart contract tests
cd contracts
npx hardhat test

# Backend tests
cd backend
pytest
```

### Deploying to Testnet
```bash
cd contracts

# Deploy to QIE testnet
npx hardhat run scripts/deploy.js --network qie-testnet

# Copy contract addresses to backend/.env
```

---

## 🧪 Testing Guide

### Unit Tests (Smart Contracts)
```javascript
// test/PredictionCore.test.js
describe("PredictionCore", function () {
  it("Should create a market", async function () {
    const [owner] = await ethers.getSigners();
    const PredictionCore = await ethers.getContractFactory("PredictionCore");
    const contract = await PredictionCore.deploy(tokenAddress);
    
    await contract.createMarket(
      "Will BTC > $50k?",
      Math.floor(Date.now() / 1000) + 86400,
      oracleAddress
    );
    
    const market = await contract.getMarket(1);
    expect(market.question).to.equal("Will BTC > $50k?");
  });
});
```

### Integration Tests (Backend)
```python
# test_api.py
def test_get_markets():
    response = client.get('/api/markets')
    assert response.status_code == 200
    assert 'markets' in response.json

def test_get_oracle_prices():
    response = client.get('/api/oracles/prices')
    assert response.status_code == 200
    assert 'forex' in response.json
```

### E2E Tests (Frontend)
```javascript
// Manual testing checklist
// 1. Connect wallet
// 2. Switch to QIE network
// 3. View markets
// 4. Stake on prediction
// 5. View portfolio
// 6. Claim rewards
```

---

## 🚀 Deployment Guide

### 1. Deploy Smart Contracts

```javascript
// hardhat.config.js
module.exports = {
  networks: {
    qie: {
      url: "https://rpc.qie.digital",
      accounts: [process.env.PRIVATE_KEY],
      chainId: 1234
    }
  }
};
```

```bash
# Deploy to mainnet
npx hardhat run scripts/deploy.js --network qie

# Verify contracts
npx hardhat verify --network qie CONTRACT_ADDRESS
```

### 2. Deploy Backend

**Option A: AWS EC2**
```bash
# SSH into EC2 instance
ssh -i key.pem ubuntu@your-instance-ip

# Clone repo
git clone https://github.com/yourusername/neural-oracle.git
cd neural-oracle/backend

# Install dependencies
pip3 install -r requirements.txt

# Set up environment
cp .env.example .env
nano .env  # Edit with production values

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

**Option B: DigitalOcean App Platform**
```yaml
# app.yaml
name: neural-oracle-api
services:
  - name: api
    github:
      repo: yourusername/neural-oracle
      branch: main
      deploy_on_push: true
    source_dir: /backend
    run_command: gunicorn -w 4 -b 0.0.0.0:5000 app:app
    envs:
      - key: QIE_RPC_URL
        value: https://rpc.qie.digital
```

### 3. Deploy Frontend

**Option A: Vercel**
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
cd frontend
vercel --prod
```

**Option B: Netlify**
```bash
# Install Netlify CLI
npm i -g netlify-cli

# Deploy
cd frontend
netlify deploy --prod
```

---

## 🏆 Hackathon Submission

### Demo Video Script (3 minutes)

**[0:00-0:30] Introduction**
- "Hi, I'm [Name], and I built Neural Oracle"
- "The world's first on-chain AI prediction market"
- Show landing page

**[0:30-1:00] Problem & Solution**
- "Current prediction markets are centralized and slow"
- "Neural Oracle runs AI inference directly on QIE Blockchain"
- "With 3-second finality and 7 oracle integration"

**[1:00-2:00] Live Demo**
- Connect MetaMask wallet
- Show AI prediction (78% confidence)
- Stake 100 QIE tokens
- Show 2.8s transaction confirmation
- Display real-time oracle updates

**[2:00-2:45] Technical Highlights**
- "Quantized neural networks for <500ms inference"
- "Gas-optimized smart contracts"
- "Self-learning through federated learning"
- Show code snippets

**[2:45-3:00] Closing**
- "Join our community of 500+ users"
- "Built for QIE Blockchain Hackathon 2025"
- Call to action: "Try it now at neural-oracle.app"

### Pitch Deck Outline (10 slides)

1. **Title Slide**: Neural Oracle logo + tagline
2. **Problem**: Current prediction market limitations
3. **Solution**: On-chain AI + QIE Blockchain
4. **How It Works**: Architecture diagram
5. **Key Features**: 6 feature cards
6. **Technology**: Tech stack + innovations
7. **Demo**: Screenshots of key features
8. **Traction**: User stats, TVL, accuracy
9. **Roadmap**: Q1-Q4 2025 milestones
10. **Team & Contact**: Your info + links

### Submission Checklist

- [ ] GitHub repository public
- [ ] README.md complete with setup instructions
- [ ] Demo video uploaded (YouTube/Loom)
- [ ] Pitch deck uploaded (Google Slides/PDF)
- [ ] Live demo deployed and accessible
- [ ] Smart contracts verified on QIE Explorer
- [ ] All links tested and working
- [ ] Submission form filled out
- [ ] Social media posts scheduled

---

## 📞 Support & Resources

### Documentation
- [QIE Blockchain Docs](https://docs.qie.digital)
- [Hardhat Documentation](https://hardhat.org/docs)
- [Web3.js Documentation](https://web3js.readthedocs.io)
- [Flask Documentation](https://flask.palletsprojects.com)

### Community
- Discord: [Your Discord Link]
- Telegram: [Your Telegram Link]
- Twitter: [@NeuralOracle]

### Contact
- Email: your.email@example.com
- GitHub: github.com/yourusername

---

**Good luck with the hackathon! 🚀**

Built with ❤️ for QIE Blockchain Hackathon 2025
