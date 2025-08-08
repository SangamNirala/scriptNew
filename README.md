# AI-Powered Video Script Generator

A comprehensive, full-stack application that transforms ideas into professional video scripts using advanced AI techniques, with integrated voice generation and avatar video creation capabilities.

## 🚀 Key Features

### 🎯 **AI Script Generation**
- **Advanced Prompting**: Multi-strategy script generation with emotional, technical, and viral optimization
- **Chain-of-Thought Processing**: Sophisticated reasoning chains for enhanced script quality
- **Industry-Specific Optimization**: Tailored content for marketing, education, entertainment, tech, health, and finance
- **Platform Optimization**: Content optimized for YouTube, TikTok, Instagram, LinkedIn

### ✨ **Enhanced Prompt Engineering**
- **Multi-Variation Enhancement**: Generate 3 optimized versions of any prompt
- **Context Integration**: Real-time trend analysis and competitive intelligence
- **Quality Metrics**: AI-powered scoring and improvement suggestions
- **Recursive Optimization**: Self-improving prompts through multiple refinement loops

### 🎙️ **Voice & Audio Generation**
- **Edge-TTS Integration**: High-quality text-to-speech with 8 professional voices
- **Multi-Language Support**: English variants (US, UK, Australian, Canadian)
- **Gender Variety**: Male and female voice options
- **Audio Processing**: Clean script parsing and professional audio output

### 🎬 **Avatar Video Generation**
- **3 Avatar Types**: Basic, Enhanced, and Ultra-Realistic avatar videos
- **Custom Avatars**: Upload your own photos or use AI-generated avatars
- **Dynamic Backgrounds**: Context-aware background generation
- **Professional Output**: High-quality MP4 videos with synchronized audio

### 📊 **Advanced Analytics & Quality Assurance**
- **Multi-Model Validation**: Consensus scoring across multiple AI models
- **Quality Improvement Loops**: Automatic script refinement until quality thresholds are met
- **Performance Tracking**: Historical analysis and optimization insights
- **A/B Testing**: Systematic prompt optimization and performance comparison

## 🛠️ Technology Stack

### **Backend**
- **FastAPI** - High-performance Python web framework
- **MongoDB** - NoSQL database for data persistence
- **Gemini AI** - Google's advanced language model for script generation
- **Edge-TTS** - Microsoft's text-to-speech engine
- **OpenCV** - Computer vision for avatar processing
- **Various AI Libraries** - spaCy, scikit-learn, transformers for advanced processing

### **Frontend**
- **React 19** - Modern JavaScript framework
- **Tailwind CSS** - Utility-first CSS framework
- **Axios** - HTTP client for API communication
- **Modern UI/UX** - Glass morphism effects and responsive design

### **Infrastructure**
- **Docker/Kubernetes** - Containerized deployment
- **Supervisor** - Process management
- **CORS Support** - Cross-origin resource sharing
- **Environment-based Configuration** - Secure API key management

## 📋 Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **MongoDB**
- **API Keys:**
  - Gemini API Key (Google AI Studio)
  - Optional: SERP API Key for trend analysis

## ⚡ Quick Start

### 1. **Clone and Setup**
```bash
# Clone the repository
git clone <repository-url>
cd <project-directory>

# Backend setup
cd backend
pip install -r requirements.txt
pip install emergentintegrations --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/
python -m spacy download en_core_web_sm

# Frontend setup
cd ../frontend
yarn install
```

### 2. **Environment Configuration**
```bash
# Backend environment (.env)
GEMINI_API_KEY=your_gemini_api_key_here
MONGO_URL=mongodb://localhost:27017
DB_NAME=video_script_db

# Frontend environment (.env)
REACT_APP_BACKEND_URL=http://localhost:8001
```

### 3. **Start Services**
```bash
# Start MongoDB
sudo systemctl start mongodb

# Start backend
cd backend
uvicorn server:app --host 0.0.0.0 --port 8001 --reload

# Start frontend
cd frontend
yarn start
```

