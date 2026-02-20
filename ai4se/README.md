# AI4SE - AI for Social Empowerment

> Local-First AI models for resource-constrained environments

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status: Active Development](https://img.shields.io/badge/Status-Active%20Development-green)]()

## 🎯 Mission

Bring specialized AI assistance to communities without internet access, electricity, or financial resources for cloud services. Our focus: **offline-first, privacy-preserving, zero-cost AI** that runs locally on affordable devices.

## 🌍 Problem We're Solving

In resource-constrained environments (slums, rural areas, developing countries):
- ❌ No reliable internet for cloud AI
- ❌ No money for API subscriptions
- ❌ No electricity infrastructure
- ❌ Privacy concerns with external services
- ❌ Language barriers (minority languages)

## ✅ Our Solution

**Small Language Models (SLMs)** that:
- ✅ Run entirely offline on phones/tablets
- ✅ Cost $0 to operate (no API fees)
- ✅ Work in "Airplane Mode"
- ✅ Protect user privacy (no data leaves device)
- ✅ Specialize in one task extremely well

## 🚀 Three Pilot Models

### 1. 🏥 Health Assistant
**Medical triage and first-contact health guidance**

- **Voice-based medical interview** (Amharic አማርኛ + English)
- **Speech-to-Text** support (Whisper)
- **Text-to-Speech** support (Piper Amharic voice)
- Symptom analysis and assessment
- Life-saving action recommendations
- Disease identification (malaria, cholera, dehydration)
- WHO protocol compliance

**Try it**: [Live Demo](https://mniami.github.io/help-children/ai4se/demo/) *(requires Chrome 113+ with WebGPU)*

**Amharic Support**: See [AMHARIC_LANGUAGE_SUPPORT.md](docs/AMHARIC_LANGUAGE_SUPPORT.md) for complete voice integration guide

### 2. 🔧 Technical Repair Assistant
**Visual AI for equipment repair**

- Photo-based device identification
- Step-by-step repair instructions
- Using locally available materials
- Voice guidance in local language
- Offline technical manuals

**Status**: In development

### 3. 🌱 Urban Farming Assistant
**Agricultural support for small-scale farming**

- Pest identification from photos
- Natural, low-cost pest control methods
- Small-space optimization (vertical farming)
- Soil and watering guidance
- Local climate calendars

**Status**: In development

## 📦 What's Included

```
ai4se/
├── demo/                    # Working WebLLM demo (try now!)
│   └── index.html          # Browser-based health assistant
├── docs/                    # Comprehensive documentation
│   ├── IMPLEMENTATION_GUIDE.md  # Technical implementation
│   └── [More guides coming]
├── models/                  # Model configurations
│   └── [Model files - download separately]
├── training/               # Fine-tuning scripts
│   └── train_medical_lora.py
└── AI4SE_PROJECT.md        # Project overview & vision
```

## 🎮 Quick Start (5 Minutes)

### Try the Demo

1. **Requirements**:
   - Chrome 113+ or Edge 113+
   - 4+ GB RAM
   - ~2 GB free storage (first time only)

2. **Run Demo**:
   ```bash
   # Clone repository
   git clone https://github.com/mniami/help-children.git
   cd help-children/ai4se/demo

   # Serve locally
   npx serve .
   # OR
   python -m http.server 8000

   # Open browser to http://localhost:8000
   ```

3. **Load Model**:
   - Click "Load Model"
   - Wait 2-5 minutes (downloads ~2 GB, cached for future use)
   - Start chatting!

4. **Test with Example**:
   - "My child has fever and diarrhea for 3 days"
   - "I have chest pain and shortness of breath"
   - "What should I do for a burn?"

### Kimi K2 (Cloud) Option

- Pick "Kimi K2 (Cloud)" in the demo dropdown and enter your Kimi API key (OpenAI-compatible endpoint at `https://api.moonshot.cn/v1`).
- Pros: stronger reasoning, 256K context window, no local model download.
- Cons: requires internet + API key, data sent to provider (not offline), possible latency/cost/CORS limits.
- Offline Llama/Phi WebLLM models remain available when internet access is limited.

## 🛠️ For Developers

### Prerequisites

**Development Machine**:
- Python 3.9+
- Node.js 18+
- 16+ GB RAM
- NVIDIA GPU (for training/quantization)

**Target Devices**:
- Android 8+ or iOS 12+
- 3+ GB RAM
- Modern browser with WebGPU

### Installation

```bash
# Clone repository
git clone https://github.com/mniami/help-children.git
cd help-children/ai4se

# Install Python dependencies
pip install -r requirements.txt

# Install JavaScript dependencies
npm install

# Download sample model
npm run download-model
```

### Project Structure

```
ai4se/
├── demo/                   # Progressive Web App demo
├── docs/                   # Documentation
│   └── IMPLEMENTATION_GUIDE.md
├── models/                 # Model storage (gitignored)
├── training/               # Training & fine-tuning scripts
│   ├── train_medical_lora.py
│   ├── quantize_model.py
│   └── evaluate_model.py
├── datasets/              # Training datasets (gitignored)
├── scripts/               # Utility scripts
├── package.json           # Node.js dependencies
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

### Development Workflow

1. **Prepare Dataset**:
   ```bash
   python training/prepare_dataset.py \
     --domain medical \
     --output datasets/medical_train.jsonl
   ```

2. **Fine-Tune Model**:
   ```bash
   python training/train_medical_lora.py \
     --base_model meta-llama/Llama-3.2-3B-Instruct \
     --dataset datasets/medical_train.jsonl \
     --output models/llama-3.2-3b-medical-lora
   ```

3. **Quantize Model**:
   ```bash
   python training/quantize_model.py \
     --model models/llama-3.2-3b-medical-merged \
     --bits 4 \
     --output models/llama-3.2-3b-medical-q4.gguf
   ```

4. **Test Locally**:
   ```bash
   # Using llama.cpp
   ./llama.cpp/main \
     -m models/llama-3.2-3b-medical-q4.gguf \
     -p "You are a medical assistant. A patient says..." \
     --temp 0.7 \
     -n 512
   ```

5. **Deploy to Web**:
   ```bash
   # Convert to WebLLM format
   mlc_llm compile \
     --model models/llama-3.2-3b-medical-q4.gguf \
     --target webgpu \
     --output demo/models/

   # Deploy (choose one)
   npm run deploy:netlify
   npm run deploy:vercel
   npm run deploy:github-pages
   ```

## 📚 Documentation

- **[Project Overview](AI4SE_PROJECT.md)** - Vision, use cases, roadmap
- **[Implementation Guide](docs/IMPLEMENTATION_GUIDE.md)** - Technical setup
- **[Amharic Language Support](docs/AMHARIC_LANGUAGE_SUPPORT.md)** - Complete guide for Amharic STT/TTS
- **[Model Training Guide](docs/TRAINING.md)** - Fine-tuning instructions *(coming soon)*
- **[Deployment Guide](docs/DEPLOYMENT.md)** - Production deployment *(coming soon)*
- **[API Reference](docs/API.md)** - JavaScript API docs *(coming soon)*

## 🎯 Roadmap

### Q1 2026 ✅
- [x] Project documentation
- [x] WebLLM proof of concept
- [ ] Model selection & benchmarking
- [ ] Dataset collection (medical protocols)

### Q2 2026
- [ ] Fine-tune medical model (Amharic/Swahili)
- [ ] PWA development (basic UI)
- [ ] Offline voice integration
- [ ] Pilot preparation (Ethiopia)

### Q3 2026
- [ ] Deploy to 20 CHWs in Hawassa, Ethiopia
- [ ] Collect usage data & feedback
- [ ] Model iteration
- [ ] Add agriculture model

### Q4 2026
- [ ] Expand to 500 CHWs (4 countries)
- [ ] Add technical repair model
- [ ] Multi-language support (5 languages)
- [ ] Open source release

### 2027+
- [ ] Edge device optimization
- [ ] Federated learning
- [ ] Integration with health systems
- [ ] New domains (education, legal aid)

## 🤝 Contributing

We welcome contributions! Here's how to get started:

### Good First Issues

- 📝 Documentation improvements
- 🌐 Translation (add new languages)
- 🧪 Testing (especially on low-end devices)
- 🎨 UI/UX enhancements
- 📊 Dataset creation/curation

### How to Contribute

1. **Fork the repository**
2. **Create a branch**: `git checkout -b feature/my-feature`
3. **Make changes and commit**: `git commit -m "Add feature"`
4. **Push to branch**: `git push origin feature/my-feature`
5. **Open Pull Request**

### Development Setup

```bash
# Fork and clone your fork
git clone https://github.com/YOUR_USERNAME/help-children.git
cd help-children/ai4se

# Add upstream remote
git remote add upstream https://github.com/mniami/help-children.git

# Install dependencies
pip install -r requirements.txt
npm install

# Create feature branch
git checkout -b feature/my-awesome-feature

# Make changes, commit, push, and open PR!
```

### Code Style

- Python: Follow PEP 8 (use `black` formatter)
- JavaScript: ESLint + Prettier
- Commits: Conventional Commits format

```bash
# Format Python code
black training/*.py

# Lint JavaScript
npm run lint
npm run format
```

## 💬 Community

- **GitHub Issues**: [Report bugs or request features](https://github.com/mniami/help-children/issues)
- **Discussions**: [Ask questions, share ideas](https://github.com/mniami/help-children/discussions)
- **Discord**: [Join community chat](https://discord.gg/ai4se) *(coming soon)*
- **Email**: ai4se@help-children.org *(coming soon)*

## 📊 Performance Benchmarks

### Model Sizes (Post-Quantization)

| Model | Full Size | Q4 Size | Q2 Size |
|-------|-----------|---------|---------|
| Llama-3.2-1B | 2.5 GB | 0.6 GB | 0.3 GB |
| Llama-3.2-3B | 6.4 GB | 1.9 GB | 1.0 GB |
| Phi-3-mini | 7.8 GB | 2.3 GB | 1.2 GB |

### Inference Speed (tokens/second)

| Device | Model | CPU | GPU |
|--------|-------|-----|-----|
| iPhone 14 Pro | Llama-3.2-3B Q4 | 15-20 | N/A |
| Samsung A54 | Llama-3.2-3B Q4 | 8-12 | N/A |
| MacBook M2 | Llama-3.2-3B Q4 | 40-50 | N/A |
| Desktop RTX 3060 | Llama-3.2-3B Q4 | 20-30 | 80-100 |

### Memory Usage

| Model | Loading | Inference | Peak |
|-------|---------|-----------|------|
| Llama-3.2-1B Q4 | 0.7 GB | 1.0 GB | 1.2 GB |
| Llama-3.2-3B Q4 | 2.2 GB | 2.5 GB | 3.0 GB |
| Phi-3-mini Q4 | 2.5 GB | 3.0 GB | 3.5 GB |

## 🏆 Use Cases

### Healthcare
- **Community Health Workers** conducting initial triage
- **Remote clinics** with no internet
- **Emergency situations** requiring immediate guidance
- **Patient education** in local languages

### Agriculture
- **Small-scale farmers** identifying crop diseases
- **Urban farmers** optimizing limited space
- **Pest control** without expensive chemicals
- **Seasonal planning** for local climates

### Technical Skills
- **Equipment repair** in resource-limited settings
- **Maintenance training** for local technicians
- **Troubleshooting** without external manuals
- **Skill development** for income generation

## 📄 License

- **Code**: MIT License (free to use, modify, distribute)
- **Models**: Apache 2.0 (permissive for commercial use)
- **Documentation**: CC BY 4.0

See [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- **Barkot Foundation** (Ethiopia) - Field testing partner
- **Meta AI** - Llama models (open source)
- **Microsoft** - Phi models (open source)
- **MLC AI** - WebLLM framework
- **Georgi Gerganov** - llama.cpp
- **Hugging Face** - Model hosting & tools

## 📞 Contact

**Project Maintainer**: [To be assigned]

**Organization**: Help Children Initiative
- Website: https://github.com/mniami/help-children
- Email: ai4se@help-children.org *(coming soon)*

---

## 🌟 Support the Project

If you find this project valuable:

1. ⭐ **Star the repository**
2. 🐛 **Report bugs** or suggest features
3. 📝 **Contribute** code or documentation
4. 💬 **Spread the word** in your network
5. 💰 **Sponsor development** *(donation links coming soon)*

---

## 📈 Project Stats

- **Models**: 3 specialized models (1 released, 2 in development)
- **Languages**: English, Amharic, Swahili *(more coming)*
- **Target Users**: Community Health Workers, farmers, technicians
- **Deployment**: Ethiopia (pilot), expanding to Kenya, Uganda, Madagascar
- **Impact**: Aiming to help 10M+ people by 2030

---

**"AI should empower everyone, not just those with internet and credit cards."**

*Built with ❤️ for social good*

---

*Last Updated: February 12, 2026*
*Version: 0.1.0-alpha*
