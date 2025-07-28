import React, { useState, useEffect } from "react";
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ScriptGenerator = () => {
  const [prompt, setPrompt] = useState("");
  const [videoType, setVideoType] = useState("general");
  const [duration, setDuration] = useState("short");
  const [enhancedPrompt, setEnhancedPrompt] = useState("");
  const [enhancementExplanation, setEnhancementExplanation] = useState("");
  const [generatedScript, setGeneratedScript] = useState("");
  const [generatedWithPrompt, setGeneratedWithPrompt] = useState(""); // Track which prompt was used
  const [isEnhancing, setIsEnhancing] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [showEnhanced, setShowEnhanced] = useState(false);
  const [error, setError] = useState("");
  const [scripts, setScripts] = useState([]);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentUtterance, setCurrentUtterance] = useState(null);

  const fetchScripts = async () => {
    try {
      const response = await axios.get(`${API}/scripts`);
      setScripts(response.data.slice(0, 5)); // Show only latest 5
    } catch (err) {
      console.error("Error fetching scripts:", err);
    }
  };

  useEffect(() => {
    fetchScripts();
  }, []);

  const handleEnhancePrompt = async () => {
    if (!prompt.trim()) {
      setError("Please enter a prompt first");
      return;
    }

    setIsEnhancing(true);
    setError("");

    try {
      const response = await axios.post(`${API}/enhance-prompt`, {
        original_prompt: prompt,
        video_type: videoType
      });

      setEnhancedPrompt(response.data.enhanced_prompt);
      setEnhancementExplanation(response.data.enhancement_explanation);
      setShowEnhanced(true);
    } catch (err) {
      setError("Error enhancing prompt. Please try again.");
      console.error("Error enhancing prompt:", err);
    } finally {
      setIsEnhancing(false);
    }
  };

  const handleGenerateScript = async (useEnhanced = false) => {
    const finalPrompt = useEnhanced ? enhancedPrompt : prompt;
    const promptType = useEnhanced ? "enhanced" : "original";
    
    if (!finalPrompt.trim()) {
      setError("Please enter a prompt first");
      return;
    }

    setIsGenerating(true);
    setError("");

    try {
      const response = await axios.post(`${API}/generate-script`, {
        prompt: finalPrompt,
        video_type: videoType,
        duration: duration
      });

      setGeneratedScript(response.data.generated_script);
      setGeneratedWithPrompt(promptType);
      fetchScripts(); // Refresh the scripts list
    } catch (err) {
      setError("Error generating script. Please try again.");
      console.error("Error generating script:", err);
    } finally {
      setIsGenerating(false);
    }
  };

  const handlePlayScript = () => {
    if ('speechSynthesis' in window) {
      if (isPlaying) {
        // Stop current playback
        window.speechSynthesis.cancel();
        setIsPlaying(false);
        setCurrentUtterance(null);
        return;
      }

      // Clean the script text for better speech synthesis
      const cleanText = generatedScript
        .replace(/\[([^\]]+)\]/g, '') // Remove scene descriptions
        .replace(/\(([^)]+)\)/g, '') // Remove speaker directions
        .replace(/\*\*([^*]+)\*\*/g, '$1') // Remove bold formatting
        .replace(/\n+/g, ' ') // Replace line breaks with spaces
        .replace(/\s+/g, ' ') // Replace multiple spaces with single space
        .trim();

      const utterance = new SpeechSynthesisUtterance(cleanText);
      
      // Configure speech settings
      utterance.rate = 0.9; // Slightly slower for better comprehension
      utterance.pitch = 1.0;
      utterance.volume = 1.0;

      // Event handlers
      utterance.onstart = () => {
        setIsPlaying(true);
      };

      utterance.onend = () => {
        setIsPlaying(false);
        setCurrentUtterance(null);
      };

      utterance.onerror = (event) => {
        console.error('Speech synthesis error:', event);
        setIsPlaying(false);
        setCurrentUtterance(null);
        setError("Error playing audio. Please try again.");
      };

      setCurrentUtterance(utterance);
      window.speechSynthesis.speak(utterance);
    } else {
      setError("Text-to-speech is not supported in your browser.");
    }
  };

  const formatScript = (script) => {
    return script
      .replace(/\[([^\]]+)\]/g, '<span class="text-blue-600 font-medium">[$1]</span>')
      .replace(/\(([^)]+)\)/g, '<span class="text-green-600 italic">($1)</span>')
      .replace(/\*\*([^*]+)\*\*/g, '<strong class="font-bold">$1</strong>')
      .replace(/\n/g, '<br/>');
  };

  const formatEnhancedPrompt = (text) => {
    return text
      .replace(/\n\n/g, '<br/><br/>') // Double line breaks for paragraphs
      .replace(/\n/g, '<br/>') // Single line breaks
      .replace(/\*\*([^*]+)\*\*/g, '<strong class="font-bold">$1</strong>'); // Bold text
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-white mb-4 bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
            🎬 AI Script Generator
          </h1>
          <p className="text-xl text-gray-300 max-w-2xl mx-auto">
            Create emotionally compelling, highly engaging video scripts that keep viewers hooked from start to finish
          </p>
        </div>

        <div className="grid lg:grid-cols-2 gap-8">
          {/* Left Column - Input Form */}
          <div className="space-y-6">
            <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
              <h2 className="text-2xl font-bold text-white mb-6">Create Your Script</h2>
              
              {/* Prompt Input */}
              <div className="mb-6">
                <label className="block text-white font-medium mb-2">
                  Your Video Idea
                </label>
                <textarea
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  placeholder="Describe your video idea... (e.g., 'A motivational video about overcoming fear')"
                  className="w-full h-32 px-4 py-3 bg-white/5 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
                />
              </div>

              {/* Video Type and Duration */}
              <div className="grid md:grid-cols-2 gap-4 mb-6">
                <div>
                  <label className="block text-white font-medium mb-2">Video Type</label>
                  <select
                    value={videoType}
                    onChange={(e) => setVideoType(e.target.value)}
                    className="w-full px-4 py-3 bg-white/5 border border-white/20 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                  >
                    <option value="general">General</option>
                    <option value="educational">Educational</option>
                    <option value="entertainment">Entertainment</option>
                    <option value="marketing">Marketing</option>
                  </select>
                </div>
                <div>
                  <label className="block text-white font-medium mb-2">Duration</label>
                  <select
                    value={duration}
                    onChange={(e) => setDuration(e.target.value)}
                    className="w-full px-4 py-3 bg-white/5 border border-white/20 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                  >
                    <option value="short">Short (30s-1min)</option>
                    <option value="medium">Medium (1-3min)</option>
                    <option value="long">Long (3-5min)</option>
                  </select>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="space-y-3">
                <button
                  onClick={handleEnhancePrompt}
                  disabled={isEnhancing || !prompt.trim()}
                  className="w-full py-3 px-6 bg-gradient-to-r from-yellow-500 to-orange-500 text-white font-semibold rounded-lg shadow-lg hover:from-yellow-600 hover:to-orange-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 transform hover:scale-105"
                >
                  {isEnhancing ? (
                    <div className="flex items-center justify-center">
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                      Enhancing Prompt...
                    </div>
                  ) : (
                    "✨ Enhance Prompt"
                  )}
                </button>

                {!showEnhanced && (
                  <button
                    onClick={() => handleGenerateScript(false)}
                    disabled={isGenerating || !prompt.trim()}
                    className="w-full py-3 px-6 bg-gradient-to-r from-purple-600 to-blue-600 text-white font-semibold rounded-lg shadow-lg hover:from-purple-700 hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 transform hover:scale-105"
                  >
                    {isGenerating ? (
                      <div className="flex items-center justify-center">
                        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                        Generating Script...
                      </div>
                    ) : (
                      "🎬 Generate Script"
                    )}
                  </button>
                )}
              </div>

              {error && (
                <div className="mt-4 p-3 bg-red-500/20 border border-red-500/50 rounded-lg text-red-200">
                  {error}
                </div>
              )}
            </div>

            {/* Enhanced Prompt Display */}
            {showEnhanced && enhancedPrompt && (
              <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
                <h3 className="text-xl font-bold text-white mb-4">✨ Enhanced Prompt</h3>
                
                <div className="mb-4">
                  <h4 className="text-sm font-medium text-gray-300 mb-2">Original:</h4>
                  <p className="text-gray-400 bg-white/5 p-3 rounded-lg">{prompt}</p>
                </div>
                
                <div className="mb-6">
                  <h4 className="text-sm font-medium text-gray-300 mb-2">Enhanced:</h4>
                  <div 
                    className="text-white bg-white/5 p-3 rounded-lg leading-relaxed"
                    dangerouslySetInnerHTML={{ __html: formatEnhancedPrompt(enhancedPrompt) }}
                  />
                </div>
                
                {enhancementExplanation && (
                  <div className="mb-6">
                    <h4 className="text-sm font-medium text-gray-300 mb-2">Why this is better:</h4>
                    <div 
                      className="text-gray-300 bg-white/5 p-3 rounded-lg text-sm leading-relaxed"
                      dangerouslySetInnerHTML={{ __html: formatEnhancedPrompt(enhancementExplanation) }}
                    />
                  </div>
                )}

                {/* Dual Script Generation Buttons */}
                <div className="grid grid-cols-2 gap-3">
                  <button
                    onClick={() => handleGenerateScript(false)}
                    disabled={isGenerating}
                    className="py-3 px-4 bg-gradient-to-r from-gray-600 to-gray-700 text-white font-semibold rounded-lg shadow-lg hover:from-gray-700 hover:to-gray-800 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 transform hover:scale-105 text-sm"
                  >
                    {isGenerating ? (
                      <div className="flex items-center justify-center">
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                        Generating...
                      </div>
                    ) : (
                      "🎬 Generate with Original"
                    )}
                  </button>
                  
                  <button
                    onClick={() => handleGenerateScript(true)}
                    disabled={isGenerating}
                    className="py-3 px-4 bg-gradient-to-r from-purple-600 to-blue-600 text-white font-semibold rounded-lg shadow-lg hover:from-purple-700 hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 transform hover:scale-105 text-sm"
                  >
                    {isGenerating ? (
                      <div className="flex items-center justify-center">
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                        Generating...
                      </div>
                    ) : (
                      "✨ Generate with Enhanced"
                    )}
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* Right Column - Generated Script */}
          <div className="space-y-6">
            {generatedScript && (
              <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
                <div className="flex justify-between items-center mb-6">
                  <h2 className="text-2xl font-bold text-white">
                    🎬 Generated Script 
                    <span className="text-sm font-normal text-gray-300 ml-2">
                      ({generatedWithPrompt} prompt)
                    </span>
                  </h2>
                  <button
                    onClick={handlePlayScript}
                    className={`px-4 py-2 rounded-lg font-medium transition-all duration-200 flex items-center space-x-2 ${
                      isPlaying 
                        ? 'bg-red-500/20 text-red-300 hover:bg-red-500/30' 
                        : 'bg-green-500/20 text-green-300 hover:bg-green-500/30'
                    }`}
                  >
                    <span>{isPlaying ? '⏹️' : '🎵'}</span>
                    <span>{isPlaying ? 'Stop' : 'Listen'}</span>
                  </button>
                </div>
                
                <div 
                  className="text-gray-200 leading-relaxed bg-white/5 p-4 rounded-lg max-h-96 overflow-y-auto"
                  dangerouslySetInnerHTML={{ __html: formatScript(generatedScript) }}
                />
                
                <div className="mt-4 pt-4 border-t border-white/20 flex space-x-3">
                  <button
                    onClick={() => navigator.clipboard.writeText(generatedScript)}
                    className="px-4 py-2 bg-white/10 text-white rounded-lg hover:bg-white/20 transition-colors"
                  >
                    📋 Copy Script
                  </button>
                  
                  {!isPlaying && (
                    <div className="text-xs text-gray-400 flex items-center">
                      💡 Click "Listen" to hear your script read aloud
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Recent Scripts */}
            {scripts.length > 0 && (
              <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
                <h3 className="text-xl font-bold text-white mb-4">📚 Recent Scripts</h3>
                <div className="space-y-3 max-h-80 overflow-y-auto">
                  {scripts.map((script) => (
                    <div key={script.id} className="bg-white/5 p-4 rounded-lg border border-white/10 hover:bg-white/10 transition-colors cursor-pointer"
                         onClick={() => {
                           setGeneratedScript(script.generated_script);
                           setGeneratedWithPrompt("saved");
                         }}>
                      <p className="text-gray-300 text-sm mb-2 line-clamp-2">{script.original_prompt}</p>
                      <div className="flex justify-between items-center text-xs text-gray-400">
                        <span>{script.video_type} • {script.duration}</span>
                        <span>{new Date(script.created_at).toLocaleDateString()}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

function App() {
  return (
    <div className="App">
      <ScriptGenerator />
    </div>
  );
}

export default App;