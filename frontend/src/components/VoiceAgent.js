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
  
  // Refs
  const recognitionRef = useRef(null);
  const synthRef = useRef(null);
  const conversationEndRef = useRef(null);

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
    "What are the legal requirements for terminating an employee?"
  ];

  // Initialize voice capabilities and session
  useEffect(() => {
    initializeVoiceCapabilities();
    initializeSession();
    
    return () => {
      stopListening();
      stopSpeaking();
    };
  }, []);

  // Scroll to bottom when conversation updates
  useEffect(() => {
    conversationEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [conversation]);

  const initializeVoiceCapabilities = () => {
    try {
      // Check for Web Speech API support
      if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        setVoiceError('Speech recognition not supported in this browser. Please use Chrome or Edge.');
        return;
      }

      if (!('speechSynthesis' in window)) {
        setVoiceError('Speech synthesis not supported in this browser.');
        return;
      }

      // Initialize Speech Recognition
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      
      recognitionRef.current.continuous = true;
      recognitionRef.current.interimResults = true;
      recognitionRef.current.lang = 'en-US';

      // Set up recognition event handlers
      recognitionRef.current.onstart = () => {
        setIsListening(true);
        setVoiceError(null);
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

        setTranscript(finalTranscript + interimTranscript);

        // Process final transcript
        if (finalTranscript.trim()) {
          processVoiceInput(finalTranscript.trim());
        }
      };

      recognitionRef.current.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        setVoiceError(`Speech recognition error: ${event.error}`);
        setIsListening(false);
      };

      recognitionRef.current.onend = () => {
        setIsListening(false);
        // Auto-restart listening if enabled and not processing
        if (autoListen && !isProcessing) {
          setTimeout(() => {
            startListening();
          }, 500);
        }
      };

      // Initialize Speech Synthesis
      synthRef.current = window.speechSynthesis;
      loadVoices();

      // Load voices when they become available
      if (synthRef.current.onvoiceschanged !== undefined) {
        synthRef.current.onvoiceschanged = loadVoices;
      }

    } catch (error) {
      console.error('Error initializing voice capabilities:', error);
      setVoiceError('Failed to initialize voice capabilities.');
    }
  };

  const loadVoices = () => {
    const voices = synthRef.current.getVoices();
    const englishVoices = voices.filter(voice => voice.lang.startsWith('en'));
    setAvailableVoices(englishVoices);
    
    // Set default voice (prefer female, US English)
    if (!selectedVoice && englishVoices.length > 0) {
      const preferredVoice = englishVoices.find(voice => 
        voice.lang === 'en-US' && voice.name.toLowerCase().includes('female')
      ) || englishVoices.find(voice => voice.lang === 'en-US') || englishVoices[0];
      
      setSelectedVoice(preferredVoice);
    }
  };

  const initializeSession = () => {
    const newSessionId = 'voice_session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    setSessionId(newSessionId);
    
    // Add welcome message
    const welcomeMessage = {
      id: Date.now(),
      type: 'assistant',
      content: 'Hello! I\'m your AI legal assistant. You can ask me any legal questions using your voice. I have access to over 25,000 legal documents. How can I help you today?',
      timestamp: new Date().toISOString(),
      confidence: null
    };
    
    setConversation([welcomeMessage]);
    
    // Speak the welcome message
    setTimeout(() => {
      speakText(welcomeMessage.content);
    }, 1000);
  };

  const startListening = () => {
    if (recognitionRef.current && !isListening && !isProcessing) {
      try {
        setTranscript('');
        recognitionRef.current.start();
      } catch (error) {
        console.error('Error starting speech recognition:', error);
        setVoiceError('Could not start voice recognition. Please try again.');
      }
    }
  };

  const stopListening = () => {
    if (recognitionRef.current && isListening) {
      recognitionRef.current.stop();
    }
  };

  const speakText = (text) => {
    if (!synthRef.current || !selectedVoice) return;

    // Stop any ongoing speech
    synthRef.current.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.voice = selectedVoice;
    utterance.rate = speechRate;
    utterance.pitch = speechPitch;
    utterance.volume = voiceVolume;

    utterance.onstart = () => {
      setIsSpeaking(true);
      setCurrentSpeech(text);
      // Stop listening while speaking
      if (isListening) {
        stopListening();
      }
    };

    utterance.onend = () => {
      setIsSpeaking(false);
      setCurrentSpeech('');
      // Resume listening after speaking if auto-listen is enabled
      if (autoListen && !isProcessing) {
        setTimeout(() => {
          startListening();
        }, 500);
      }
    };

    utterance.onerror = (event) => {
      console.error('Speech synthesis error:', event.error);
      setIsSpeaking(false);
      setCurrentSpeech('');
    };

    synthRef.current.speak(utterance);
  };

  const stopSpeaking = () => {
    if (synthRef.current) {
      synthRef.current.cancel();
      setIsSpeaking(false);
      setCurrentSpeech('');
    }
  };

  const processVoiceInput = async (input) => {
    if (!input.trim() || isProcessing) return;

    setIsProcessing(true);
    setTranscript('');

    // Add user message to conversation
    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: input,
      timestamp: new Date().toISOString()
    };

    setConversation(prev => [...prev, userMessage]);

    try {
      // Call the legal Q&A API
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/legal-qa/ask`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          question: input,
          session_id: sessionId,
          jurisdiction: selectedJurisdiction,
          legal_domain: selectedDomain === 'all_domains' ? null : selectedDomain
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

        // Speak the response
        speakText(result.answer);
        
      } else {
        throw new Error('Failed to get response from legal assistant');
      }
    } catch (error) {
      console.error('Error processing voice input:', error);
      
      const errorMessage = {
        id: Date.now() + 1,
        type: 'error',
        content: 'I apologize, but I encountered an error processing your question. Please try again.',
        timestamp: new Date().toISOString()
      };

      setConversation(prev => [...prev, errorMessage]);
      speakText(errorMessage.content);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleSampleQuestion = (question) => {
    processVoiceInput(question);
  };

  const resetConversation = () => {
    setConversation([]);
    setTranscript('');
    stopSpeaking();
    stopListening();
    initializeSession();
  };

  const toggleAutoListen = () => {
    setAutoListen(!autoListen);
    if (!autoListen && !isListening && !isProcessing) {
      startListening();
    } else if (autoListen && isListening) {
      stopListening();
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
                  onClick={isListening ? stopListening : startListening}
                  disabled={isProcessing || !!voiceError}
                  className={`flex items-center space-x-2 ${
                    isListening ? 'bg-red-600 hover:bg-red-700' : 'bg-blue-600 hover:bg-blue-700'
                  }`}
                  size="sm"
                >
                  {isListening ? <MicOff className="h-4 w-4" /> : <Mic className="h-4 w-4" />}
                  <span>{isListening ? 'Stop' : 'Start'} Listening</span>
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
                >
                  <RotateCcw className="h-4 w-4" />
                  <span className="ml-1">Reset</span>
                </Button>
              </div>
              
              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="autoListen"
                  checked={autoListen}
                  onChange={toggleAutoListen}
                  className="rounded"
                />
                <label htmlFor="autoListen" className="text-sm">Auto-listen after speaking</label>
              </div>
            </div>

            <div className="space-y-2">
              <h4 className="font-semibold text-sm">Settings</h4>
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
            </div>
          </div>

          {/* Status Indicators */}
          <div className="flex-shrink-0 flex items-center space-x-4 p-2 bg-white border rounded-lg">
            <div className="flex items-center space-x-2">
              <Activity className={`h-4 w-4 ${isListening ? 'text-green-500 animate-pulse' : 'text-gray-400'}`} />
              <span className="text-sm">{isListening ? 'Listening...' : 'Not listening'}</span>
            </div>
            
            <div className="flex items-center space-x-2">
              <Volume2 className={`h-4 w-4 ${isSpeaking ? 'text-blue-500 animate-pulse' : 'text-gray-400'}`} />
              <span className="text-sm">{isSpeaking ? 'Speaking...' : 'Silent'}</span>
            </div>

            {isProcessing && (
              <div className="flex items-center space-x-2">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-purple-600"></div>
                <span className="text-sm">Processing...</span>
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