## 🎯 Usage Guide

### **Basic Script Generation**
1. Enter your video idea in the text area
2. Select video type (General, Educational, Entertainment, Marketing)
3. Choose duration (Short, Medium, Long)
4. Click "Generate Script" for AI-powered content

### **Enhanced Prompts**
1. Click "✨ Enhance Prompt" for advanced optimization
2. Review 3 enhancement variations:
   - **Emotional Focus**: Psychology-driven engagement
   - **Technical Focus**: Professional framework architecture
   - **Viral Focus**: Algorithm-optimized shareability
3. Generate scripts using any enhanced version

### **Voice & Audio**
1. After generating a script, click "Listen"
2. Choose from 8 professional voices
3. Generate high-quality audio output
4. Download or play directly in browser

### **Avatar Videos**
1. Generate script and audio first
2. Choose avatar type:
   - **Basic**: Simple lip-sync animation
   - **Enhanced**: Custom avatar options
   - **Ultra-Realistic**: Professional-grade avatar videos
3. Download final video with synchronized audio

## 🔧 API Endpoints

### **Core Endpoints**
- `GET /api/` - Health check
- `POST /api/generate-script` - Generate video scripts
- `POST /api/enhance-prompt` - Enhanced prompt optimization
- `GET /api/voices` - Available TTS voices
- `POST /api/generate-audio` - Text-to-speech conversion

### **Advanced Features**
- `POST /api/generate-script-cot` - Chain-of-thought script generation
- `POST /api/generate-avatar-video` - Basic avatar video creation
- `POST /api/generate-enhanced-avatar-video` - Enhanced avatar videos
- `POST /api/multi-model-validation` - Quality assurance
- `POST /api/quality-improvement-loop` - Automatic optimization

### **Data Management**
- `GET /api/scripts` - Retrieve script history
- `PUT /api/scripts/{id}` - Update existing scripts
- `POST /api/pattern-analysis` - Content pattern analysis

## 🎨 Features in Detail

### **Chain-of-Thought Processing**
Advanced reasoning system that breaks down script generation into logical steps:
1. **Analysis & Understanding** - Deep prompt comprehension
2. **Audience & Context Mapping** - Target demographic analysis
3. **Narrative Architecture** - Story structure design
4. **Engagement Strategy** - Psychological trigger placement
5. **Content Development** - Full script creation
6. **Quality Validation** - Final refinement and optimization

### **Multi-Model Validation**
Quality assurance through consensus scoring:
- Multiple AI models evaluate each script
- Consensus-based quality scoring
- Automatic regeneration for low-quality outputs
- Confidence metrics and improvement suggestions

### **Context Integration System**
Real-time enhancement through:
- **Trend Analysis** - Current market trends and viral topics
- **Platform Optimization** - Algorithm-specific adaptations
- **Competitor Analysis** - Competitive intelligence integration
- **Audience Psychology** - Behavioral pattern analysis
- **Seasonal Relevance** - Time-sensitive content optimization

## 🔒 Security & Configuration

### **Environment Variables**
All sensitive data is managed through environment variables:
- API keys are never hardcoded
- Database connections are configurable
- Cross-origin policies are properly configured

### **CORS Configuration**
Properly configured for secure cross-origin requests between frontend and backend.

## 🚀 Deployment

The application is designed for containerized deployment with:
- Docker support for consistent environments
- Kubernetes orchestration for scalability
- Supervisor for process management
- Environment-based configuration for different deployment stages

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support & Troubleshooting

### **Common Issues**
- **Service not starting**: Check dependencies installation
- **API errors**: Verify API keys in environment variables
- **Voice generation issues**: Ensure Edge-TTS is properly installed
- **Frontend build issues**: Clear node_modules and reinstall

### **Getting Help**
- Check the logs in `/var/log/supervisor/` for detailed error information
- Verify all environment variables are properly set
- Ensure all dependencies are installed according to requirements.txt

---

**Built with ❤️ using cutting-edge AI technology to democratize professional video content creation.**
