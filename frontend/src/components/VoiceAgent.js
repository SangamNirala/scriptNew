import React, { useState, useEffect, useRef } from 'react';
import { Mic, MicOff, Volume2, VolumeX, Play, Pause, RotateCcw, Settings, Activity, MessageCircle, Bot, User, X } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Alert, AlertDescription } from './ui/alert';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';

const VoiceAgent = ({ onClose }) => {
  // Voice states
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [currentSpeech, setCurrentSpeech] = useState('');
  const [conversation, setConversation] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [voiceError, setVoiceError] = useState(null);
  
  // Voice settings
  const [selectedVoice, setSelectedVoice] = useState(null);
  const [speechRate, setSpeechRate] = useState(1.0);
  const [speechPitch, setSpeechPitch] = useState(1.0);
  const [voiceVolume, setVoiceVolume] = useState(0.8);
  const [availableVoices, setAvailableVoices] = useState([]);
  const [autoListen, setAutoListen] = useState(true);
  
  // Legal Q&A settings
  const [sessionId, setSessionId] = useState(null);
  const [selectedJurisdiction, setSelectedJurisdiction] = useState('US');
  const [selectedDomain, setSelectedDomain] = useState('all_domains');
  
  // Enhanced conversation states
  const [interimTranscript, setInterimTranscript] = useState('');
  const [isUserSpeaking, setIsUserSpeaking] = useState(false);
  const [conversationContext, setConversationContext] = useState([]);
  const [suggestedFollowUps, setSuggestedFollowUps] = useState([]);
  const [isInterrupted, setIsInterrupted] = useState(false);
  const [conversationSummary, setConversationSummary] = useState('');
  const [lastUserIntent, setLastUserIntent] = useState('');
  
  // Enhanced error handling and retry logic
  const [retryCount, setRetryCount] = useState(0);
  const [isInitializing, setIsInitializing] = useState(false);
  const [recognitionState, setRecognitionState] = useState('idle'); // 'idle', 'starting', 'active', 'stopping', 'error'
  
  // Refs
  const recognitionRef = useRef(null);
  const synthRef = useRef(null);
  const conversationEndRef = useRef(null);
  const retryTimeoutRef = useRef(null);
  const restartTimeoutRef = useRef(null);
  const interruptTimeoutRef = useRef(null);
  const currentUtteranceRef = useRef(null);

  const jurisdictions = [
    { value: 'US', label: 'United States' },
    { value: 'UK', label: 'United Kingdom' },
    { value: 'CA', label: 'Canada' },
    { value: 'AU', label: 'Australia' },
    { value: 'EU', label: 'European Union' },
    { value: 'IN', label: 'India' }
  ];

  const legalDomains = [
    { value: 'all_domains', label: 'All Legal Domains' },
    { value: 'contract_law', label: 'Contract Law' },
    { value: 'employment_labor_law', label: 'Employment & Labor Law' },
    { value: 'intellectual_property', label: 'Intellectual Property' },
    { value: 'corporate_regulatory', label: 'Corporate & Regulatory' },
    { value: 'civil_criminal_procedure', label: 'Civil & Criminal Procedure' },
    { value: 'constitutional_law', label: 'Constitutional Law' },
    { value: 'taxation_financial', label: 'Taxation & Financial' },
    { value: 'real_estate_law', label: 'Real Estate Law' },
    { value: 'family_law', label: 'Family Law' },
    { value: 'immigration_law', label: 'Immigration Law' }
  ];

  const sampleQuestions = [
    "What are the key elements of a valid contract?",
    "How does employment at-will doctrine work?", 
    "What is the difference between copyright and trademark?",
    "What are the requirements for forming an LLC?",
    "How do non-compete agreements work in different states?",
    "What are the legal requirements for terminating an employee?",
    "Can you explain breach of contract remedies?",
    "What is intellectual property infringement?",
    "How do I protect my business from liability?",
    "What are the basics of employment discrimination law?"
  ];

  // Generate contextual follow-up suggestions
  const generateFollowUpSuggestions = (lastResponse, userQuestion) => {
    const suggestions = [];
    
    // Contract law follow-ups
    if (lastResponse.toLowerCase().includes('contract') || userQuestion.toLowerCase().includes('contract')) {
      suggestions.push("What happens if a contract is breached?");
      suggestions.push("Can you explain contract modification?");
      suggestions.push("What makes a contract void?");
    }
    
    // Employment law follow-ups
    if (lastResponse.toLowerCase().includes('employment') || userQuestion.toLowerCase().includes('employee')) {
      suggestions.push("What are wrongful termination laws?");
      suggestions.push("Can you explain workplace discrimination?");
      suggestions.push("What are employee rights regarding wages?");
    }
    
    // IP law follow-ups
    if (lastResponse.toLowerCase().includes('intellectual property') || lastResponse.toLowerCase().includes('copyright') || lastResponse.toLowerCase().includes('trademark')) {
      suggestions.push("How do I file for trademark protection?");
      suggestions.push("What is fair use in copyright law?");
      suggestions.push("Can you explain patent basics?");
    }
    
    // Business law follow-ups
    if (lastResponse.toLowerCase().includes('llc') || lastResponse.toLowerCase().includes('corporation') || userQuestion.toLowerCase().includes('business')) {
      suggestions.push("What are the tax implications of an LLC?");
      suggestions.push("How do I maintain corporate compliance?");
      suggestions.push("What are the differences between LLC and corporation?");
    }
    
    // Generic follow-ups if no specific category matched
    if (suggestions.length === 0) {
      suggestions.push("Can you provide more details?");
      suggestions.push("What are the practical implications?");
      suggestions.push("Are there any exceptions to this rule?");
    }
    
    return suggestions.slice(0, 3); // Return max 3 suggestions
  };

  // Enhanced cleanup utility
  const cleanupReferences = () => {
    // Clear all timeouts
    if (retryTimeoutRef.current) {
      clearTimeout(retryTimeoutRef.current);
      retryTimeoutRef.current = null;
    }
    if (restartTimeoutRef.current) {
      clearTimeout(restartTimeoutRef.current);
      restartTimeoutRef.current = null;
    }
    if (interruptTimeoutRef.current) {
      clearTimeout(interruptTimeoutRef.current);
      interruptTimeoutRef.current = null;
    }
    
    // Stop speech synthesis safely
    if (synthRef.current) {
      try {
        synthRef.current.cancel();
        if (currentUtteranceRef.current) {
          currentUtteranceRef.current = null;
        }
      } catch (error) {
        console.warn('Error during speech synthesis cleanup:', error);
      }
    }
    
    // Stop recognition safely
    if (recognitionRef.current) {
      try {
        recognitionRef.current.abort();
        recognitionRef.current = null;
      } catch (error) {
        console.warn('Error during recognition cleanup:', error);
      }
    }
    
    setRecognitionState('idle');
    setIsListening(false);
    setIsSpeaking(false);
    setIsUserSpeaking(false);
    setInterimTranscript('');
  };

  // Initialize voice capabilities and session
  useEffect(() => {
    initializeVoiceCapabilities();
    initializeSession();
    
    return cleanupReferences;
  }, []);

  // Scroll to bottom when conversation updates
  useEffect(() => {
    conversationEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [conversation]);

  // Categorize speech recognition errors
  const categorizeError = (error) => {
    const fatalErrors = ['not-allowed', 'audio-capture', 'service-not-allowed'];
    const retryableErrors = ['aborted', 'network', 'no-speech'];
    
    if (fatalErrors.includes(error)) {
      return 'fatal';
    } else if (retryableErrors.includes(error)) {
      return 'retryable';
    }
    return 'unknown';
  };

  // Calculate retry delay with exponential backoff
  const getRetryDelay = (attempt) => {
    return Math.min(1000 * Math.pow(2, attempt), 10000); // Max 10 seconds
  };

  const initializeVoiceCapabilities = () => {
    if (isInitializing) return;
    
    setIsInitializing(true);
    
    try {
      // Check for Web Speech API support
      if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        setVoiceError('Speech recognition not supported in this browser. Please use Chrome or Edge.');
        setIsInitializing(false);
        return;
      }

      if (!('speechSynthesis' in window)) {
        setVoiceError('Speech synthesis not supported in this browser.');
        setIsInitializing(false);
        return;
      }

      // Initialize Speech Recognition
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      
      recognitionRef.current.continuous = true;
      recognitionRef.current.interimResults = true;
      recognitionRef.current.lang = 'en-US';
      recognitionRef.current.maxAlternatives = 1;

      // Set up recognition event handlers with improved logic
      recognitionRef.current.onstart = () => {
        console.log('Speech recognition started');
        setRecognitionState('active');
        setIsListening(true);
        setVoiceError(null);
        setRetryCount(0); // Reset retry count on successful start
      };

      recognitionRef.current.onresult = (event) => {
        let interimTranscript = '';
        let finalTranscript = '';

        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            finalTranscript += transcript;
          } else {
            interimTranscript += transcript;
          }
        }

        // Update interim transcript for live feedback
        setInterimTranscript(interimTranscript);
        setTranscript(finalTranscript + interimTranscript);
        
        // Detect if user is actively speaking
        const hasInterimText = interimTranscript.trim().length > 0;
        setIsUserSpeaking(hasInterimText || finalTranscript.trim().length > 0);
        
        // If user starts speaking while AI is speaking, interrupt
        if (hasInterimText && isSpeaking) {
          console.log('User interruption detected, stopping AI speech');
          setIsInterrupted(true);
          stopSpeaking();
        }

        // Process final transcript
        if (finalTranscript.trim()) {
          setInterimTranscript(''); // Clear interim when we have final
          setIsUserSpeaking(false);
          processVoiceInput(finalTranscript.trim());
        }
      };

      recognitionRef.current.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        const errorCategory = categorizeError(event.error);
        
        setRecognitionState('error');
        setIsListening(false);
        
        if (errorCategory === 'fatal') {
          setVoiceError(`Speech recognition error: ${event.error}. Please check microphone permissions.`);
          setAutoListen(false);
          setRetryCount(0);
        } else if (errorCategory === 'retryable' && retryCount < 5) {
          setVoiceError(`Temporary issue: ${event.error}. Retrying...`);
          handleRetryableError();
        } else {
          setVoiceError(`Speech recognition error: ${event.error}`);
          setAutoListen(false);
          setRetryCount(0);
        }
      };

      recognitionRef.current.onend = () => {
        console.log('Speech recognition ended');
        setRecognitionState('idle');
        setIsListening(false);
        setIsUserSpeaking(false);
        setInterimTranscript('');
        
        // Only auto-restart if conditions are met and we're not in an error state
        if (autoListen && 
            !isProcessing && 
            !isSpeaking && 
            !voiceError && 
            !isInterrupted &&
            recognitionState !== 'error' &&
            retryCount < 3) {
          
          // Clear any existing restart timeout
          if (restartTimeoutRef.current) {
            clearTimeout(restartTimeoutRef.current);
          }
          
          // Delayed restart to prevent rapid cycling
          restartTimeoutRef.current = setTimeout(() => {
            if (autoListen && !isProcessing && !isSpeaking && !voiceError && !isInterrupted) {
              startListening();
            }
          }, 1500); // Increased delay to prevent loops
        }
        
        // Reset interruption flag after a delay
        if (isInterrupted) {
          setTimeout(() => setIsInterrupted(false), 2000);
        }
      };

      // Initialize Speech Synthesis
      synthRef.current = window.speechSynthesis;
      
      // Load voices with multiple attempts
      loadVoices();
      
      if (synthRef.current.onvoiceschanged !== undefined) {
        synthRef.current.onvoiceschanged = loadVoices;
      }
      
      setTimeout(() => {
        loadVoices();
        setIsInitializing(false);
      }, 200);

    } catch (error) {
      console.error('Error initializing voice capabilities:', error);
      setVoiceError('Failed to initialize voice capabilities.');
      setIsInitializing(false);
    }
  };

  // Handle retryable errors with exponential backoff
  const handleRetryableError = () => {
    const delay = getRetryDelay(retryCount);
    
    setRetryCount(prev => prev + 1);
    
    if (retryTimeoutRef.current) {
      clearTimeout(retryTimeoutRef.current);
    }
    
    retryTimeoutRef.current = setTimeout(() => {
      if (autoListen && !isProcessing && !isSpeaking && retryCount < 5) {
        console.log(`Retrying speech recognition (attempt ${retryCount + 1})`);
        startListening();
      }
    }, delay);
  };

  const loadVoices = () => {
    const voices = synthRef.current.getVoices();
    const englishVoices = voices.filter(voice => voice.lang.startsWith('en'));
    setAvailableVoices(englishVoices);
    
    // Set default voice with better selection criteria
    if (!selectedVoice && englishVoices.length > 0) {
      // Try to find a good female voice first
      let preferredVoice = englishVoices.find(voice => 
        voice.lang === 'en-US' && 
        (voice.name.toLowerCase().includes('female') || voice.name.toLowerCase().includes('samantha') || voice.name.toLowerCase().includes('karen'))
      );
      
      // If no female voice, try any US English voice
      if (!preferredVoice) {
        preferredVoice = englishVoices.find(voice => voice.lang === 'en-US');
      }
      
      // If no US voice, pick the first English voice
      if (!preferredVoice) {
        preferredVoice = englishVoices[0];
      }
      
      setSelectedVoice(preferredVoice);
      console.log('Selected voice:', preferredVoice?.name);
    }
  };

  const initializeSession = () => {
    const newSessionId = 'voice_session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    setSessionId(newSessionId);
    
    // Add welcome message
    const welcomeMessage = {
      id: Date.now(),
      type: 'assistant',
      content: 'Hello! I\'m your AI legal assistant. You can ask me any legal questions using your voice. I have access to over 25,000 legal documents and can help with contracts, employment law, intellectual property, and much more. How can I help you today?',
      timestamp: new Date().toISOString(),
      confidence: null
    };
    
    setConversation([welcomeMessage]);
    
    // Ensure voices are loaded and speak the welcome message
    const speakWelcome = () => {
      if (synthRef.current && selectedVoice) {
        speakText(welcomeMessage.content);
      } else {
        // If voices aren't ready yet, try again in a moment
        setTimeout(() => {
          loadVoices();
          if (synthRef.current && selectedVoice) {
            speakText(welcomeMessage.content);
          }
        }, 500);
      }
    };
    
    // Speak the welcome message after a short delay
    setTimeout(speakWelcome, 800);
  };

  const startListening = () => {
    // Prevent multiple simultaneous start attempts
    if (recognitionState === 'starting' || recognitionState === 'active' || isProcessing || isSpeaking || isInitializing) {
      console.log('Start listening blocked:', { recognitionState, isProcessing, isSpeaking, isInitializing });
      return;
    }

    if (!recognitionRef.current) {
      console.warn('Recognition not initialized');
      setVoiceError('Voice recognition not properly initialized. Please reload the page.');
      return;
    }

    try {
      setRecognitionState('starting');
      setTranscript('');
      setVoiceError(null);
      
      // Small delay to ensure previous operations completed
      setTimeout(() => {
        if (recognitionRef.current && recognitionState === 'starting') {
          recognitionRef.current.start();
        }
      }, 100);
      
    } catch (error) {
      console.error('Error starting speech recognition:', error);
      setVoiceError('Could not start voice recognition. Please try again.');
      setRecognitionState('error');
      setIsListening(false);
    }
  };

  const stopListening = () => {
    if (recognitionRef.current && (recognitionState === 'active' || recognitionState === 'starting')) {
      try {
        setRecognitionState('stopping');
        recognitionRef.current.stop();
      } catch (error) {
        console.error('Error stopping speech recognition:', error);
        setRecognitionState('idle');
        setIsListening(false);
      }
    }
    
    // Clear any pending restart
    if (restartTimeoutRef.current) {
      clearTimeout(restartTimeoutRef.current);
      restartTimeoutRef.current = null;
    }
  };

  const speakText = (text) => {
    if (!synthRef.current) {
      console.warn('Speech synthesis not available');
      return;
    }

    if (!selectedVoice) {
      console.warn('No voice selected, loading voices...');
      loadVoices();
      setTimeout(() => {
        if (selectedVoice) {
          speakText(text);
        }
      }, 500);
      return;
    }

    // Stop any ongoing speech
    stopSpeaking();
    setIsInterrupted(false);

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.voice = selectedVoice;
    utterance.rate = speechRate;
    utterance.pitch = speechPitch;
    utterance.volume = voiceVolume;
    
    // Store reference for interruption capability
    currentUtteranceRef.current = utterance;

    utterance.onstart = () => {
      console.log('Started speaking:', text.substring(0, 50) + '...');
      setIsSpeaking(true);
      setCurrentSpeech(text);
      // Stop listening while speaking to prevent feedback
      if (recognitionState === 'active') {
        stopListening();
      }
    };

    utterance.onend = () => {
      console.log('Finished speaking');
      setIsSpeaking(false);
      setCurrentSpeech('');
      currentUtteranceRef.current = null;
      
      // Resume listening after speaking if auto-listen is enabled and not interrupted
      if (autoListen && !isProcessing && !voiceError && !isInterrupted) {
        setTimeout(() => {
          if (!isInterrupted) {
            startListening();
          }
        }, 800);
      }
    };

    utterance.onerror = (event) => {
      console.error('Speech synthesis error:', event.error);
      setIsSpeaking(false);
      setCurrentSpeech('');
      currentUtteranceRef.current = null;
      setVoiceError(`Speech error: ${event.error}`);
    };

    // Enable interruption detection
    utterance.onboundary = (event) => {
      // Check for interruption every word boundary
      if (isInterrupted && currentUtteranceRef.current) {
        synthRef.current.cancel();
        return;
      }
    };

    synthRef.current.speak(utterance);
  };

  const stopSpeaking = () => {
    if (synthRef.current) {
      synthRef.current.cancel();
      setIsSpeaking(false);
      setCurrentSpeech('');
      if (currentUtteranceRef.current) {
        currentUtteranceRef.current = null;
      }
    }
  };

  const processVoiceInput = async (input) => {
    if (!input.trim() || isProcessing) return;

    setIsProcessing(true);
    setTranscript('');
    setInterimTranscript('');
    setIsUserSpeaking(false);
    setLastUserIntent(input);

    // Add user message to conversation
    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: input,
      timestamp: new Date().toISOString()
    };

    setConversation(prev => [...prev, userMessage]);
    
    // Update conversation context
    setConversationContext(prev => [...prev, { role: 'user', content: input }]);

    try {
      // Call the legal Q&A API with enhanced parameters
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/legal-qa/ask`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          question: input,
          session_id: sessionId,
          jurisdiction: selectedJurisdiction,
          legal_domain: selectedDomain === 'all_domains' ? null : selectedDomain,
          is_voice: true,
          conversation_context: conversationContext.slice(-4) // Last 4 exchanges for context
        })
      });

      if (response.ok) {
        const result = await response.json();
        
        const assistantMessage = {
          id: Date.now() + 1,
          type: 'assistant',
          content: result.answer,
          timestamp: new Date().toISOString(),
          confidence: result.confidence,
          sources: result.sources || []
        };

        setConversation(prev => [...prev, assistantMessage]);
        
        // Update conversation context
        setConversationContext(prev => [...prev, { role: 'assistant', content: result.answer }]);
        
        // Generate contextual follow-up suggestions
        const followUps = generateFollowUpSuggestions(result.answer, input);
        setSuggestedFollowUps(followUps);
        
        // Update conversation summary
        updateConversationSummary(input, result.answer);

        // Speak the response with enhanced naturalness
        const enhancedResponse = enhanceResponseForSpeech(result.answer);
        speakText(enhancedResponse);
        
      } else {
        throw new Error('Failed to get response from legal assistant');
      }
    } catch (error) {
      console.error('Error processing voice input:', error);
      
      const errorMessage = {
        id: Date.now() + 1,
        type: 'error',
        content: 'I apologize, but I encountered an error processing your question. Could you please rephrase or try again?',
        timestamp: new Date().toISOString()
      };

      setConversation(prev => [...prev, errorMessage]);
      speakText(errorMessage.content);
    } finally {
      setIsProcessing(false);
    }
  };

  // Enhance response text for more natural speech
  const enhanceResponseForSpeech = (text) => {
    // Add natural pauses and improve flow for speech
    return text
      .replace(/\n\n/g, '. ') // Replace paragraph breaks with pauses
      .replace(/\n/g, ', ') // Replace line breaks with commas
      .replace(/\s+/g, ' ') // Normalize whitespace
      .replace(/([.!?])\s*([A-Z])/g, '$1 $2') // Ensure proper spacing after sentences
      .trim();
  };

  // Update conversation summary
  const updateConversationSummary = (question, answer) => {
    const topics = [];
    
    // Extract key legal topics from the conversation
    const legalKeywords = {
      'contract': 'Contract Law',
      'employment': 'Employment Law', 
      'intellectual property': 'IP Law',
      'trademark': 'Trademark Law',
      'copyright': 'Copyright Law',
      'llc': 'Business Formation',
      'corporation': 'Corporate Law',
      'liability': 'Liability Issues',
      'breach': 'Contract Breach',
      'termination': 'Employment Termination'
    };
    
    const combined = (question + ' ' + answer).toLowerCase();
    Object.entries(legalKeywords).forEach(([keyword, topic]) => {
      if (combined.includes(keyword) && !topics.includes(topic)) {
        topics.push(topic);
      }
    });
    
    if (topics.length > 0) {
      setConversationSummary(`Discussed: ${topics.join(', ')}`);
    }
  };

  const handleSampleQuestion = (question) => {
    processVoiceInput(question);
  };

  const resetConversation = () => {
    setConversation([]);
    setTranscript('');
    setRetryCount(0);
    setVoiceError(null);
    stopSpeaking();
    stopListening();
    
    // Clear all timeouts
    if (retryTimeoutRef.current) {
      clearTimeout(retryTimeoutRef.current);
      retryTimeoutRef.current = null;
    }
    if (restartTimeoutRef.current) {
      clearTimeout(restartTimeoutRef.current);
      restartTimeoutRef.current = null;
    }
    
    // Reinitialize session
    setTimeout(() => {
      initializeSession();
    }, 500);
  };

  const toggleAutoListen = () => {
    const newAutoListen = !autoListen;
    setAutoListen(newAutoListen);
    
    if (newAutoListen && recognitionState === 'idle' && !isProcessing && !isSpeaking) {
      setTimeout(() => {
        startListening();
      }, 500);
    } else if (!newAutoListen) {
      stopListening();
      // Clear retry attempts when auto-listen is disabled
      if (retryTimeoutRef.current) {
        clearTimeout(retryTimeoutRef.current);
        retryTimeoutRef.current = null;
      }
      setRetryCount(0);
    }
  };

  // Enhanced retry function
  const handleRetry = () => {
    setVoiceError(null);
    setRetryCount(0);
    setRecognitionState('idle');
    
    // Clear all timeouts
    if (retryTimeoutRef.current) {
      clearTimeout(retryTimeoutRef.current);
      retryTimeoutRef.current = null;
    }
    if (restartTimeoutRef.current) {
      clearTimeout(restartTimeoutRef.current);
      restartTimeoutRef.current = null;
    }
    
    // Reinitialize if needed
    if (!recognitionRef.current) {
      initializeVoiceCapabilities();
    } else {
      setAutoListen(true);
      if (!isProcessing && !isSpeaking) {
        setTimeout(() => {
          startListening();
        }, 800);
      }
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-4xl h-[90vh] flex flex-col bg-white"
            style={{ zIndex: 9999 }}>
        <CardHeader className="flex-shrink-0">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Bot className="h-6 w-6 text-purple-600" />
              <div>
                <CardTitle className="text-xl">AI Voice Legal Assistant</CardTitle>
                <CardDescription>Ask legal questions using your voice</CardDescription>
              </div>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={onClose}
              className="p-2"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>

          {voiceError && (
            <Alert className="mt-4">
              <AlertDescription>{voiceError}</AlertDescription>
            </Alert>
          )}
        </CardHeader>

        <CardContent className="flex-1 flex flex-col space-y-4 overflow-hidden">
          {/* Voice Controls */}
          <div className="flex-shrink-0 grid grid-cols-1 md:grid-cols-2 gap-4 p-4 bg-gray-50 rounded-lg">
            <div className="space-y-2">
              <h4 className="font-semibold text-sm">Voice Controls</h4>
              <div className="flex space-x-2">
                <Button
                  onClick={recognitionState === 'active' ? stopListening : startListening}
                  disabled={isProcessing || isInitializing || isSpeaking || recognitionState === 'starting' || recognitionState === 'stopping'}
                  className={`flex items-center space-x-2 ${
                    recognitionState === 'active' ? 'bg-red-600 hover:bg-red-700' : 'bg-blue-600 hover:bg-blue-700'
                  }`}
                  size="sm"
                >
                  {recognitionState === 'active' ? <MicOff className="h-4 w-4" /> : <Mic className="h-4 w-4" />}
                  <span>
                    {recognitionState === 'active' ? 'Stop' : 
                     recognitionState === 'starting' ? 'Starting...' :
                     recognitionState === 'stopping' ? 'Stopping...' : 
                     'Start'} Listening
                  </span>
                </Button>
                
                <Button
                  onClick={isSpeaking ? stopSpeaking : () => {}}
                  disabled={!isSpeaking}
                  variant={isSpeaking ? "destructive" : "outline"}
                  size="sm"
                >
                  {isSpeaking ? <VolumeX className="h-4 w-4" /> : <Volume2 className="h-4 w-4" />}
                  <span className="ml-1">{isSpeaking ? 'Stop' : 'Speak'}</span>
                </Button>

                <Button
                  onClick={resetConversation}
                  variant="outline"
                  size="sm"
                  disabled={isProcessing || isInitializing}
                >
                  <RotateCcw className="h-4 w-4" />
                  <span className="ml-1">Reset</span>
                </Button>

                {voiceError && (
                  <Button
                    onClick={handleRetry}
                    variant="outline"
                    size="sm"
                    className="bg-yellow-100 hover:bg-yellow-200"
                    disabled={isInitializing}
                  >
                    <Settings className="h-4 w-4" />
                    <span className="ml-1">{isInitializing ? 'Initializing...' : 'Retry'}</span>
                  </Button>
                )}
              </div>
              
              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="autoListen"
                  checked={autoListen}
                  onChange={toggleAutoListen}
                  disabled={isInitializing}
                  className="rounded"
                />
                <label htmlFor="autoListen" className="text-sm">Auto-listen after speaking</label>
                {retryCount > 0 && (
                  <span className="text-xs text-yellow-600">
                    (Retry {retryCount}/5)
                  </span>
                )}
              </div>
            </div>

            <div className="space-y-2">
              <h4 className="font-semibold text-sm">Settings</h4>
              <div className="grid grid-cols-1 gap-2">
                <div className="flex space-x-2">
                  <Select value={selectedJurisdiction} onValueChange={setSelectedJurisdiction}>
                    <SelectTrigger className="w-full">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {jurisdictions.map((jurisdiction) => (
                        <SelectItem key={jurisdiction.value} value={jurisdiction.value}>
                          {jurisdiction.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  
                  <Select value={selectedDomain} onValueChange={setSelectedDomain}>
                    <SelectTrigger className="w-full">
                      <SelectValue placeholder="Legal Domain" />
                    </SelectTrigger>
                    <SelectContent>
                      {legalDomains.map((domain) => (
                        <SelectItem key={domain.value} value={domain.value}>
                          {domain.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                
                {/* Voice Selection */}
                <div className="flex space-x-2">
                  <Select 
                    value={selectedVoice?.name || ''} 
                    onValueChange={(voiceName) => {
                      const voice = availableVoices.find(v => v.name === voiceName);
                      if (voice) {
                        setSelectedVoice(voice);
                        console.log('Voice changed to:', voice.name);
                      }
                    }}
                  >
                    <SelectTrigger className="w-full">
                      <SelectValue placeholder="Select Voice" />
                    </SelectTrigger>
                    <SelectContent>
                      {availableVoices.map((voice) => (
                        <SelectItem key={voice.name} value={voice.name}>
                          {voice.name} ({voice.lang})
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  
                  {/* Voice Test Button */}
                  <Button
                    onClick={() => {
                      if (selectedVoice) {
                        speakText('Hello, this is a voice test. How do I sound?');
                      }
                    }}
                    variant="outline"
                    size="sm"
                    disabled={!selectedVoice || isSpeaking}
                  >
                    <Volume2 className="h-4 w-4" />
                    Test
                  </Button>
                </div>
                
                {/* Voice Speed Control */}
                <div className="flex items-center space-x-2">
                  <label className="text-xs text-gray-600 w-16">Speed:</label>
                  <input
                    type="range"
                    min="0.5"
                    max="2"
                    step="0.1"
                    value={speechRate}
                    onChange={(e) => setSpeechRate(parseFloat(e.target.value))}
                    className="flex-1"
                  />
                  <span className="text-xs text-gray-600 w-8">{speechRate.toFixed(1)}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Status Indicators */}
          <div className="flex-shrink-0 flex items-center space-x-4 p-2 bg-white border rounded-lg">
            <div className="flex items-center space-x-2">
              <Activity className={`h-4 w-4 ${
                recognitionState === 'active' ? 'text-green-500 animate-pulse' : 
                recognitionState === 'starting' ? 'text-yellow-500 animate-pulse' :
                recognitionState === 'stopping' ? 'text-orange-500 animate-pulse' :
                'text-gray-400'
              }`} />
              <span className="text-sm">
                {recognitionState === 'active' ? 'Listening...' :
                 recognitionState === 'starting' ? 'Starting...' :
                 recognitionState === 'stopping' ? 'Stopping...' :
                 recognitionState === 'error' ? 'Error' :
                 'Not listening'}
              </span>
            </div>
            
            <div className="flex items-center space-x-2">
              <Volume2 className={`h-4 w-4 ${isSpeaking ? 'text-blue-500 animate-pulse' : 'text-gray-400'}`} />
              <span className="text-sm">{isSpeaking ? 'Speaking...' : 'Silent'}</span>
              {selectedVoice && !isSpeaking && (
                <span className="text-xs text-gray-500">({selectedVoice.name.split(' ')[0]})</span>
              )}
            </div>

            {isProcessing && (
              <div className="flex items-center space-x-2">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-purple-600"></div>
                <span className="text-sm">Processing...</span>
              </div>
            )}

            {isInitializing && (
              <div className="flex items-center space-x-2">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                <span className="text-sm">Initializing...</span>
              </div>
            )}

            {transcript && (
              <div className="text-sm text-blue-600 italic">
                Transcript: "{transcript}"
              </div>
            )}
          </div>

          {/* Conversation Area */}
          <div className="flex-1 overflow-y-auto bg-gray-50 rounded-lg p-4 space-y-4">
            {conversation.map((message) => (
              <div
                key={message.id}
                className={`flex items-start space-x-3 ${
                  message.type === 'user' ? 'flex-row-reverse space-x-reverse' : ''
                }`}
              >
                <div className={`flex-shrink-0 ${
                  message.type === 'user' 
                    ? 'bg-blue-600 text-white' 
                    : message.type === 'error'
                    ? 'bg-red-600 text-white'
                    : 'bg-purple-600 text-white'
                } rounded-full p-2`}>
                  {message.type === 'user' ? (
                    <User className="h-4 w-4" />
                  ) : (
                    <Bot className="h-4 w-4" />
                  )}
                </div>

                <div className={`flex-1 ${
                  message.type === 'user' ? 'text-right' : 'text-left'
                }`}>
                  <div className={`inline-block p-3 rounded-lg max-w-xs md:max-w-md lg:max-w-lg ${
                    message.type === 'user'
                      ? 'bg-blue-600 text-white'
                      : message.type === 'error'
                      ? 'bg-red-100 text-red-800'
                      : 'bg-white shadow-sm border'
                  }`}>
                    <div className="text-sm whitespace-pre-wrap">{message.content}</div>
                    {message.confidence && (
                      <div className="mt-2">
                        <Badge variant="outline" className="text-xs">
                          Confidence: {Math.round(message.confidence * 100)}%
                        </Badge>
                      </div>
                    )}
                  </div>
                  <div className="text-xs text-gray-500 mt-1">
                    {new Date(message.timestamp).toLocaleTimeString()}
                  </div>
                </div>
              </div>
            ))}
            <div ref={conversationEndRef} />
          </div>

          {/* Sample Questions */}
          <div className="flex-shrink-0 p-3 bg-white border rounded-lg">
            <h4 className="font-semibold text-sm mb-2">Try asking:</h4>
            <div className="flex flex-wrap gap-2">
              {sampleQuestions.slice(0, 3).map((question, index) => (
                <Button
                  key={index}
                  variant="outline"
                  size="sm"
                  onClick={() => handleSampleQuestion(question)}
                  disabled={isProcessing}
                  className="text-xs"
                >
                  {question}
                </Button>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default VoiceAgent;