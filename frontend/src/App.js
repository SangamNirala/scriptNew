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
  const [lastAudioTarget, setLastAudioTarget] = useState(null); // 'script' | 'dialogue'
  
  // Avatar video state
  const [isGeneratingVideo, setIsGeneratingVideo] = useState(false);
  const [avatarVideoData, setAvatarVideoData] = useState(null);
  const [lastGeneratedAudio, setLastGeneratedAudio] = useState(null);

  // Enhanced avatar generation state
  const [avatarOption, setAvatarOption] = useState("default");
  const [userImageFile, setUserImageFile] = useState(null);
  const [userImageBase64, setUserImageBase64] = useState(null);
  const [showAvatarOptions, setShowAvatarOptions] = useState(false);

  // Image prompt enhancement state
  const [isEnhancingImagePrompts, setIsEnhancingImagePrompts] = useState(false);
  const [enhancedImagePrompts, setEnhancedImagePrompts] = useState("");

  // Image generation state
  const [isGeneratingImages, setIsGeneratingImages] = useState(false);
  const [generatedImages, setGeneratedImages] = useState([]);
  const [imageGenerationError, setImageGenerationError] = useState("");
  const [showInlineGallery, setShowInlineGallery] = useState(false);

  // Translation state
  const [currentLanguage, setCurrentLanguage] = useState("en");
  const [isTranslating, setIsTranslating] = useState(false);
  const [originalScript, setOriginalScript] = useState("");
  const [translatedScript, setTranslatedScript] = useState("");
  const [showLanguageDropdown, setShowLanguageDropdown] = useState(false);

  // Dialogue translation state
  const [dialogueLanguage, setDialogueLanguage] = useState("en");
  const [isTranslatingDialogue, setIsTranslatingDialogue] = useState(false);
  const [originalDialogue, setOriginalDialogue] = useState("");
  const [translatedDialogue, setTranslatedDialogue] = useState("");
  const [showDialogueLanguageDropdown, setShowDialogueLanguageDropdown] = useState(false);

  // Ultra-realistic avatar generation state
  const [showUltraRealisticOptions, setShowUltraRealisticOptions] = useState(false);
  const [ultraAvatarStyle, setUltraAvatarStyle] = useState("business_professional");
  const [ultraAvatarGender, setUltraAvatarGender] = useState("female");
  const [ultraAvatarIndex, setUltraAvatarIndex] = useState(1);

  // AI-optimized script generation state
  const [showAIScriptOptions, setShowAIScriptOptions] = useState(false);
  const [visualStyle, setVisualStyle] = useState("cinematic");
  const [targetPlatform, setTargetPlatform] = useState("general");
  const [mood, setMood] = useState("professional");
  const [isGeneratingAIScript, setIsGeneratingAIScript] = useState(false);
  const [aiScriptData, setAiScriptData] = useState(null);

  // Dialogue-only script state
  const [dialogueOnlyScript, setDialogueOnlyScript] = useState("");
  // Dialogue edit state
  const [isEditingDialogue, setIsEditingDialogue] = useState(false);
  const [editedDialogue, setEditedDialogue] = useState("");
  const [hasUnsavedDialogueChanges, setHasUnsavedDialogueChanges] = useState(false);
  const [isSavingDialogue, setIsSavingDialogue] = useState(false);
  
  // Audio target: which content to generate/play audio for ('script' | 'dialogue')
  const [audioTarget, setAudioTarget] = useState("script");

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

  // Close language dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (!event.target.closest('.language-dropdown') && showLanguageDropdown) {
        setShowLanguageDropdown(false);
      }
      if (!event.target.closest('.dialogue-language-dropdown') && showDialogueLanguageDropdown) {
        setShowDialogueLanguageDropdown(false);
      }
    };

    document.addEventListener('click', handleClickOutside);
    return () => document.removeEventListener('click', handleClickOutside);
  }, [showLanguageDropdown, showDialogueLanguageDropdown]);

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

      // Handle new response structure
      const data = response.data;
      
      // Set the enhancement variations
      setEnhancementVariations(data.enhancement_variations || []);
      setEnhancementRecommendation(data.recommendation || "");
      
      // Find the recommended/best variation (highest score) for backward compatibility
      if (data.enhancement_variations && data.enhancement_variations.length > 0) {
        const bestVariation = data.enhancement_variations.reduce((best, current) => 
          current.estimated_performance_score > best.estimated_performance_score ? current : best
        );
        
        setEnhancedPrompt(bestVariation.enhanced_prompt);
        
        // Use the recommendation as explanation
        setEnhancementExplanation(data.recommendation || `${bestVariation.title} - Focus: ${bestVariation.focus_strategy}`);
      }
      
      setShowEnhanced(true);
    } catch (err) {
      setError("Error enhancing prompt. Please try again.");
      console.error("Error enhancing prompt:", err);
    } finally {
      setIsEnhancing(false);
    }
  };

  const handleGenerateScript = async (promptType = "original", variationIndex = null) => {
    let finalPrompt = prompt;
    let promptTypeLabel = "original";
    
    if (promptType === "enhanced" && variationIndex !== null && enhancementVariations[variationIndex]) {
      finalPrompt = enhancementVariations[variationIndex].enhanced_prompt;
      promptTypeLabel = `enhanced (${enhancementVariations[variationIndex].title})`;
    } else if (promptType === "enhanced" && enhancedPrompt) {
      finalPrompt = enhancedPrompt;
      promptTypeLabel = "enhanced";
    }
    
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
      setDialogueOnlyScript(extractDialogueOnly(response.data.generated_script));
      setCurrentScriptId(response.data.id); // Store the script ID
      setGeneratedWithPrompt(promptTypeLabel);
      
      // Reset translation state for new script
      setCurrentLanguage("en");
      setOriginalScript("");
      setTranslatedScript("");
      
      // Reset dialogue translation state for new script
      setDialogueLanguage("en");
      setOriginalDialogue("");
      setTranslatedDialogue("");
      
      fetchScripts(); // Refresh the list
    } catch (err) {
      setError("Error generating script. Please try again.");
      console.error("Error generating script:", err);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleGenerateAIScript = async () => {
    if (!prompt.trim()) {
      setError("Please enter a prompt first");
      return;
    }

    setIsGeneratingAIScript(true);
    setError("");
    setShowAIScriptOptions(false);

    try {
      const response = await axios.post(`${API}/generate-ai-video-script`, {
        prompt: prompt,
        video_type: videoType,
        duration: duration,
        visual_style: visualStyle,
        target_platform: targetPlatform,
        mood: mood
      });

      setAiScriptData(response.data);
      setGeneratedScript(response.data.generated_script);
      setDialogueOnlyScript(extractDialogueOnly(response.data.generated_script));
      setCurrentScriptId(response.data.id); // Store the script ID
      setGeneratedWithPrompt("ai-optimized");
      
      // Reset translation state for new AI script
      setCurrentLanguage("en");
      setOriginalScript("");
      setTranslatedScript("");
      
      // Reset dialogue translation state for new AI script
      setDialogueLanguage("en");
      setOriginalDialogue("");
      setTranslatedDialogue("");
      
      fetchScripts(); // Refresh the scripts list
    } catch (err) {
      setError("Error generating AI-optimized script. Please try again.");
      console.error("Error generating AI script:", err);
    } finally {
      setIsGeneratingAIScript(false);
    }
  };

  const handlePlayScript = () => {
    setAudioTarget("script");
    if (isPlaying) {
      if (audioData) {
        audioData.pause();
        audioData.currentTime = 0;
      }
      setIsPlaying(false);
      setAudioData(null);
      return;
    }
    setShowVoiceSelection(true);
  };

  // Dialogue-only actions
  const handleEditDialogue = () => {
    setIsEditingDialogue(true);
    setEditedDialogue(dialogueOnlyScript);
    setHasUnsavedDialogueChanges(false);
  };

  const handleCancelEditDialogue = () => {
    setIsEditingDialogue(false);
    setEditedDialogue("");
    setHasUnsavedDialogueChanges(false);
  };

  const handleDialogueChange = (newText) => {
    setEditedDialogue(newText);
    setHasUnsavedDialogueChanges(newText !== dialogueOnlyScript);
  };

  const handleSaveDialogue = async () => {
    try {
      setIsSavingDialogue(true);
      setError("");

      // Build a map from timestamp -> dialogue from editedDialogue
      const pairs = [];
      const parts = editedDialogue.split(/\n\n+/).map(s => s.trim()).filter(Boolean);
      for (const chunk of parts) {
        const lines = chunk.split("\n").map(s => s.trim()).filter(Boolean);
        if (lines.length >= 2) {
          const ts = lines[0];
          const text = lines.slice(1).join(" ");
          pairs.push({ ts, text });
        }
      }

      // Replace in generatedScript: find blocks that look like [mm:ss-mm:ss] ... [DIALOGUE:] line
      let newScript = generatedScript;
      for (const { ts, text } of pairs) {
        const tsEsc = ts.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
        const regex = new RegExp(`(\\*?\\*?\\[${tsEsc}\\][\\s\\S]*?\\[DIALOGUE:\\\]\\*?\\*?\\s*)(.+)`, "i");
        newScript = newScript.replace(regex, (m, p1) => `${p1}${text}`);
      }

      // Update states
      setGeneratedScript(newScript);
      setDialogueOnlyScript(editedDialogue);

      // If we have a currentScriptId, persist the full script using existing endpoint
      if (currentScriptId) {
        await axios.put(`${API}/scripts/${currentScriptId}`, {
          script_id: currentScriptId,
          generated_script: newScript
        });
      }

      setIsEditingDialogue(false);
      setHasUnsavedDialogueChanges(false);
      setEditedDialogue("");

      // refresh recent list
      fetchScripts();
    } catch (err) {
      console.error("Error saving dialogue:", err);
      setError("Error saving dialogue changes. Please try again.");
    } finally {
      setIsSavingDialogue(false);
    }
  };

  const handlePlayDialogue = () => {
    if (isPlaying) {
      if (audioData) {
        audioData.pause();
        audioData.currentTime = 0;
      }
      setIsPlaying(false);
      setAudioData(null);
      return;
    }
    setAudioTarget("dialogue");
    setShowVoiceSelection(true);
  };


  const handleVoiceSelect = (voice) => {
    setSelectedVoice(voice);
  };

  // Script editing functions
  const handleEditScript = () => {
    setIsEditingScript(true);
    setEditedScript(generatedScript);
    setHasUnsavedChanges(false);
  };

  const handleCancelEdit = () => {
    setIsEditingScript(false);
    setEditedScript("");
    setHasUnsavedChanges(false);
  };

  const handleScriptChange = (newText) => {
    setEditedScript(newText);
    setHasUnsavedChanges(newText !== generatedScript);
  };

  const handleSaveScript = async () => {
    if (!currentScriptId || !hasUnsavedChanges) return;
    
    setIsSavingScript(true);
    setError("");

    try {
      const response = await axios.put(`${API}/scripts/${currentScriptId}`, {
        script_id: currentScriptId,
        generated_script: editedScript
      });

      setGeneratedScript(editedScript);
      setDialogueOnlyScript(extractDialogueOnly(editedScript));
      setIsEditingScript(false);
      setHasUnsavedChanges(false);
      setEditedScript("");
      
      // Refresh scripts list
      fetchScripts();
      
    } catch (err) {
      setError("Error saving script changes. Please try again.");
      console.error("Error saving script:", err);
    } finally {
      setIsSavingScript(false);
    }
  };

  const handleGenerateAndPlayAudio = async () => {
    if (!selectedVoice) {
      setError("Please select a voice.");
      return;
    }
    const textToSpeak = audioTarget === "dialogue" ? (isEditingDialogue ? editedDialogue : dialogueOnlyScript) : generatedScript;
    if (!textToSpeak) {
      setError("No content available to generate audio.");
      return;
    }

    setIsGeneratingAudio(true);
    setShowVoiceSelection(false);
    setError("");

    try {
      const response = await axios.post(`${API}/generate-audio`, {
        text: textToSpeak,
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
      setLastAudioTarget(audioTarget);
      audio.play();
      
    } catch (err) {
      console.error("Error generating audio:", err);
      setError("Error generating audio. Please try again.");
    } finally {
      setIsGeneratingAudio(false);
    }
  };

  const handleDownloadAudio = () => {
    if (!lastGeneratedAudio || !selectedVoice) {
      setError("No audio available to download.");
      return;
    }

    try {
      // Convert base64 to audio blob
      const audioBytes = atob(lastGeneratedAudio);
      const audioArray = new Uint8Array(audioBytes.length);
      
      for (let i = 0; i < audioBytes.length; i++) {
        audioArray[i] = audioBytes.charCodeAt(i);
      }
      
      const audioBlob = new Blob([audioArray], { type: 'audio/mp3' });
      
      // Create download link
      const downloadUrl = URL.createObjectURL(audioBlob);
      const link = document.createElement('a');
      link.href = downloadUrl;
      
      // Generate filename with voice name and timestamp
      const timestamp = new Date().toISOString().split('T')[0];
      const voiceName = selectedVoice.display_name.replace(/\s+/g, '_');
      link.download = `script_audio_${voiceName}_${timestamp}.mp3`;
      
      // Trigger download
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      // Clean up URL
      URL.revokeObjectURL(downloadUrl);
      
    } catch (err) {
      console.error("Error downloading audio:", err);
      setError("Error downloading audio. Please try again.");
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

  const handleImageUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      setUserImageFile(file);
      
      // Convert to base64
      const reader = new FileReader();
      reader.onload = (e) => {
        const base64 = e.target.result.split(',')[1]; // Remove data:image/...;base64, prefix
        setUserImageBase64(base64);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleGenerateEnhancedAvatarVideo = async () => {
    if (!lastGeneratedAudio) {
      setError("Please generate audio first before creating avatar video.");
      return;
    }

    if (avatarOption === "upload" && !userImageBase64) {
      setError("Please upload an image for the upload option.");
      return;
    }

    setIsGeneratingVideo(true);
    setError("");
    setShowAvatarOptions(false);

    try {
      const response = await axios.post(`${API}/generate-enhanced-avatar-video`, {
        audio_base64: lastGeneratedAudio,
        avatar_option: avatarOption,
        user_image_base64: userImageBase64,
        script_text: generatedScript
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
        requestId: response.data.request_id,
        avatarOption: response.data.avatar_option,
        scriptSegments: response.data.script_segments,
        sadtalkerUsed: response.data.sadtalker_used,
        qualityLevel: "Enhanced"
      });

    } catch (err) {
      console.error("Error generating enhanced avatar video:", err);
      setError("Error generating enhanced avatar video. Please try again.");
    } finally {
      setIsGeneratingVideo(false);
    }
  };

  const handleGenerateUltraRealisticAvatarVideo = async () => {
    if (!lastGeneratedAudio) {
      setError("Please generate audio first before creating avatar video.");
      return;
    }

    setIsGeneratingVideo(true);
    setError("");
    setShowUltraRealisticOptions(false);

    try {
      const response = await axios.post(`${API}/generate-ultra-realistic-avatar-video`, {
        audio_base64: lastGeneratedAudio,
        avatar_style: ultraAvatarStyle,
        gender: ultraAvatarGender,
        avatar_index: ultraAvatarIndex,
        script_text: generatedScript
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
        requestId: response.data.request_id,
        avatarStyle: response.data.avatar_style,
        gender: response.data.gender,
        avatarIndex: response.data.avatar_index,
        scriptSegments: response.data.script_segments,
        backgroundContexts: response.data.background_contexts,
        aiModelUsed: response.data.ai_model_used,
        qualityLevel: response.data.quality_level
      });

    } catch (err) {
      console.error("Error generating ultra-realistic avatar video:", err);
      setError("Error generating ultra-realistic avatar video. Please try again.");
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

  const handleEnhanceImagePrompts = async () => {
    if (!generatedScript) {
      setError("Please generate a script first before enhancing image prompts.");
      return;
    }

    setIsEnhancingImagePrompts(true);
    setError("");

    try {
      const response = await axios.post(`${API}/enhance-image-prompts`, {
        script_content: generatedScript,
        video_type: videoType,
        enhancement_style: "detailed" // Can be made configurable later
      });

      setEnhancedImagePrompts(response.data.enhanced_script);

    } catch (err) {
      console.error("Error enhancing image prompts:", err);
      if (err.response?.status === 500) {
        setError("AI service temporarily unavailable. Please try again in a moment.");
      } else {
        setError("Error enhancing image prompts. Please try again.");
      }
    } finally {
      setIsEnhancingImagePrompts(false);
    }
  };

  const handleGenerateImages = async () => {
    if (!enhancedImagePrompts) {
      setImageGenerationError("Please enhance image prompts first.");
      return;
    }

    setIsGeneratingImages(true);
    setImageGenerationError("");

    try {
      // Extract enhanced image prompts from the enhanced script
      const promptRegex = /\[([^\]]+)\]/g;
      const matches = [];
      let match;
      while ((match = promptRegex.exec(enhancedImagePrompts)) !== null) {
        matches.push(match[1]);
      }

      if (matches.length === 0) {
        setImageGenerationError("No image prompts found in enhanced script.");
        return;
      }

      const response = await axios.post(`${API}/generate-images`, {
        enhanced_prompts: matches,
        video_type: videoType,
        number_of_images_per_prompt: 1
      });

      setGeneratedImages(response.data.generated_images);
      
      // Open new tab with generated images
      openImageGallery(response.data.generated_images);

    } catch (err) {
      console.error("Error generating images:", err);
      if (err.response?.status === 500) {
        setImageGenerationError("Image generation service temporarily unavailable. Please try again in a moment.");
      } else {
        setImageGenerationError("Error generating images. Please try again.");
      }
    } finally {
      setIsGeneratingImages(false);
    }
  };

  const openImageGallery = (images) => {
    try {
      // Try to open new tab with the image gallery
      const newTab = window.open('', '_blank');
      
      // Check if popup was blocked
      if (!newTab || newTab.closed || typeof newTab.closed == 'undefined') {
        console.log("Popup blocked, showing images inline instead");
        // Fallback: Show images inline by scrolling to the image gallery section
        setShowInlineGallery(true);
        // Scroll to the gallery section
        setTimeout(() => {
          const gallerySection = document.getElementById('inline-image-gallery');
          if (gallerySection) {
            gallerySection.scrollIntoView({ behavior: 'smooth' });
          }
        }, 100);
        return;
      }
      
      // Create HTML content for the new tab
      const htmlContent = `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Generated Images - AI Video Script Generator</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
    </style>
</head>
<body class="bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900">
    <div class="container mx-auto px-4 py-8">
        <div class="text-center mb-12">
            <h1 class="text-5xl font-bold text-white mb-4 bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                Generated Images
            </h1>
            <p class="text-xl text-purple-200">
                AI-Generated Images from Enhanced Prompts
            </p>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            ${images.map((img, index) => `
                <div class="bg-white/10 backdrop-blur-lg rounded-lg border border-white/20 p-6">
                    <div class="aspect-square mb-4 rounded-lg overflow-hidden bg-white/5">
                        <img src="data:image/png;base64,${img.image_base64}" 
                             alt="Generated Image ${img.image_index}"
                             class="w-full h-full object-cover hover:scale-105 transition-transform duration-200"
                             onclick="this.requestFullscreen()"
                             style="cursor: zoom-in" />
                    </div>
                    <div class="space-y-3">
                        <h3 class="text-lg font-semibold text-white">Shot ${img.image_index}</h3>
                        <div class="bg-purple-500/20 rounded-lg p-3">
                            <h4 class="text-sm font-medium text-purple-300 mb-2">Enhanced Prompt:</h4>
                            <p class="text-sm text-gray-200 leading-relaxed">${img.enhanced_prompt}</p>
                        </div>
                        <button onclick="downloadImage('${img.image_base64}', 'generated-image-${img.image_index}.png')"
                                class="w-full px-4 py-2 bg-blue-500/20 text-blue-300 rounded-lg hover:bg-blue-500/30 transition-colors flex items-center justify-center space-x-2">
                            <span>💾</span>
                            <span>Download Image</span>
                        </button>
                    </div>
                </div>
            `).join('')}
        </div>
        
        <div class="text-center mt-12">
            <button onclick="window.close()" 
                    class="px-6 py-3 bg-purple-500/20 text-purple-300 rounded-lg hover:bg-purple-500/30 transition-colors">
                Close Gallery
            </button>
        </div>
    </div>
    
    <script>
        function downloadImage(base64Data, filename) {
            const link = document.createElement('a');
            link.href = 'data:image/png;base64,' + base64Data;
            link.download = filename;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
    </script>
</body>
</html>`;

      newTab.document.write(htmlContent);
      newTab.document.close();
    } catch (error) {
      console.error("Error opening image gallery:", error);
      // Fallback: Show images inline
      setShowInlineGallery(true);
      // Scroll to the gallery section
      setTimeout(() => {
        const gallerySection = document.getElementById('inline-image-gallery');
        if (gallerySection) {
          gallerySection.scrollIntoView({ behavior: 'smooth' });
        }
      }, 100);
    }
  };

  // Function to download images
  const downloadImage = (base64Data, filename) => {
    const link = document.createElement('a');
    link.href = 'data:image/png;base64,' + base64Data;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const formatScript = (script) => {
    return script
      .replace(/\[([^\]]+)\]/g, '<span class="text-blue-600 font-medium">[$1]</span>')
      .replace(/\(([^)]+)\)/g, '<span class="text-green-600 italic">($1)</span>')
      .replace(/\*\*([^*]+)\*\*/g, '<strong class="font-bold">$1</strong>')
      .replace(/\n/g, '<br/>');
  };

  // Function to extract only dialogue (timestamps + spoken lines) from the full script
  const extractDialogueOnly = (script) => {
    const lines = script.split('\n');
    const dialogueEntries = [];
    
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i].trim();
      
      // Look for timestamp patterns that appear before dialogue
      const timestampMatch = line.match(/\*?\*?\[(\d+:\d+[-–]\d+:\d+)\]\s*AI\s+IMAGE\s+PROMPT/i);
      if (timestampMatch) {
        const timestamp = timestampMatch[1];
        
        // Look for the corresponding dialogue in the next few lines
        for (let j = i + 1; j <= Math.min(i + 5, lines.length - 1); j++) {
          const nextLine = lines[j].trim();
          if (nextLine.includes('[DIALOGUE:]')) {
            const dialogueMatch = nextLine.match(/\*?\*?\[DIALOGUE:\]\*?\*?\s*(.+)/);
            if (dialogueMatch) {
              let dialogueText = dialogueMatch[1].trim();
              // Clean the dialogue text
              dialogueText = dialogueText
                .replace(/^\(.*?\)\s*/, '') // Remove voice directions like "(Upbeat voice)"
                .replace(/^["'"']|["'"']$/g, '') // Remove surrounding quotes
                .trim();
              
              if (dialogueText && dialogueText.length > 5) {
                dialogueEntries.push(`${timestamp}\n${dialogueText}`);
              }
            }
            break;
          }
        }
      }
    }
    
    // If no structured entries found, try to extract quoted dialogue
    if (dialogueEntries.length === 0) {
      const quotedMatches = script.match(/"([^"]{10,}[^"]*?)"/g);
      if (quotedMatches) {
        quotedMatches.forEach(match => {
          let cleanDialogue = match.replace(/^"|"$/g, '').trim();
          // Filter out AI image prompts and other non-dialogue content
          if (cleanDialogue && 
              !cleanDialogue.includes('AI IMAGE PROMPT') && 
              !cleanDialogue.includes('shot') &&
              !cleanDialogue.includes('camera') &&
              !cleanDialogue.includes('photography') &&
              cleanDialogue.length > 10 && 
              cleanDialogue.length < 200) {
            dialogueEntries.push(cleanDialogue);
          }
        });
      }
    }
    
    // Remove duplicates and return formatted result
    const uniqueEntries = [...new Set(dialogueEntries)];
    return uniqueEntries.join('\n\n');
  };

  // Function to format dialogue-only script for display
  const formatDialogueScript = (script) => {
    return script
      .replace(/\(([^)]*[\d:.\-]+[^)]*)\)/g, '<span class="text-purple-400 font-medium">($1)</span>') // Highlight timestamps
      .replace(/\*\*([^*]+)\*\*/g, '<strong class="font-bold">$1</strong>')
      .replace(/\n/g, '<br/>');
  };

  // Translation handler
  const handleTranslateScript = async (targetLanguage) => {
    if (!generatedScript) {
      setError("Please generate a script first before translating.");
      return;
    }

    // If switching back to English, show original script
    if (targetLanguage === "en") {
      if (originalScript) {
        setGeneratedScript(originalScript);
        setDialogueOnlyScript(extractDialogueOnly(originalScript));
        setCurrentLanguage("en");
        return;
      }
      // If no original cached, current script is already in English
      setCurrentLanguage("en");
      return;
    }

    // Save original script if not already saved
    if (!originalScript) {
      setOriginalScript(generatedScript);
    }

    setIsTranslating(true);
    setError("");

    try {
      // Delegate preservation rules to backend which:
      // - Keeps [bracketed] image prompts in English
      // - Keeps AI IMAGE PROMPT quoted content in English
      const response = await axios.post(`${API}/translate-script`, {
        text: generatedScript,
        source_language: "en",
        target_language: targetLanguage
      });

      if (response.data.success) {
        const translatedText = response.data.translated_text;
        setGeneratedScript(translatedText);
        setDialogueOnlyScript(extractDialogueOnly(translatedText));
        setTranslatedScript(translatedText);
        setCurrentLanguage(targetLanguage);
      } else {
        setError("Translation failed. Please try again.");
      }
    } catch (err) {
      console.error("Translation error:", err);
      setError("Translation service is temporarily unavailable. Please try again later.");
    } finally {
      setIsTranslating(false);
      setShowLanguageDropdown(false);
    }
  };

  // Dialogue translation handler
  const handleTranslateDialogue = async (targetLanguage) => {
    if (!dialogueOnlyScript) {
      setError("Please generate a script first before translating dialogue.");
      return;
    }

    // If switching back to English, show original dialogue
    if (targetLanguage === "en") {
      if (originalDialogue) {
        setDialogueOnlyScript(originalDialogue);
        setDialogueLanguage("en");
        return;
      }
      // If no original cached, current dialogue is already in English
      setDialogueLanguage("en");
      return;
    }

    // Save original dialogue if not already saved
    if (!originalDialogue) {
      setOriginalDialogue(dialogueOnlyScript);
    }

    setIsTranslatingDialogue(true);
    setError("");

    try {
      // Call the same translation endpoint but with dialogue content
      const response = await axios.post(`${API}/translate-script`, {
        text: dialogueOnlyScript,
        source_language: "en",
        target_language: targetLanguage
      });

      if (response.data.success) {
        const translatedText = response.data.translated_text;
        setDialogueOnlyScript(translatedText);
        setTranslatedDialogue(translatedText);
        setDialogueLanguage(targetLanguage);
      } else {
        setError("Translation failed. Please try again.");
      }
    } catch (err) {
      console.error("Dialogue translation error:", err);
      setError("Translation service is temporarily unavailable. Please try again later.");
    } finally {
      setIsTranslatingDialogue(false);
      setShowDialogueLanguageDropdown(false);
    }
  };

  const formatEnhancedPrompt = (text) => {
    return text
      .replace(/\n\n/g, '<br/><br/>') // Double line breaks for paragraphs
      .replace(/\n/g, '<br/>') // Single line breaks
      .replace(/\*\*([^*]+)\*\*/g, '<strong class="font-bold text-white">$1</strong>') // Bold text in white
      // Format framework section headers with colored styling
      .replace(/🎬 COMPREHENSIVE SCRIPT FRAMEWORK/g, '<span class="text-purple-400 font-bold text-lg">🎬 COMPREHENSIVE SCRIPT FRAMEWORK</span>')
      .replace(/📋 SCRIPT FRAMEWORK:/g, '<span class="text-blue-400 font-bold">📋 SCRIPT FRAMEWORK:</span>')
      .replace(/🎯 PRODUCTION GUIDELINES:/g, '<span class="text-green-400 font-bold">🎯 PRODUCTION GUIDELINES:</span>')
      .replace(/🧠 PSYCHOLOGICAL TRIGGERS INTEGRATED:/g, '<span class="text-yellow-400 font-bold">🧠 PSYCHOLOGICAL TRIGGERS:</span>')
      .replace(/📱 PLATFORM ADAPTATIONS:/g, '<span class="text-pink-400 font-bold">📱 PLATFORM ADAPTATIONS:</span>')
      // Format template placeholders
      .replace(/\[([A-Z_]+)\]/g, '<span class="bg-purple-500/20 text-purple-300 px-2 py-1 rounded text-xs font-mono">[$1]</span>')
      // Format bullet points and lists
      .replace(/^- ([^\n]+)/gm, '<span class="text-gray-300">• $1</span>')
      // Format numbered lists
      .replace(/^(\d+)\. ([^\n]+)/gm, '<span class="text-blue-300 font-medium">$1.</span> <span class="text-gray-200">$2</span>');
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
                    <option value="extended_5">Extended (5-10min)</option>
                    <option value="extended_10">Extended (10-15min)</option>
                    <option value="extended_15">Extended (15-20min)</option>
                    <option value="extended_20">Extended (20-25min)</option>
                    <option value="extended_25">Extended (25-30min)</option>
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
            {showEnhanced && (enhancedPrompt || enhancementVariations.length > 0) && (
              <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
                <h3 className="text-xl font-bold text-white mb-4">✨ Enhanced Prompts</h3>
                
                <div className="mb-4">
                  <h4 className="text-sm font-medium text-gray-300 mb-2">Original:</h4>
                  <p className="text-gray-400 bg-white/5 p-3 rounded-lg">{prompt}</p>
                </div>

                {/* Enhancement Variations Preview */}
                {enhancementVariations.length > 0 && (
                  <div className="mb-6">
                    <h4 className="text-sm font-medium text-gray-300 mb-3">Enhancement Variations:</h4>
                    <div className="space-y-3">
                      {enhancementVariations.map((variation, index) => (
                        <div 
                          key={variation.id} 
                          className="p-4 rounded-lg border bg-white/5 border-white/20"
                        >
                          <div className="flex justify-between items-start mb-2">
                            <div className="flex items-center space-x-2">
                              <span className="text-white font-medium">{index + 1}. {variation.title}</span>
                              <span className="text-xs px-2 py-1 bg-blue-500/20 text-blue-300 rounded-full">
                                {variation.focus_strategy}
                              </span>
                              <span className="text-xs px-2 py-1 bg-green-500/20 text-green-300 rounded-full">
                                Score: {Math.round(variation.estimated_performance_score)}/10
                              </span>
                            </div>
                          </div>
                          <div 
                            className="text-gray-300 text-sm leading-relaxed"
                            dangerouslySetInnerHTML={{ __html: formatEnhancedPrompt(variation.enhanced_prompt) }}
                          />
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Single Enhanced Prompt (backward compatibility) */}
                {enhancementVariations.length === 0 && enhancedPrompt && (
                  <div className="mb-6">
                    <h4 className="text-sm font-medium text-gray-300 mb-2">Enhanced:</h4>
                    <div 
                      className="text-white bg-white/5 p-3 rounded-lg leading-relaxed"
                      dangerouslySetInnerHTML={{ __html: formatEnhancedPrompt(enhancedPrompt) }}
                    />
                  </div>
                )}
                
                {/* Recommendation */}
                {enhancementRecommendation && (
                  <div className="mb-6">
                    <h4 className="text-sm font-medium text-gray-300 mb-2">AI Recommendation:</h4>
                    <div 
                      className="text-gray-300 bg-blue-500/10 border border-blue-500/20 p-3 rounded-lg text-sm leading-relaxed"
                      dangerouslySetInnerHTML={{ __html: formatEnhancedPrompt(enhancementRecommendation) }}
                    />
                  </div>
                )}

                {/* Enhancement Explanation (fallback) */}
                {!enhancementRecommendation && enhancementExplanation && (
                  <div className="mb-6">
                    <h4 className="text-sm font-medium text-gray-300 mb-2">Why this is better:</h4>
                    <div 
                      className="text-gray-300 bg-white/5 p-3 rounded-lg text-sm leading-relaxed"
                      dangerouslySetInnerHTML={{ __html: formatEnhancedPrompt(enhancementExplanation) }}
                    />
                  </div>
                )}

                {/* Multiple Script Generation Buttons */}
                <div className="space-y-3">
                  {/* Original Prompt Button */}
                  <button
                    onClick={() => handleGenerateScript("original")}
                    disabled={isGenerating}
                    className="w-full py-3 px-4 bg-gradient-to-r from-gray-600 to-gray-700 text-white font-semibold rounded-lg shadow-lg hover:from-gray-700 hover:to-gray-800 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 transform hover:scale-105"
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

                  {/* Enhanced Prompt Buttons */}
                  {enhancementVariations.map((variation, index) => (
                    <button
                      key={variation.id}
                      onClick={() => handleGenerateScript("enhanced", index)}
                      disabled={isGenerating}
                      className="w-full py-3 px-4 bg-gradient-to-r from-purple-600 to-blue-600 text-white font-semibold rounded-lg shadow-lg hover:from-purple-700 hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 transform hover:scale-105"
                    >
                      {isGenerating ? (
                        <div className="flex items-center justify-center">
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                          Generating...
                        </div>
                      ) : (
                        <div className="text-center">
                          <div>✨ Generate with {index + 1}{index === 0 ? 'st' : index === 1 ? 'nd' : 'rd'} Enhanced Prompt</div>
                          <div className="text-xs opacity-75 mt-1">
                            {variation.title} ({variation.focus_strategy})
                          </div>
                        </div>
                      )}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Right Column - Generated Script */}
          <div className="space-y-6">
            {/* Dialogue Only Box - positioned above the generated script */}
            {dialogueOnlyScript && (
              <div className="bg-gradient-to-r from-purple-500/10 to-blue-500/10 backdrop-blur-lg rounded-xl p-6 border border-purple-300/20">
                <div className="flex justify-between items-center mb-6">
                  <h2 className="text-2xl font-bold text-white">
                    🎭 Dialogue Only 
                    <span className="text-sm font-normal text-gray-300 ml-2">
                      (Timestamps + Spoken Lines)
                    </span>
                  </h2>
                  <div className="flex items-center space-x-2">
                    {/* Copy Dialogue Button */}
                    <button
                      onClick={() => navigator.clipboard.writeText(dialogueOnlyScript)}
                      className="px-4 py-2 bg-purple-500/20 text-purple-300 rounded-lg hover:bg-purple-500/30 transition-colors flex items-center space-x-2"
                    >
                      <span>📋</span>
                      <span>Copy</span>
                    </button>

                    {/* Edit Dialogue Button */}
                    {!isEditingDialogue && (
                      <button
                        onClick={handleEditDialogue}
                        disabled={isGeneratingAudio}
                        className={`px-4 py-2 rounded-lg font-medium transition-all duration-200 flex items-center space-x-2 ${
                          isGeneratingAudio
                            ? 'bg-gray-500/20 text-gray-400 cursor-not-allowed opacity-75'
                            : 'bg-blue-500/20 text-blue-300 hover:bg-blue-500/30'
                        }`}
                      >
                        <span>✏️</span>
                        <span>Edit</span>
                      </button>
                    )}

                    {/* Save/Cancel when editing */}
                    {isEditingDialogue && (
                      <>
                        <button
                          onClick={handleSaveDialogue}
                          disabled={!hasUnsavedDialogueChanges || isSavingDialogue}
                          className={`px-4 py-2 rounded-lg font-medium transition-all duration-200 flex items-center space-x-2 ${
                            !hasUnsavedDialogueChanges || isSavingDialogue
                              ? 'bg-gray-500/20 text-gray-400 cursor-not-allowed opacity-75'
                              : 'bg-green-500/20 text-green-300 hover:bg-green-500/30'
                          }`}
                        >
                          {isSavingDialogue ? (
                            <>
                              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-green-300"></div>
                              <span>Saving...</span>
                            </>
                          ) : (
                            <>
                              <span>💾</span>
                              <span>Save</span>
                            </>
                          )}
                        </button>
                        <button
                          onClick={handleCancelEditDialogue}
                          disabled={isSavingDialogue}
                          className="px-4 py-2 rounded-lg font-medium transition-all duration-200 flex items-center space-x-2 bg-red-500/20 text-red-300 hover:bg-red-500/30"
                        >
                          <span>❌</span>
                          <span>Cancel</span>
                        </button>
                      </>
                    )}

                    {/* Listen Dialogue Button */}
                    <button
                      onClick={handlePlayDialogue}
                      disabled={isGeneratingAudio || isEditingDialogue}
                      className={`px-4 py-2 rounded-lg font-medium transition-all duration-200 flex items-center space-x-2 ${
                        isPlaying
                          ? 'bg-red-500/20 text-red-300 hover:bg-red-500/30'
                          : isGeneratingAudio || isEditingDialogue
                          ? 'bg-gray-500/20 text-gray-400 cursor-not-allowed opacity-75'
                          : 'bg-green-500/20 text-green-300 hover:bg-green-500/30'
                      }`}
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

                    {/* Download Dialogue Audio Button */}
                    {lastGeneratedAudio && lastAudioTarget === 'dialogue' && (
                      <button
                        onClick={handleDownloadAudio}
                        className="px-4 py-2 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg hover:from-blue-700 hover:to-blue-800 transition-all duration-200 flex items-center space-x-2"
                      >
                        <span>💾</span>
                        <span>Download Audio</span>
                      </button>
                    )}

                    {/* Change Language Button for Dialogue Only */}
                    <div className="relative dialogue-language-dropdown">
                      <button
                        onClick={() => setShowDialogueLanguageDropdown(!showDialogueLanguageDropdown)}
                        disabled={isTranslatingDialogue || isEditingDialogue || !dialogueOnlyScript}
                        className={`px-4 py-2 rounded-lg font-medium transition-all duration-200 flex items-center space-x-2 ${
                          isTranslatingDialogue 
                            ? 'bg-yellow-500/20 text-yellow-300 cursor-not-allowed' 
                            : !dialogueOnlyScript || isEditingDialogue
                            ? 'bg-gray-500/20 text-gray-400 cursor-not-allowed opacity-75'
                            : 'bg-blue-500/20 text-blue-300 hover:bg-blue-500/30'
                        }`}
                      >
                        {isTranslatingDialogue ? (
                          <>
                            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-yellow-300"></div>
                            <span>Translating...</span>
                          </>
                        ) : (
                          <>
                            <span>🌐</span>
                            <span>Change Language</span>
                            <span className="text-xs">({dialogueLanguage === "en" ? "English" : "हिन्दी"})</span>
                          </>
                        )}
                      </button>
                      
                      {/* Language Dropdown */}
                      {showDialogueLanguageDropdown && !isTranslatingDialogue && (
                        <div className="absolute top-full left-0 mt-2 w-48 bg-gray-800/95 backdrop-blur-lg rounded-lg border border-white/20 shadow-xl z-10">
                          <button
                            onClick={() => handleTranslateDialogue("en")}
                            className={`w-full px-4 py-3 text-left transition-colors duration-200 rounded-t-lg ${
                              dialogueLanguage === "en" 
                                ? 'bg-blue-500/30 text-blue-300' 
                                : 'text-gray-300 hover:bg-white/10'
                            }`}
                          >
                            <span className="flex items-center space-x-3">
                              <span>🇺🇸</span>
                              <span>English</span>
                              {dialogueLanguage === "en" && <span className="text-xs text-blue-400">✓ Current</span>}
                            </span>
                          </button>
                          <button
                            onClick={() => handleTranslateDialogue("hi")}
                            className={`w-full px-4 py-3 text-left transition-colors duration-200 rounded-b-lg ${
                              dialogueLanguage === "hi" 
                                ? 'bg-blue-500/30 text-blue-300' 
                                : 'text-gray-300 hover:bg-white/10'
                            }`}
                          >
                            <span className="flex items-center space-x-3">
                              <span>🇮🇳</span>
                              <span>हिन्दी (Hindi)</span>
                              {dialogueLanguage === "hi" && <span className="text-xs text-blue-400">✓ Current</span>}
                            </span>
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
                
                {/* Dialogue Content */}
                {isEditingDialogue ? (
                  <div className="space-y-3 w-full">
                    <textarea
                      value={editedDialogue}
                      onChange={(e) => handleDialogueChange(e.target.value)}
                      className="w-full h-64 p-4 bg-white/10 backdrop-blur-lg rounded-lg border border-white/20 text-gray-200 leading-relaxed resize-none focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-transparent"
                      placeholder="Edit dialogue timestamps and lines here... Each block should be:\n[0:00-0:03]\nYour dialogue line"
                    />
                    {hasUnsavedDialogueChanges && (
                      <div className="text-sm text-yellow-300 flex items-center space-x-2">
                        <span>⚠️</span>
                        <span>You have unsaved changes. Click "Save" to apply them.</span>
                      </div>
                    )}
                  </div>
                ) : (
                  <div 
                    className="text-gray-200 leading-relaxed bg-white/5 p-4 rounded-lg max-h-80 overflow-y-auto"
                    dangerouslySetInnerHTML={{ __html: formatDialogueScript(dialogueOnlyScript) }}
                  />
                )}
                
                <div className="mt-4 pt-4 border-t border-white/20">
                  <div className="text-xs text-gray-400">
                    <span className="text-purple-400">●</span> This box contains only the dialogue content - timestamps and spoken lines without AI image prompts or production notes.
                  </div>
                </div>
              </div>
            )}

            {generatedScript && (
              <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
                <div className="flex justify-between items-center mb-6">
                  <h2 className="text-2xl font-bold text-white">
                    🎬 Generated Script 
                    <span className="text-sm font-normal text-gray-300 ml-2">
                      ({generatedWithPrompt} prompt)
                    </span>
                  </h2>
                  <div className="flex items-center space-x-2">
                    {/* Edit Button */}
                    <button
                      onClick={handleEditScript}
                      disabled={isEditingScript || isGeneratingAudio}
                      className={`px-4 py-2 rounded-lg font-medium transition-all duration-200 flex items-center space-x-2 ${
                        isEditingScript 
                          ? 'bg-gray-500/20 text-gray-400 cursor-not-allowed opacity-75' 
                          : 'bg-blue-500/20 text-blue-300 hover:bg-blue-500/30'
                      }`}
                    >
                      <span>✏️</span>
                      <span>{isEditingScript ? 'Editing...' : 'Edit'}</span>
                    </button>

                    {/* Save Changes Button (only visible when editing) */}
                    {isEditingScript && (
                      <button
                        onClick={handleSaveScript}
                        disabled={!hasUnsavedChanges || isSavingScript}
                        className={`px-4 py-2 rounded-lg font-medium transition-all duration-200 flex items-center space-x-2 ${
                          !hasUnsavedChanges || isSavingScript
                            ? 'bg-gray-500/20 text-gray-400 cursor-not-allowed opacity-75'
                            : 'bg-green-500/20 text-green-300 hover:bg-green-500/30'
                        }`}
                      >
                        {isSavingScript ? (
                          <>
                            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-green-300"></div>
                            <span>Saving...</span>
                          </>
                        ) : (
                          <>
                            <span>💾</span>
                            <span>Save Changes</span>
                          </>
                        )}
                      </button>
                    )}

                    {/* Cancel Button (only visible when editing) */}
                    {isEditingScript && (
                      <button
                        onClick={handleCancelEdit}
                        disabled={isSavingScript}
                        className="px-4 py-2 rounded-lg font-medium transition-all duration-200 flex items-center space-x-2 bg-red-500/20 text-red-300 hover:bg-red-500/30"
                      >
                        <span>❌</span>
                        <span>Cancel</span>
                      </button>
                    )}

                    {/* Listen Button */}
                    <button
                      onClick={handlePlayScript}
                      disabled={isGeneratingAudio || isEditingScript}
                      className={`px-4 py-2 rounded-lg font-medium transition-all duration-200 flex items-center space-x-2 ${
                        isPlaying 
                          ? 'bg-red-500/20 text-red-300 hover:bg-red-500/30' 
                          : isGeneratingAudio || isEditingScript
                          ? 'bg-gray-500/20 text-gray-400 cursor-not-allowed opacity-75'
                          : 'bg-green-500/20 text-green-300 hover:bg-green-500/30'
                      }`}
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

                    {/* Change Language Button */}
                    <div className="relative language-dropdown">
                      <button
                        onClick={() => setShowLanguageDropdown(!showLanguageDropdown)}
                        disabled={isTranslating || isEditingScript || !generatedScript}
                        className={`px-4 py-2 rounded-lg font-medium transition-all duration-200 flex items-center space-x-2 ${
                          isTranslating 
                            ? 'bg-yellow-500/20 text-yellow-300 cursor-not-allowed' 
                            : !generatedScript || isEditingScript
                            ? 'bg-gray-500/20 text-gray-400 cursor-not-allowed opacity-75'
                            : 'bg-blue-500/20 text-blue-300 hover:bg-blue-500/30'
                        }`}
                      >
                        {isTranslating ? (
                          <>
                            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-yellow-300"></div>
                            <span>Translating...</span>
                          </>
                        ) : (
                          <>
                            <span>🌐</span>
                            <span>Change Language</span>
                            <span className="text-xs">({currentLanguage === "en" ? "English" : "हिन्दी"})</span>
                          </>
                        )}
                      </button>
                      
                      {/* Language Dropdown */}
                      {showLanguageDropdown && !isTranslating && (
                        <div className="absolute top-full left-0 mt-2 w-48 bg-gray-800/95 backdrop-blur-lg rounded-lg border border-white/20 shadow-xl z-10">
                          <button
                            onClick={() => handleTranslateScript("en")}
                            className={`w-full px-4 py-3 text-left transition-colors duration-200 rounded-t-lg ${
                              currentLanguage === "en" 
                                ? 'bg-blue-500/30 text-blue-300' 
                                : 'text-gray-300 hover:bg-white/10'
                            }`}
                          >
                            <span className="flex items-center space-x-3">
                              <span>🇺🇸</span>
                              <span>English</span>
                              {currentLanguage === "en" && <span className="text-xs text-blue-400">✓ Current</span>}
                            </span>
                          </button>
                          <button
                            onClick={() => handleTranslateScript("hi")}
                            className={`w-full px-4 py-3 text-left transition-colors duration-200 rounded-b-lg ${
                              currentLanguage === "hi" 
                                ? 'bg-blue-500/30 text-blue-300' 
                                : 'text-gray-300 hover:bg-white/10'
                            }`}
                          >
                            <span className="flex items-center space-x-3">
                              <span>🇮🇳</span>
                              <span>Hindi (हिन्दी)</span>
                              {currentLanguage === "hi" && <span className="text-xs text-blue-400">✓ Current</span>}
                            </span>
                          </button>
                        </div>
                      )}
                    </div>

                    {/* Enhance Image Prompt Button */}
                    <button
                      onClick={handleEnhanceImagePrompts}
                      disabled={isEnhancingImagePrompts || isEditingScript || !generatedScript}
                      className={`px-4 py-2 rounded-lg font-medium transition-all duration-200 flex items-center space-x-2 ${
                        isEnhancingImagePrompts 
                          ? 'bg-yellow-500/20 text-yellow-300 cursor-not-allowed' 
                          : !generatedScript || isEditingScript
                          ? 'bg-gray-500/20 text-gray-400 cursor-not-allowed opacity-75'
                          : 'bg-orange-500/20 text-orange-300 hover:bg-orange-500/30'
                      }`}
                    >
                      {isEnhancingImagePrompts ? (
                        <>
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-yellow-300"></div>
                          <span>Enhancing...</span>
                        </>
                      ) : (
                        <>
                          <span>🎨</span>

                  {/* If audio was generated for dialogue, show a download button here too */}
                  {lastGeneratedAudio && lastAudioTarget === 'dialogue' && (
                    <button
                      onClick={handleDownloadAudio}
                      className="mt-3 px-4 py-2 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg hover:from-blue-700 hover:to-blue-800 transition-all duration-200 flex items-center space-x-2"
                    >
                      <span>💾</span>
                      <span>Download Audio</span>
                    </button>
                  )}

                          <span>Enhance Image Prompt</span>
                        </>
                      )}
                    </button>
                  </div>
                </div>
                
                {/* Script Content - Editable or Display */}
                {isEditingScript ? (
                  <div className="space-y-4">
                    <textarea
                      value={editedScript}
                      onChange={(e) => handleScriptChange(e.target.value)}
                      className="w-full h-80 p-4 bg-white/10 backdrop-blur-lg rounded-lg border border-white/20 text-gray-200 leading-relaxed resize-none focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-transparent"
                      placeholder="Edit your script content here..."
                    />
                    {hasUnsavedChanges && (
                      <div className="text-sm text-yellow-300 flex items-center space-x-2">
                        <span>⚠️</span>
                        <span>You have unsaved changes. Click "Save Changes" to apply them.</span>
                      </div>
                    )}
                  </div>
                ) : (
                  <div 
                    className="text-gray-200 leading-relaxed bg-white/5 p-4 rounded-lg max-h-96 overflow-y-auto"
                    dangerouslySetInnerHTML={{ __html: formatScript(generatedScript) }}
                  />
                )}
                
                {/* Enhanced Image Prompts Display */}
                {enhancedImagePrompts && (
                  <div className="mt-6 bg-gradient-to-r from-orange-500/10 to-pink-500/10 backdrop-blur-lg rounded-lg border border-orange-300/20 p-6">
                    <div className="flex items-center space-x-2 mb-4">
                      <span className="text-2xl">🎨</span>
                      <h3 className="text-xl font-bold text-orange-300">Enhanced AI Image Prompts</h3>
                    </div>
                    <div className="text-sm text-orange-200 mb-4">
                      Copy any prompt below and paste directly into MidJourney, DALL-E, Stable Diffusion, or other AI image generators
                    </div>
                    <div 
                      className="text-gray-200 leading-relaxed bg-white/5 p-4 rounded-lg max-h-96 overflow-y-auto"
                      dangerouslySetInnerHTML={{ __html: formatScript(enhancedImagePrompts) }}
                    />
                    <div className="flex gap-3 mt-4">
                      <button
                        onClick={() => navigator.clipboard.writeText(enhancedImagePrompts)}
                        className="px-4 py-2 bg-orange-500/20 text-orange-300 rounded-lg hover:bg-orange-500/30 transition-colors flex items-center space-x-2"
                      >
                        <span>📋</span>
                        <span>Copy Enhanced Prompts</span>
                      </button>
                      
                      {/* Generate Image Button */}
                      <button
                        onClick={handleGenerateImages}
                        disabled={isGeneratingImages}
                        className={`px-4 py-2 rounded-lg font-medium transition-all duration-200 flex items-center space-x-2 ${
                          isGeneratingImages 
                            ? 'bg-pink-500/20 text-pink-300 cursor-not-allowed' 
                            : 'bg-pink-500/20 text-pink-300 hover:bg-pink-500/30'
                        }`}
                      >
                        {isGeneratingImages ? (
                          <>
                            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-pink-300"></div>
                            <span>Generating...</span>
                          </>
                        ) : (
                          <>
                            <span>🖼️</span>
                            <span>Generate Images</span>
                          </>
                        )}
                      </button>
                    </div>
                    
                    {/* Image Generation Error Display */}
                    {imageGenerationError && (
                      <div className="mt-4 p-3 bg-red-500/20 border border-red-300/20 rounded-lg">
                        <p className="text-red-300 text-sm">{imageGenerationError}</p>
                      </div>
                    )}
                  </div>
                )}
                
                <div className="mt-4 pt-4 border-t border-white/20 flex flex-wrap gap-3">
                  <button
                    onClick={() => navigator.clipboard.writeText(generatedScript)}
                    className="px-4 py-2 bg-white/10 text-white rounded-lg hover:bg-white/20 transition-colors flex items-center space-x-2"
                  >
                    <span>📋</span>
                    <span>Copy Script</span>
                  </button>
                  
                  {lastGeneratedAudio && selectedVoice && (
                    <button
                      onClick={handleDownloadAudio}
                      className="px-4 py-2 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg hover:from-blue-700 hover:to-blue-800 transition-all duration-200 flex items-center space-x-2"
                    >
                      <span>💾</span>
                      <span>Download Audio</span>
                    </button>
                  )}
                  
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

                  {lastGeneratedAudio && (
                    <button
                      onClick={() => setShowAvatarOptions(true)}
                      disabled={isGeneratingVideo}
                      className={`px-4 py-2 rounded-lg font-medium transition-all duration-200 flex items-center space-x-2 ${
                        isGeneratingVideo 
                          ? 'bg-yellow-500/20 text-yellow-300 cursor-not-allowed' 
                          : 'bg-gradient-to-r from-purple-600 to-pink-600 text-white hover:from-purple-700 hover:to-pink-700'
                      }`}
                    >
                      <span>✨</span>
                      <span>Enhanced Avatar Video</span>
                    </button>
                  )}

                  {lastGeneratedAudio && (
                    <button
                      onClick={() => setShowUltraRealisticOptions(true)}
                      disabled={isGeneratingVideo}
                      className={`px-4 py-2 rounded-lg font-medium transition-all duration-200 flex items-center space-x-2 ${
                        isGeneratingVideo 
                          ? 'bg-yellow-500/20 text-yellow-300 cursor-not-allowed' 
                          : 'bg-gradient-to-r from-pink-600 to-red-600 text-white hover:from-pink-700 hover:to-red-700'
                      }`}
                    >
                      <span>🎬</span>
                      <span>Ultra-Realistic Avatar</span>
                    </button>
                  )}
                  
                  {!isPlaying && !isGeneratingAudio && !lastGeneratedAudio && (
                    <div className="text-xs text-gray-400 flex items-center">
                      💡 Click "Listen" to choose a voice and hear your script read aloud
                    </div>
                  )}
                  
                  {lastGeneratedAudio && selectedVoice && (
                    <div className="text-xs text-green-400 flex items-center space-x-2">
                      <span>🎤</span>
                      <span>Audio generated with: <strong>{selectedVoice.display_name}</strong></span>
                      <span className="text-gray-400">• Click "Download Audio" to save</span>
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
                    {avatarVideoData.qualityLevel && (
                      <span className="text-sm font-normal text-gray-300 ml-2">
                        ({avatarVideoData.qualityLevel})
                      </span>
                    )}
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
                      Duration: {Math.round(avatarVideoData.duration || 0)}s
                      {avatarVideoData.scriptSegments && (
                        <span> | Script Segments: {avatarVideoData.scriptSegments}</span>
                      )}
                    </p>
                    
                    {/* Ultra-Realistic Features Info */}
                    {avatarVideoData.qualityLevel === "Ultra-Realistic" && (
                      <div className="mt-3 p-3 bg-gradient-to-r from-pink-500/20 to-red-500/20 rounded-lg border border-pink-500/30">
                        <div className="flex items-center justify-center space-x-4 text-xs text-white">
                          <div className="flex items-center space-x-1">
                            <span>🎭</span>
                            <span>Style: {avatarVideoData.avatarStyle?.replace('_', ' ')}</span>
                          </div>
                          <div className="flex items-center space-x-1">
                            <span>👤</span>
                            <span>Gender: {avatarVideoData.gender}</span>
                          </div>
                          <div className="flex items-center space-x-1">
                            <span>🤖</span>
                            <span>AI: {avatarVideoData.aiModelUsed}</span>
                          </div>
                        </div>
                        
                        {avatarVideoData.backgroundContexts && avatarVideoData.backgroundContexts.length > 0 && (
                          <div className="mt-2 text-xs text-gray-300">
                            <span className="font-medium">🎬 Dynamic Backgrounds: </span>
                            {avatarVideoData.backgroundContexts.join(', ')}
                          </div>
                        )}
                      </div>
                    )}
                    
                    {/* Enhanced Features Info */}
                    {avatarVideoData.qualityLevel === "Enhanced" && (
                      <div className="mt-3 text-xs text-gray-400">
                        <span className="font-medium">✨ Enhanced Features: </span>
                        Avatar Option: {avatarVideoData.avatarOption}
                        {avatarVideoData.sadtalkerUsed && " | SadTalker: Enabled"}
                      </div>
                    )}
                    
                    {/* Basic Features Info */}
                    {!avatarVideoData.qualityLevel && (
                      <div className="mt-3 text-xs text-gray-400">
                        💡 This avatar video contains essential narration from your script, 
                        perfectly synchronized with lip movements for professional video content.
                      </div>
                    )}
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
                           setDialogueOnlyScript(extractDialogueOnly(script.generated_script));
                           setCurrentScriptId(script.id); // Set the script ID
                           setGeneratedWithPrompt("saved");
                           // Reset editing state if user switches scripts
                           setIsEditingScript(false);
                           setEditedScript("");
                           setHasUnsavedChanges(false);
                           // Reset translation state when loading existing script
                           setCurrentLanguage("en");
                           setOriginalScript("");
                           setTranslatedScript("");
                           // Reset dialogue translation state when loading existing script  
                           setDialogueLanguage("en");
                           setOriginalDialogue("");
                           setTranslatedDialogue("");
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

        {/* Avatar Options Modal */}
        {showAvatarOptions && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20 max-w-md w-full max-h-[80vh] overflow-y-auto">
              <h3 className="text-2xl font-bold text-white mb-4">✨ Avatar Options</h3>
              
              <div className="space-y-4 mb-6">
                {/* Default Avatar Option */}
                <div
                  onClick={() => setAvatarOption("default")}
                  className={`p-4 rounded-lg cursor-pointer transition-all duration-200 ${
                    avatarOption === "default"
                      ? 'bg-purple-500/30 border-purple-400 border-2'
                      : 'bg-white/5 border border-white/20 hover:bg-white/10'
                  }`}
                >
                  <div className="flex items-center space-x-3">
                    <div className="text-2xl">🤖</div>
                    <div>
                      <div className="font-medium text-white">Default AI Avatar</div>
                      <div className="text-sm text-gray-400">Use our built-in professional avatar</div>
                    </div>
                  </div>
                </div>

                {/* Upload Your Photo Option */}
                <div
                  onClick={() => setAvatarOption("upload")}
                  className={`p-4 rounded-lg cursor-pointer transition-all duration-200 ${
                    avatarOption === "upload"
                      ? 'bg-purple-500/30 border-purple-400 border-2'
                      : 'bg-white/5 border border-white/20 hover:bg-white/10'
                  }`}
                >
                  <div className="flex items-center space-x-3">
                    <div className="text-2xl">📸</div>
                    <div>
                      <div className="font-medium text-white">Upload Your Photo</div>
                      <div className="text-sm text-gray-400">Use your own image as the avatar</div>
                    </div>
                  </div>
                </div>

                {/* AI Generated Avatar Option */}
                <div
                  onClick={() => setAvatarOption("ai_generated")}
                  className={`p-4 rounded-lg cursor-pointer transition-all duration-200 ${
                    avatarOption === "ai_generated"
                      ? 'bg-purple-500/30 border-purple-400 border-2'
                      : 'bg-white/5 border border-white/20 hover:bg-white/10'
                  }`}
                >
                  <div className="flex items-center space-x-3">
                    <div className="text-2xl">🎭</div>
                    <div>
                      <div className="font-medium text-white">AI Generated Avatar</div>
                      <div className="text-sm text-gray-400">Create a unique AI-generated human face</div>
                    </div>
                  </div>
                </div>

                {/* File Upload for Upload Option */}
                {avatarOption === "upload" && (
                  <div className="mt-4 p-4 bg-white/5 rounded-lg border border-white/20">
                    <label className="block text-white text-sm font-medium mb-2">
                      Upload your photo:
                    </label>
                    <input
                      type="file"
                      accept="image/*"
                      onChange={handleImageUpload}
                      className="w-full p-2 bg-white/10 border border-white/20 rounded-lg text-white file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-purple-500/20 file:text-purple-300 hover:file:bg-purple-500/30"
                    />
                    {userImageFile && (
                      <div className="mt-2 text-sm text-green-400">
                        ✓ Image uploaded: {userImageFile.name}
                      </div>
                    )}
                  </div>
                )}
              </div>

              <div className="flex gap-3">
                <button
                  onClick={() => setShowAvatarOptions(false)}
                  className="flex-1 py-3 px-4 bg-gray-600 text-white font-semibold rounded-lg shadow-lg hover:bg-gray-700 transition-all duration-200"
                >
                  Cancel
                </button>
                <button
                  onClick={handleGenerateEnhancedAvatarVideo}
                  disabled={isGeneratingVideo || (avatarOption === "upload" && !userImageBase64)}
                  className="flex-1 py-3 px-4 bg-gradient-to-r from-purple-600 to-pink-600 text-white font-semibold rounded-lg shadow-lg hover:from-purple-700 hover:to-pink-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
                >
                  {isGeneratingVideo ? (
                    <div className="flex items-center justify-center">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      Generating...
                    </div>
                  ) : (
                    "✨ Generate Enhanced Video"
                  )}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Ultra-Realistic Avatar Options Modal */}
        {showUltraRealisticOptions && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20 max-w-lg w-full max-h-[90vh] overflow-y-auto">
              <h3 className="text-2xl font-bold text-white mb-6 flex items-center">
                <span className="mr-2">🎬</span>
                Ultra-Realistic Avatar Options
              </h3>
              
              <div className="space-y-6">
                {/* Avatar Style Selection */}
                <div>
                  <label className="block text-white text-sm font-medium mb-3">
                    Avatar Style
                  </label>
                  <div className="grid grid-cols-2 gap-3">
                    <div
                      onClick={() => setUltraAvatarStyle("business_professional")}
                      className={`p-3 rounded-lg cursor-pointer transition-all duration-200 ${
                        ultraAvatarStyle === "business_professional"
                          ? 'bg-pink-500/30 border-pink-400 border-2'
                          : 'bg-white/5 border border-white/20 hover:bg-white/10'
                      }`}
                    >
                      <div className="flex items-center space-x-2">
                        <div className="text-xl">👔</div>
                        <div>
                          <div className="font-medium text-white">Business Professional</div>
                          <div className="text-xs text-gray-400">Formal, corporate style</div>
                        </div>
                      </div>
                    </div>
                    
                    <div
                      onClick={() => setUltraAvatarStyle("casual")}
                      className={`p-3 rounded-lg cursor-pointer transition-all duration-200 ${
                        ultraAvatarStyle === "casual"
                          ? 'bg-pink-500/30 border-pink-400 border-2'
                          : 'bg-white/5 border border-white/20 hover:bg-white/10'
                      }`}
                    >
                      <div className="flex items-center space-x-2">
                        <div className="text-xl">👕</div>
                        <div>
                          <div className="font-medium text-white">Casual</div>
                          <div className="text-xs text-gray-400">Relaxed, friendly style</div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Gender Selection */}
                <div>
                  <label className="block text-white text-sm font-medium mb-3">
                    Avatar Gender
                  </label>
                  <div className="grid grid-cols-3 gap-3">
                    <div
                      onClick={() => setUltraAvatarGender("female")}
                      className={`p-3 rounded-lg cursor-pointer transition-all duration-200 ${
                        ultraAvatarGender === "female"
                          ? 'bg-pink-500/30 border-pink-400 border-2'
                          : 'bg-white/5 border border-white/20 hover:bg-white/10'
                      }`}
                    >
                      <div className="text-center">
                        <div className="text-xl mb-1">👩</div>
                        <div className="text-sm font-medium text-white">Female</div>
                      </div>
                    </div>
                    
                    <div
                      onClick={() => setUltraAvatarGender("male")}
                      className={`p-3 rounded-lg cursor-pointer transition-all duration-200 ${
                        ultraAvatarGender === "male"
                          ? 'bg-pink-500/30 border-pink-400 border-2'
                          : 'bg-white/5 border border-white/20 hover:bg-white/10'
                      }`}
                    >
                      <div className="text-center">
                        <div className="text-xl mb-1">👨</div>
                        <div className="text-sm font-medium text-white">Male</div>
                      </div>
                    </div>
                    
                    <div
                      onClick={() => setUltraAvatarGender("diverse")}
                      className={`p-3 rounded-lg cursor-pointer transition-all duration-200 ${
                        ultraAvatarGender === "diverse"
                          ? 'bg-pink-500/30 border-pink-400 border-2'
                          : 'bg-white/5 border border-white/20 hover:bg-white/10'
                      }`}
                    >
                      <div className="text-center">
                        <div className="text-xl mb-1">🌍</div>
                        <div className="text-sm font-medium text-white">Diverse</div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Avatar Index Selection */}
                <div>
                  <label className="block text-white text-sm font-medium mb-3">
                    Avatar Variation
                  </label>
                  <div className="grid grid-cols-3 gap-3">
                    {[1, 2, 3].map((index) => (
                      <div
                        key={index}
                        onClick={() => setUltraAvatarIndex(index)}
                        className={`p-3 rounded-lg cursor-pointer transition-all duration-200 ${
                          ultraAvatarIndex === index
                            ? 'bg-pink-500/30 border-pink-400 border-2'
                            : 'bg-white/5 border border-white/20 hover:bg-white/10'
                        }`}
                      >
                        <div className="text-center">
                          <div className="text-xl mb-1">🎭</div>
                          <div className="text-sm font-medium text-white">Option {index}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Features Info */}
                <div className="bg-white/5 p-4 rounded-lg border border-white/20">
                  <h4 className="text-sm font-medium text-white mb-2">🚀 Ultra-Realistic Features:</h4>
                  <ul className="text-xs text-gray-300 space-y-1">
                    <li>• Professional AI-generated human faces</li>
                    <li>• Perfect lip-sync with advanced audio analysis</li>
                    <li>• Dynamic backgrounds that change with script content</li>
                    <li>• Realistic facial expressions and micro-movements</li>
                    <li>• Studio-quality lighting and composition</li>
                    <li>• Maximum quality optimized for professional use</li>
                  </ul>
                </div>
              </div>

              <div className="flex gap-3 mt-6">
                <button
                  onClick={() => setShowUltraRealisticOptions(false)}
                  className="flex-1 py-3 px-4 bg-gray-600 text-white font-semibold rounded-lg shadow-lg hover:bg-gray-700 transition-all duration-200"
                >
                  Cancel
                </button>
                <button
                  onClick={handleGenerateUltraRealisticAvatarVideo}
                  disabled={isGeneratingVideo}
                  className="flex-1 py-3 px-4 bg-gradient-to-r from-pink-600 to-red-600 text-white font-semibold rounded-lg shadow-lg hover:from-pink-700 hover:to-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
                >
                  {isGeneratingVideo ? (
                    <div className="flex items-center justify-center">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      Generating...
                    </div>
                  ) : (
                    "🎬 Generate Ultra-Realistic Video"
                  )}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Inline Image Gallery */}
        {showInlineGallery && generatedImages.length > 0 && (
          <div id="inline-image-gallery" className="bg-white/5 backdrop-blur-lg rounded-xl border border-white/20 p-6 mt-8">
            <div className="text-center mb-8">
              <h2 className="text-3xl font-bold text-white mb-2 bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                Generated Images
              </h2>
              <p className="text-lg text-purple-200">
                AI-Generated Images from Enhanced Prompts
              </p>
              <button
                onClick={() => setShowInlineGallery(false)}
                className="mt-4 px-4 py-2 bg-red-500/20 text-red-300 rounded-lg hover:bg-red-500/30 transition-colors"
              >
                ✕ Close Gallery
              </button>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {generatedImages.map((img, index) => (
                <div key={index} className="bg-white/10 backdrop-blur-lg rounded-lg border border-white/20 p-4">
                  <div className="aspect-square mb-4 rounded-lg overflow-hidden bg-white/5">
                    <img 
                      src={`data:image/png;base64,${img.image_base64}`}
                      alt={`Generated Image ${img.image_index}`}
                      className="w-full h-full object-cover hover:scale-105 transition-transform duration-200 cursor-zoom-in"
                      onClick={(e) => {
                        if (e.target.requestFullscreen) {
                          e.target.requestFullscreen();
                        }
                      }}
                    />
                  </div>
                  <div className="space-y-3">
                    <h3 className="text-lg font-semibold text-white">Shot {img.image_index}</h3>
                    <div className="bg-purple-500/20 rounded-lg p-3">
                      <h4 className="text-sm font-medium text-purple-300 mb-2">Enhanced Prompt:</h4>
                      <p className="text-sm text-gray-200 leading-relaxed">{img.enhanced_prompt}</p>
                    </div>
                    <button
                      onClick={() => downloadImage(img.image_base64, `generated-image-${img.image_index}.png`)}
                      className="w-full px-4 py-2 bg-blue-500/20 text-blue-300 rounded-lg hover:bg-blue-500/30 transition-colors flex items-center justify-center space-x-2"
                    >
                      <span>💾</span>
                      <span>Download Image</span>
                    </button>
                  </div>
                </div>
              ))}
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