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
  const [enhancementVariations, setEnhancementVariations] = useState([]);
  const [enhancementRecommendation, setEnhancementRecommendation] = useState("");
  const [generatedScript, setGeneratedScript] = useState("");
  const [currentScriptId, setCurrentScriptId] = useState(""); // Track current script ID
  const [generatedWithPrompt, setGeneratedWithPrompt] = useState(""); // Track which prompt was used
  const [isEnhancing, setIsEnhancing] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [showEnhanced, setShowEnhanced] = useState(false);
  const [error, setError] = useState("");
  const [scripts, setScripts] = useState([]);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentUtterance, setCurrentUtterance] = useState(null);
  
  // Script editing state
  const [isEditingScript, setIsEditingScript] = useState(false);
  const [editedScript, setEditedScript] = useState("");
  const [isSavingScript, setIsSavingScript] = useState(false);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  
  // Voice selection state
  const [voices, setVoices] = useState([]);
  const [selectedVoice, setSelectedVoice] = useState(null);
  const [showVoiceSelection, setShowVoiceSelection] = useState(false);
  const [isGeneratingAudio, setIsGeneratingAudio] = useState(false);
  const [audioData, setAudioData] = useState(null);

  // AI-optimized script generation state
  const [showAIScriptOptions, setShowAIScriptOptions] = useState(false);
  const [visualStyle, setVisualStyle] = useState("cinematic");
  const [targetPlatform, setTargetPlatform] = useState("general");
  const [mood, setMood] = useState("professional");
  const [isGeneratingAIScript, setIsGeneratingAIScript] = useState(false);
  const [aiScriptData, setAiScriptData] = useState(null);

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
    setShowEnhanced(false);

    try {
      const response = await axios.post(`${API}/enhance-prompt`, {
        prompt: prompt.trim(),
        video_type: videoType,
        industry_focus: "general"
      });

      // Handle the new response structure with multiple variations
      if (response.data.enhancement_variations && Array.isArray(response.data.enhancement_variations)) {
        setEnhancementVariations(response.data.enhancement_variations);
        setEnhancementRecommendation(response.data.recommendation || "");
        setShowEnhanced(true);
      } else {
        // Fallback for old structure
        setEnhancedPrompt(response.data.enhanced_prompt || response.data.prompt || "");
        setEnhancementExplanation(response.data.enhancement_explanation || response.data.explanation || "");
        setShowEnhanced(true);
      }

    } catch (err) {
      console.error("Error enhancing prompt:", err);
      setError("Error enhancing prompt. Please try again.");
    } finally {
      setIsEnhancing(false);
    }
  };

  const handleGenerateScript = async (promptToUse = null, variationIndex = null) => {
    let finalPrompt = promptToUse || prompt.trim();

    if (!finalPrompt) {
      setError("Please enter a prompt first");
      return;
    }

    setIsGenerating(true);
    setError("");
    setGeneratedScript("");

    try {
      const response = await axios.post(`${API}/generate-script`, {
        prompt: finalPrompt,
        video_type: videoType,
        duration: duration
      });

      setGeneratedScript(response.data.generated_script);
      setCurrentScriptId(response.data.id);
      setGeneratedWithPrompt(finalPrompt);
      
      // Update script editing state
      setEditedScript(response.data.generated_script);
      setIsEditingScript(false);
      setHasUnsavedChanges(false);
      
      // Refresh scripts list
      fetchScripts();
    } catch (err) {
      console.error("Error generating script:", err);
      setError("Error generating script. Please try again.");
    } finally {
      setIsGenerating(false);
    }
  };

  const handleSaveScript = async () => {
    if (!currentScriptId || !editedScript.trim()) {
      setError("No script to save or script is empty");
      return;
    }

    setIsSavingScript(true);
    setError("");

    try {
      const response = await axios.put(`${API}/scripts/${currentScriptId}`, {
        generated_script: editedScript.trim()
      });

      setGeneratedScript(editedScript.trim());
      setHasUnsavedChanges(false);
      setIsEditingScript(false);

      // Refresh scripts list
      fetchScripts();
      
      // Show success feedback briefly
      setTimeout(() => {
        setError("");
      }, 3000);

    } catch (err) {
      console.error("Error saving script:", err);
      setError("Error saving script. Please try again.");
    } finally {
      setIsSavingScript(false);
    }
  };

  const handleScriptChange = (newValue) => {
    setEditedScript(newValue);
    setHasUnsavedChanges(newValue !== generatedScript);
  };

  const handleCopyScript = () => {
    const scriptText = isEditingScript ? editedScript : generatedScript;
    navigator.clipboard.writeText(scriptText).then(() => {
      // You could show a brief "Copied!" message here
    }).catch(err => {
      console.error("Error copying script:", err);
    });
  };

  const handleGenerateAudio = async () => {
    if (!selectedVoice) {
      setError("Please select a voice first");
      return;
    }

    const scriptText = isEditingScript ? editedScript : generatedScript;
    if (!scriptText.trim()) {
      setError("Please generate a script first");
      return;
    }

    setIsGeneratingAudio(true);
    setError("");

    try {
      const response = await axios.post(`${API}/generate-audio`, {
        text: scriptText,
        voice: selectedVoice.name,
        voice_display_name: selectedVoice.display_name
      });

      // Create audio blob from base64
      const audioBase64 = response.data.audio_base64;
      const audioBytes = atob(audioBase64);
      const audioArray = new Uint8Array(audioBytes.length);
      
      for (let i = 0; i < audioBytes.length; i++) {
        audioArray[i] = audioBytes.charCodeAt(i);
      }
      
      const audioBlob = new Blob([audioArray], { type: 'audio/mpeg' });
      const audioUrl = URL.createObjectURL(audioBlob);
      
      setAudioData({
        url: audioUrl,
        blob: audioBlob,
        voice: selectedVoice,
        duration: response.data.duration_seconds
      });

      // Store audio data for potential avatar video generation
      // setLastGeneratedAudio(audioBase64); // REMOVED - no longer needed

    } catch (err) {
      console.error("Error generating audio:", err);
      setError("Error generating audio. Please try again.");
    } finally {
      setIsGeneratingAudio(false);
    }
  };

  const downloadAudio = () => {
    if (audioData) {
      const link = document.createElement('a');
      link.href = audioData.url;
      link.download = `script-audio-${selectedVoice?.name || 'audio'}.mp3`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  const formatScript = (script) => {
    return script
      .split('\n')
      .map((line, index) => (
        <div key={index} style={{ marginBottom: '8px' }}>
          {line.split(/(\[.*?\]|\(.*?\)|\*\*.*?\*\*)/).map((part, partIndex) => {
            if (part.startsWith('[') && part.endsWith(']')) {
              return <span key={partIndex} style={{ color: '#10b981', fontStyle: 'italic' }}>{part}</span>;
            } else if (part.startsWith('(') && part.endsWith(')')) {
              return <span key={partIndex} style={{ color: '#f59e0b', fontWeight: 'bold' }}>{part}</span>;
            } else if (part.startsWith('**') && part.endsWith('**')) {
              return <span key={partIndex} style={{ color: '#ef4444', fontWeight: 'bold' }}>{part.slice(2, -2)}</span>;
            }
            return part;
          })}
        </div>
      ));
  };

  const renderEnhancedPrompts = () => {
    if (enhancementVariations && enhancementVariations.length > 0) {
      return (
        <div className="space-y-4">
          {enhancementVariations.map((variation, index) => (
            <div key={index} className="bg-white/5 p-4 rounded-lg border border-white/20">
              <h4 className="text-lg font-semibold text-white mb-2 flex items-center">
                <span className="mr-2">
                  {index === 0 ? "❤️" : index === 1 ? "⚡" : "🚀"}
                </span>
                {variation.focus_strategy}
              </h4>
              <p className="text-gray-300 text-sm mb-3">{variation.enhanced_prompt}</p>
              {variation.performance_score && (
                <div className="text-xs text-gray-400 mb-3">
                  Performance Score: <span className="text-green-400">{variation.performance_score}/10</span>
                </div>
              )}
              <button
                onClick={() => handleGenerateScript(variation.enhanced_prompt, index)}
                disabled={isGenerating}
                className="w-full py-2 px-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold rounded-lg shadow-lg hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
              >
                {isGenerating ? "Generating..." : `Generate with ${variation.focus_strategy} Prompt`}
              </button>
            </div>
          ))}
          
          {enhancementRecommendation && (
            <div className="bg-gradient-to-r from-green-500/20 to-blue-500/20 p-4 rounded-lg border border-green-500/30 mt-4">
              <h4 className="text-lg font-semibold text-white mb-2">🤖 AI Recommendation</h4>
              <p className="text-gray-300 text-sm">{enhancementRecommendation}</p>
            </div>
          )}
        </div>
      );
    }

    // Fallback for old single enhanced prompt structure
    if (enhancedPrompt) {
      return (
        <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
          <h3 className="text-xl font-bold text-white mb-4">✨ Enhanced Prompt</h3>
          <div className="space-y-4">
            <div>
              <h4 className="text-sm font-semibold text-gray-300 mb-2">Original:</h4>
              <p className="text-gray-400 text-sm bg-white/5 p-3 rounded">{prompt}</p>
            </div>
            <div>
              <h4 className="text-sm font-semibold text-gray-300 mb-2">Enhanced:</h4>
              <p className="text-white text-sm bg-white/10 p-3 rounded">{enhancedPrompt}</p>
            </div>
            {enhancementExplanation && (
              <div>
                <h4 className="text-sm font-semibold text-gray-300 mb-2">Why it's better:</h4>
                <p className="text-gray-300 text-sm">{enhancementExplanation}</p>
              </div>
            )}
          </div>
          
          <div className="flex gap-3 mt-6">
            <button
              onClick={() => handleGenerateScript(prompt)}
              disabled={isGenerating}
              className="flex-1 py-3 px-4 bg-gray-600 text-white font-semibold rounded-lg shadow-lg hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
            >
              {isGenerating ? "Generating..." : "Generate with Original"}
            </button>
            <button
              onClick={() => handleGenerateScript(enhancedPrompt)}
              disabled={isGenerating}
              className="flex-1 py-3 px-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold rounded-lg shadow-lg hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
            >
              {isGenerating ? "Generating..." : "Generate with Enhanced"}
            </button>
          </div>
        </div>
      );
    }

    return null;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900">
      <div className="container mx-auto px-4 py-8">
        <header className="text-center mb-12">
          <h1 className="text-5xl font-bold text-white mb-4 bg-gradient-to-r from-pink-400 via-purple-400 to-indigo-400 bg-clip-text text-transparent">
            AI Script Generator
          </h1>
          <p className="text-xl text-gray-300 max-w-2xl mx-auto">
            Transform your ideas into engaging video scripts with AI-powered enhancement and professional voice narration
          </p>
        </header>

        {error && (
          <div className="bg-red-500/20 border border-red-500/50 text-red-300 px-6 py-4 rounded-lg mb-6 backdrop-blur-sm">
            <p className="font-medium">{error}</p>
          </div>
        )}

        <div className="max-w-4xl mx-auto space-y-8">
          {/* Script Generation Form */}
          <div className="bg-white/10 backdrop-blur-lg rounded-xl p-8 border border-white/20 shadow-2xl">
            <div className="space-y-6">
              <div>
                <label className="block text-white text-sm font-medium mb-3">
                  Describe your video idea
                </label>
                <textarea
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  placeholder="Describe your video idea... (e.g., Create a motivational video about achieving your dreams)"
                  rows="4"
                  className="w-full px-4 py-3 bg-white/5 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all duration-200 backdrop-blur-sm"
                />
              </div>

              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-white text-sm font-medium mb-3">
                    Video Type
                  </label>
                  <select
                    value={videoType}
                    onChange={(e) => setVideoType(e.target.value)}
                    className="w-full px-4 py-3 bg-white/5 border border-white/20 rounded-lg text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all duration-200 backdrop-blur-sm"
                  >
                    <option value="general">General</option>
                    <option value="educational">Educational</option>
                    <option value="entertainment">Entertainment</option>
                    <option value="marketing">Marketing</option>
                  </select>
                </div>

                <div>
                  <label className="block text-white text-sm font-medium mb-3">
                    Duration
                  </label>
                  <select
                    value={duration}
                    onChange={(e) => setDuration(e.target.value)}
                    className="w-full px-4 py-3 bg-white/5 border border-white/20 rounded-lg text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all duration-200 backdrop-blur-sm"
                  >
                    <option value="short">Short (30s-1min)</option>
                    <option value="medium">Medium (1-3min)</option>
                    <option value="long">Long (3-5min)</option>
                  </select>
                </div>
              </div>

              <div className="flex flex-col sm:flex-row gap-4">
                <button
                  onClick={handleEnhancePrompt}
                  disabled={isEnhancing || !prompt.trim()}
                  className="px-6 py-3 bg-gradient-to-r from-pink-600 to-purple-600 text-white font-semibold rounded-lg shadow-lg hover:from-pink-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center justify-center"
                >
                  {isEnhancing ? (
                    <>
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                      Enhancing Prompt...
                    </>
                  ) : (
                    <>
                      <span className="mr-2">✨</span>
                      Enhance Prompt
                    </>
                  )}
                </button>
                
                <button
                  onClick={() => handleGenerateScript()}
                  disabled={isGenerating || !prompt.trim()}
                  className="px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold rounded-lg shadow-lg hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center justify-center"
                >
                  {isGenerating ? (
                    <>
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                      Generating Script...
                    </>
                  ) : (
                    <>
                      <span className="mr-2">🎬</span>
                      Generate Script
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>

          {/* Enhanced Prompts Display */}
          {showEnhanced && renderEnhancedPrompts()}

          {/* Generated Script Display */}
          {generatedScript && (
            <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold text-white">
                  {isEditingScript ? "✏️ Editing Script" : "📝 Generated Script"}
                </h2>
                <div className="flex gap-3">
                  {!isEditingScript && (
                    <button
                      onClick={() => setIsEditingScript(true)}
                      className="px-4 py-2 bg-yellow-600 text-white font-medium rounded-lg shadow-lg hover:bg-yellow-700 transition-all duration-200 flex items-center space-x-2"
                    >
                      <span>✏️</span>
                      <span>Edit Script</span>
                    </button>
                  )}
                  
                  <button
                    onClick={handleCopyScript}
                    className="px-4 py-2 bg-green-600 text-white font-medium rounded-lg shadow-lg hover:bg-green-700 transition-all duration-200 flex items-center space-x-2"
                  >
                    <span>📋</span>
                    <span>Copy Script</span>
                  </button>
                </div>
              </div>
              
              <div className="bg-white/5 p-4 rounded-lg max-h-96 overflow-y-auto">
                {isEditingScript ? (
                  <div className="space-y-4">
                    <textarea
                      value={editedScript}
                      onChange={(e) => handleScriptChange(e.target.value)}
                      className="w-full h-80 px-4 py-3 bg-white/5 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all duration-200 backdrop-blur-sm resize-none"
                      placeholder="Edit your script here..."
                    />
                    
                    <div className="flex gap-3">
                      <button
                        onClick={handleSaveScript}
                        disabled={isSavingScript || !hasUnsavedChanges}
                        className="px-4 py-2 bg-green-600 text-white font-medium rounded-lg shadow-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center space-x-2"
                      >
                        {isSavingScript ? (
                          <>
                            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                            <span>Saving...</span>
                          </>
                        ) : (
                          <>
                            <span>💾</span>
                            <span>Save Changes</span>
                          </>
                        )}
                      </button>
                      
                      <button
                        onClick={() => {
                          setIsEditingScript(false);
                          setEditedScript(generatedScript);
                          setHasUnsavedChanges(false);
                        }}
                        className="px-4 py-2 bg-gray-600 text-white font-medium rounded-lg shadow-lg hover:bg-gray-700 transition-all duration-200 flex items-center space-x-2"
                      >
                        <span>❌</span>
                        <span>Cancel</span>
                      </button>
                    </div>
                    
                    {hasUnsavedChanges && (
                      <div className="text-yellow-400 text-sm flex items-center">
                        <span className="mr-2">⚠️</span>
                        You have unsaved changes
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="text-white font-mono leading-relaxed">
                    {formatScript(generatedScript)}
                  </div>
                )}
              </div>

              {/* Audio Generation Section */}
              {!isEditingScript && (
                <div className="mt-6 pt-6 border-t border-white/20">
                  <h3 className="text-lg font-semibold text-white mb-4">🎵 Generate Audio</h3>
                  
                  <div className="space-y-4">
                    <div className="flex flex-wrap gap-3 items-center">
                      <button
                        onClick={() => setShowVoiceSelection(true)}
                        className="px-4 py-2 bg-purple-600 text-white font-medium rounded-lg shadow-lg hover:bg-purple-700 transition-all duration-200 flex items-center space-x-2"
                      >
                        <span>🎤</span>
                        <span>Choose Voice</span>
                      </button>
                      
                      {selectedVoice && (
                        <button
                          onClick={handleGenerateAudio}
                          disabled={isGeneratingAudio}
                          className={`px-4 py-2 rounded-lg font-medium transition-all duration-200 flex items-center space-x-2 ${
                            isGeneratingAudio 
                              ? 'bg-yellow-500/20 text-yellow-300 cursor-not-allowed' 
                              : 'bg-gradient-to-r from-blue-600 to-purple-600 text-white hover:from-blue-700 hover:to-purple-700'
                          }`}
                        >
                          {isGeneratingAudio ? (
                            <>
                              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-yellow-300"></div>
                              <span>Generating...</span>
                            </>
                          ) : (
                            <>
                              <span>🔊</span>
                              <span>Listen</span>
                            </>
                          )}
                        </button>
                      )}
                      
                      {audioData && (
                        <button
                          onClick={downloadAudio}
                          className="px-4 py-2 bg-gradient-to-r from-green-600 to-teal-600 text-white font-medium rounded-lg shadow-lg hover:from-green-700 hover:to-teal-700 transition-all duration-200 flex items-center space-x-2"
                        >
                          <span>💾</span>
                          <span>Download Audio</span>
                        </button>
                      )}
                      
                      {!isGeneratingAudio && !audioData && (
                        <div className="text-xs text-gray-400 flex items-center">
                          💡 Click "Listen" to choose a voice and hear your script read aloud
                        </div>
                      )}
                      
                      {audioData && selectedVoice && (
                        <div className="text-xs text-green-400 flex items-center space-x-2">
                          <span>🎤</span>
                          <span>Audio generated with: <strong>{selectedVoice.display_name}</strong></span>
                          <span className="text-gray-400">• Click "Download Audio" to save</span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Recent Scripts */}
          {scripts.length > 0 && (
            <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
              <h2 className="text-2xl font-bold text-white mb-6">📚 Recent Scripts</h2>
              <div className="space-y-4">
                {scripts.map((script, index) => (
                  <div key={script.id} className="bg-white/5 p-4 rounded-lg border border-white/10">
                    <div className="flex justify-between items-start mb-2">
                      <p className="text-white font-medium truncate flex-1">
                        {script.original_prompt}
                      </p>
                      <div className="flex items-center space-x-2 text-xs text-gray-400 ml-4">
                        <span className="capitalize bg-white/10 px-2 py-1 rounded">
                          {script.video_type}
                        </span>
                        <span className="capitalize bg-white/10 px-2 py-1 rounded">
                          {script.duration}
                        </span>
                      </div>
                    </div>
                    <p className="text-gray-300 text-sm line-clamp-2">
                      {script.generated_script.substring(0, 150)}...
                    </p>
                    <div className="flex justify-between items-center mt-3">
                      <span className="text-xs text-gray-400">
                        {new Date(script.created_at).toLocaleDateString()}
                      </span>
                      <button
                        onClick={() => {
                          setGeneratedScript(script.generated_script);
                          setCurrentScriptId(script.id);
                          setEditedScript(script.generated_script);
                          setIsEditingScript(false);
                          setHasUnsavedChanges(false);
                        }}
                        className="text-purple-400 hover:text-purple-300 text-sm font-medium transition-colors duration-200"
                      >
                        Load →
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Voice Selection Modal */}
        {showVoiceSelection && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20 max-w-lg w-full max-h-[80vh] overflow-y-auto">
              <h3 className="text-2xl font-bold text-white mb-6">🎤 Choose Your Voice</h3>
              
              <div className="space-y-3 mb-6">
                {voices.map((voice) => (
                  <div
                    key={voice.name}
                    onClick={() => setSelectedVoice(voice)}
                    className={`p-4 rounded-lg cursor-pointer transition-all duration-200 ${
                      selectedVoice?.name === voice.name
                        ? 'bg-purple-500/30 border-purple-400 border-2'
                        : 'bg-white/5 border border-white/20 hover:bg-white/10'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <h4 className="font-semibold text-white">{voice.display_name}</h4>
                        <p className="text-sm text-gray-300">
                          {voice.language} • {voice.gender}
                        </p>
                      </div>
                      <div className="text-2xl">
                        {voice.gender === 'Male' ? '👨' : '👩'}
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              <div className="flex gap-3">
                <button
                  onClick={() => setShowVoiceSelection(false)}
                  className="flex-1 py-3 px-4 bg-gray-600 text-white font-semibold rounded-lg shadow-lg hover:bg-gray-700 transition-all duration-200"
                >
                  Cancel
                </button>
                <button
                  onClick={() => {
                    setShowVoiceSelection(false);
                    if (selectedVoice) {
                      handleGenerateAudio();
                    }
                  }}
                  disabled={!selectedVoice}
                  className="flex-1 py-3 px-4 bg-gradient-to-r from-purple-600 to-pink-600 text-white font-semibold rounded-lg shadow-lg hover:from-purple-700 hover:to-pink-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
                >
                  🔊 Generate Audio
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