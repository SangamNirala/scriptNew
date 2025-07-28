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
  
  // Voice selection state
  const [voices, setVoices] = useState([]);
  const [selectedVoice, setSelectedVoice] = useState(null);
  const [showVoiceSelection, setShowVoiceSelection] = useState(false);
  const [isGeneratingAudio, setIsGeneratingAudio] = useState(false);
  const [audioData, setAudioData] = useState(null);
  
  // Avatar video state
  const [isGeneratingVideo, setIsGeneratingVideo] = useState(false);
  const [avatarVideoData, setAvatarVideoData] = useState(null);
  const [lastGeneratedAudio, setLastGeneratedAudio] = useState(null);

  const fetchScripts = async () => {
    try {
      const response = await axios.get(`${API}/scripts`);
      setScripts(response.data.slice(0, 5)); // Show only latest 5
    } catch (err) {
      console.error("Error fetching scripts:", err);
    }
  };

  const fetchVoices = async () => {
    try {
      const response = await axios.get(`${API}/voices`);
      setVoices(response.data);
      // Set default voice to the first female voice (usually Aria)
      if (response.data.length > 0) {
        const defaultVoice = response.data.find(v => v.gender === 'Female') || response.data[0];
        setSelectedVoice(defaultVoice);
      }
    } catch (err) {
      console.error("Error fetching voices:", err);
      setError("Error loading voices. Please refresh the page.");
    }
  };

  useEffect(() => {
    fetchScripts();
    fetchVoices();
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
    if (isPlaying) {
      // Stop current playback
      if (audioData) {
        audioData.pause();
        audioData.currentTime = 0;
      }
      setIsPlaying(false);
      setAudioData(null);
      return;
    }

    // Show voice selection modal
    setShowVoiceSelection(true);
  };

  const handleVoiceSelect = (voice) => {
    setSelectedVoice(voice);
  };

  const handleGenerateAndPlayAudio = async () => {
    if (!selectedVoice || !generatedScript) {
      setError("Please select a voice and ensure you have a script to read.");
      return;
    }

    setIsGeneratingAudio(true);
    setShowVoiceSelection(false);
    setError("");

    try {
      const response = await axios.post(`${API}/generate-audio`, {
        text: generatedScript,
        voice_name: selectedVoice.name
      });

      // Convert base64 to audio blob and play
      const audioBase64 = response.data.audio_base64;
      const audioBytes = atob(audioBase64);
      const audioArray = new Uint8Array(audioBytes.length);
      
      for (let i = 0; i < audioBytes.length; i++) {
        audioArray[i] = audioBytes.charCodeAt(i);
      }
      
      const audioBlob = new Blob([audioArray], { type: 'audio/mp3' });
      const audioUrl = URL.createObjectURL(audioBlob);
      const audio = new Audio(audioUrl);
      
      audio.onloadstart = () => {
        setIsPlaying(true);
      };
      
      audio.onended = () => {
        setIsPlaying(false);
        setAudioData(null);
        URL.revokeObjectURL(audioUrl);
      };
      
      audio.onerror = (e) => {
        console.error('Audio playback error:', e);
        setIsPlaying(false);
        setAudioData(null);
        setError("Error playing audio. Please try again.");
        URL.revokeObjectURL(audioUrl);
      };
      
      setAudioData(audio);
      setLastGeneratedAudio(audioBase64); // Store for avatar video generation
      audio.play();
      
    } catch (err) {
      console.error("Error generating audio:", err);
      setError("Error generating audio. Please try again.");
    } finally {
      setIsGeneratingAudio(false);
    }
  };

  const handleGenerateAvatarVideo = async () => {
    if (!lastGeneratedAudio) {
      setError("Please generate audio first before creating avatar video.");
      return;
    }

    setIsGeneratingVideo(true);
    setError("");

    try {
      const response = await axios.post(`${API}/generate-avatar-video`, {
        audio_base64: lastGeneratedAudio
      });

      // Convert base64 video to blob for download
      const videoBase64 = response.data.video_base64;
      const videoBytes = atob(videoBase64);
      const videoArray = new Uint8Array(videoBytes.length);
      
      for (let i = 0; i < videoBytes.length; i++) {
        videoArray[i] = videoBytes.charCodeAt(i);
      }
      
      const videoBlob = new Blob([videoArray], { type: 'video/mp4' });
      const videoUrl = URL.createObjectURL(videoBlob);
      
      setAvatarVideoData({
        url: videoUrl,
        blob: videoBlob,
        duration: response.data.duration_seconds,
        requestId: response.data.request_id
      });
      
    } catch (err) {
      console.error("Error generating avatar video:", err);
      setError("Error generating avatar video. Please try again.");
    } finally {
      setIsGeneratingVideo(false);
    }
  };

  const downloadAvatarVideo = () => {
    if (avatarVideoData) {
      const link = document.createElement('a');
      link.href = avatarVideoData.url;
      link.download = `avatar-video-${avatarVideoData.requestId}.mp4`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
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
                    disabled={isGeneratingAudio}
                    className={`px-4 py-2 rounded-lg font-medium transition-all duration-200 flex items-center space-x-2 ${
                      isPlaying 
                        ? 'bg-red-500/20 text-red-300 hover:bg-red-500/30' 
                        : isGeneratingAudio
                        ? 'bg-yellow-500/20 text-yellow-300'
                        : 'bg-green-500/20 text-green-300 hover:bg-green-500/30'
                    } ${isGeneratingAudio ? 'cursor-not-allowed opacity-75' : ''}`}
                  >
                    {isGeneratingAudio ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-yellow-300"></div>
                        <span>Generating...</span>
                      </>
                    ) : (
                      <>
                        <span>{isPlaying ? '⏹️' : '🎵'}</span>
                        <span>{isPlaying ? 'Stop' : 'Listen'}</span>
                      </>
                    )}
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
                  
                  {lastGeneratedAudio && (
                    <button
                      onClick={handleGenerateAvatarVideo}
                      disabled={isGeneratingVideo}
                      className={`px-4 py-2 rounded-lg font-medium transition-all duration-200 flex items-center space-x-2 ${
                        isGeneratingVideo 
                          ? 'bg-yellow-500/20 text-yellow-300 cursor-not-allowed' 
                          : 'bg-gradient-to-r from-green-600 to-teal-600 text-white hover:from-green-700 hover:to-teal-700'
                      }`}
                    >
                      {isGeneratingVideo ? (
                        <>
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-yellow-300"></div>
                          <span>Creating Video...</span>
                        </>
                      ) : (
                        <>
                          <span>🎥</span>
                          <span>Generate Avatar Video</span>
                        </>
                      )}
                    </button>
                  )}
                  
                  {!isPlaying && !isGeneratingAudio && !lastGeneratedAudio && (
                    <div className="text-xs text-gray-400 flex items-center">
                      💡 Click "Listen" to choose a voice and hear your script read aloud
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Avatar Video Display */}
            {avatarVideoData && (
              <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
                <div className="flex justify-between items-center mb-6">
                  <h2 className="text-2xl font-bold text-white">
                    🎥 Generated Avatar Video
                  </h2>
                  <button
                    onClick={downloadAvatarVideo}
                    className="px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold rounded-lg shadow-lg hover:from-blue-700 hover:to-purple-700 transition-all duration-200 flex items-center space-x-2"
                  >
                    <span>📥</span>
                    <span>Download Video</span>
                  </button>
                </div>
                
                <div className="bg-white/5 p-4 rounded-lg">
                  <video 
                    src={avatarVideoData.url} 
                    controls 
                    className="w-full max-w-md mx-auto rounded-lg"
                    style={{ maxHeight: '400px' }}
                  >
                    Your browser does not support the video tag.
                  </video>
                  
                  <div className="mt-4 text-center">
                    <p className="text-gray-300 text-sm">
                      Duration: {Math.round(avatarVideoData.duration || 0)}s | 
                      Ready for video integration
                    </p>
                    <p className="text-xs text-gray-400 mt-2">
                      💡 This avatar video contains only the essential narration from your script, 
                      perfectly synchronized with lip movements for professional video content.
                    </p>
                  </div>
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

        {/* Voice Selection Modal */}
        {showVoiceSelection && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20 max-w-md w-full max-h-[80vh] overflow-y-auto">
              <h3 className="text-2xl font-bold text-white mb-4">🎤 Choose Voice</h3>
              
              <div className="space-y-3 mb-6">
                {voices.map((voice) => (
                  <button
                    key={voice.name}
                    onClick={() => handleVoiceSelect(voice)}
                    className={`w-full p-3 rounded-lg text-left transition-all duration-200 ${
                      selectedVoice?.name === voice.name
                        ? 'bg-purple-500/30 border-purple-400 border-2 text-white'
                        : 'bg-white/5 border border-white/20 text-gray-300 hover:bg-white/10'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="font-medium">{voice.display_name}</div>
                        <div className="text-sm text-gray-400">{voice.language}</div>
                      </div>
                      <div className={`px-2 py-1 rounded text-xs ${
                        voice.gender === 'Female' 
                          ? 'bg-pink-500/20 text-pink-300' 
                          : 'bg-blue-500/20 text-blue-300'
                      }`}>
                        {voice.gender}
                      </div>
                    </div>
                  </button>
                ))}
              </div>

              <div className="flex space-x-3">
                <button
                  onClick={() => setShowVoiceSelection(false)}
                  className="flex-1 py-3 px-4 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleGenerateAndPlayAudio}
                  disabled={!selectedVoice || isGeneratingAudio}
                  className="flex-1 py-3 px-4 bg-gradient-to-r from-purple-600 to-blue-600 text-white font-semibold rounded-lg shadow-lg hover:from-purple-700 hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
                >
                  {isGeneratingAudio ? (
                    <div className="flex items-center justify-center">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      Generating...
                    </div>
                  ) : (
                    "🎵 Generate Audio"
                  )}
                </button>
              </div>
            </div>
          </div>
        )}
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