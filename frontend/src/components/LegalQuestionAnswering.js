import React, { useState, useEffect, useRef } from 'react';
import { MessageCircle, Send, Bot, User, Clock, ChevronDown, Scale, Search, FileText, AlertCircle, CheckCircle, Loader2, ExternalLink, Gavel, Shield } from 'lucide-react';

const LegalQuestionAnswering = () => {
  const [messages, setMessages] = useState([]);
  const [currentQuestion, setCurrentQuestion] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [selectedJurisdiction, setSelectedJurisdiction] = useState('US');
  const [selectedDomain, setSelectedDomain] = useState('');
  const [ragStats, setRagStats] = useState(null);
  const [knowledgeBaseStats, setKnowledgeBaseStats] = useState(null);
  const [showInitializationPanel, setShowInitializationPanel] = useState(false);
  const [isInitializing, setIsInitializing] = useState(false);
  const messagesEndRef = useRef(null);

  const legalDomains = [
    { value: '', label: 'All Legal Areas' },
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

  const jurisdictions = [
    { value: 'US', label: 'United States' },
    { value: 'UK', label: 'United Kingdom' },
    { value: 'CA', label: 'Canada' },
    { value: 'AU', label: 'Australia' },
    { value: 'EU', label: 'European Union' },
    { value: 'IN', label: 'India' }
  ];

  const sampleQuestions = [
    "What are the key elements of a valid contract under US law?",
    "How does employment at-will doctrine work in different states?",
    "What is the difference between copyright and trademark protection?",
    "What are the requirements for forming an LLC in California?",
    "How does the doctrine of consideration apply in contract law?",
    "What are the main types of intellectual property protection?",
    "What are the legal requirements for terminating an employee?",
    "How do non-compete agreements work in different jurisdictions?"
  ];

  useEffect(() => {
    // Generate session ID
    setSessionId(generateSessionId());
    
    // Load system stats
    loadSystemStats();
    
    // Show welcome message
    setMessages([{
      id: Date.now(),
      type: 'system',
      content: '👋 Welcome to the Legal Question Answering Assistant! I can help you understand legal concepts, statutes, and case law. Please note that this is for informational purposes only and does not constitute legal advice.',
      timestamp: new Date().toISOString()
    }]);
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const generateSessionId = () => {
    return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const loadSystemStats = async () => {
    try {
      // Load RAG system stats
      const ragResponse = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/legal-qa/stats`);
      if (ragResponse.ok) {
        const ragData = await ragResponse.json();
        setRagStats(ragData);
      }

      // Load knowledge base stats
      const kbResponse = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/legal-qa/knowledge-base/stats`);
      if (kbResponse.ok) {
        const kbData = await kbResponse.json();
        setKnowledgeBaseStats(kbData);
      }
    } catch (error) {
      console.error('Error loading system stats:', error);
    }
  };

  const initializeKnowledgeBase = async () => {
    setIsInitializing(true);
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/legal-qa/initialize-knowledge-base`, {
        method: 'POST'
      });

      if (response.ok) {
        const result = await response.json();
        
        setMessages(prev => [...prev, {
          id: Date.now(),
          type: 'system',
          content: `✅ Knowledge base initialized successfully! ${result.knowledge_base_stats?.total_documents || 0} legal documents are now available for analysis.`,
          timestamp: new Date().toISOString()
        }]);

        // Reload stats
        await loadSystemStats();
      } else {
        throw new Error('Failed to initialize knowledge base');
      }
    } catch (error) {
      console.error('Error initializing knowledge base:', error);
      setMessages(prev => [...prev, {
        id: Date.now(),
        type: 'system',
        content: '❌ Failed to initialize knowledge base. Please try again later.',
        timestamp: new Date().toISOString()
      }]);
    } finally {
      setIsInitializing(false);
      setShowInitializationPanel(false);
    }
  };

  const askQuestion = async (question) => {
    if (!question.trim()) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: question,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setCurrentQuestion('');
    setIsLoading(true);

    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/legal-qa/ask`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          question: question,
          session_id: sessionId,
          jurisdiction: selectedJurisdiction,
          legal_domain: selectedDomain || null
        })
      });

      if (response.ok) {
        const result = await response.json();
        
        const assistantMessage = {
          id: Date.now() + 1,
          type: 'assistant',
          content: result.answer,
          confidence: result.confidence,
          sources: result.sources || [],
          retrievedDocuments: result.retrieved_documents,
          modelUsed: result.model_used,
          timestamp: result.timestamp
        };

        setMessages(prev => [...prev, assistantMessage]);
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to get answer');
      }
    } catch (error) {
      console.error('Error asking question:', error);
      
      const errorMessage = {
        id: Date.now() + 1,
        type: 'error',
        content: `❌ Sorry, I encountered an error while processing your question: ${error.message}. Please try again.`,
        timestamp: new Date().toISOString()
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    askQuestion(currentQuestion);
  };

  const handleSampleQuestion = (question) => {
    askQuestion(question);
  };

  const formatConfidence = (confidence) => {
    const percentage = Math.round(confidence * 100);
    if (percentage >= 80) return { label: 'HIGH', color: 'text-green-600', bg: 'bg-green-100' };
    if (percentage >= 60) return { label: 'MEDIUM', color: 'text-yellow-600', bg: 'bg-yellow-100' };
    return { label: 'LOW', color: 'text-red-600', bg: 'bg-red-100' };
  };

  const convertMarkdownToHtml = (text) => {
    if (!text) return '';
    
    let html = text;
    
    // Convert **text** to <strong>text</strong>
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // Convert line breaks to <br> tags
    html = html.replace(/\n/g, '<br>');
    
    // Convert numbered lists (1. item) to proper HTML lists
    html = html.replace(/^(\d+)\.\s+(.+)$/gm, '<div class="mb-2"><span class="font-semibold text-gray-700">$1.</span> $2</div>');
    
    // Convert bullet points (* item) to proper HTML
    html = html.replace(/^\*\s+(.+)$/gm, '<div class="mb-1 ml-4">• $1</div>');
    
    // Convert pipe tables to HTML tables
    if (html.includes('|')) {
      html = convertPipeTableToHtml(html);
    }
    
    return html;
  };

  const convertPipeTableToHtml = (text) => {
    const lines = text.split('<br>');
    let inTable = false;
    let tableRows = [];
    let result = [];
    
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i].trim();
      
      if (line.includes('|') && line.split('|').length > 2) {
        // This looks like a table row
        if (!inTable) {
          inTable = true;
          tableRows = [];
        }
        
        const cells = line.split('|').map(cell => cell.trim()).filter(cell => cell !== '');
        tableRows.push(cells);
        
        // Check if next line is a separator (like |---|---|)
        if (i + 1 < lines.length && lines[i + 1].includes('---')) {
          i++; // Skip the separator line
        }
      } else {
        // Not a table row
        if (inTable) {
          // End of table, convert accumulated rows to HTML
          result.push(convertTableRowsToHtml(tableRows));
          tableRows = [];
          inTable = false;
        }
        result.push(line);
      }
    }
    
    // Handle table at end of text
    if (inTable && tableRows.length > 0) {
      result.push(convertTableRowsToHtml(tableRows));
    }
    
    return result.join('<br>');
  };

  const convertTableRowsToHtml = (rows) => {
    if (rows.length === 0) return '';
    
    let html = '<table class="min-w-full mt-4 mb-4 border-collapse border border-gray-300">';
    
    // First row is header
    if (rows.length > 0) {
      html += '<thead><tr>';
      rows[0].forEach(cell => {
        html += `<th class="border border-gray-300 px-3 py-2 bg-gray-100 font-semibold text-left">${cell}</th>`;
      });
      html += '</tr></thead>';
    }
    
    // Remaining rows are body
    if (rows.length > 1) {
      html += '<tbody>';
      for (let i = 1; i < rows.length; i++) {
        html += '<tr>';
        rows[i].forEach(cell => {
          html += `<td class="border border-gray-300 px-3 py-2">${cell}</td>`;
        });
        html += '</tr>';
      }
      html += '</tbody>';
    }
    
    html += '</table>';
    return html;
  };

  const shouldShowMetadata = (message) => {
    // Don't show metadata for simple greetings (handled by greeting_handler)
    if (message.modelUsed === 'greeting_handler') {
      return false;
    }
    
    // Don't show metadata if there are no sources and confidence is exactly 1.0 (likely a greeting)
    if (message.confidence === 1.0 && (!message.sources || message.sources.length === 0) && (!message.retrievedDocuments || message.retrievedDocuments === 0)) {
      return false;
    }
    
    return true;
  };

  const renderMessage = (message) => {
    switch (message.type) {
      case 'user':
        return (
          <div key={message.id} className="flex justify-end mb-4">
            <div className="flex items-start space-x-2 max-w-3xl">
              <div className="bg-blue-600 text-white rounded-lg px-4 py-3 shadow-sm">
                <p className="text-sm">{message.content}</p>
              </div>
              <div className="flex-shrink-0 w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                <User className="w-4 h-4 text-blue-600" />
              </div>
            </div>
          </div>
        );

      case 'assistant':
        const confidenceInfo = formatConfidence(message.confidence);
        const shouldShowMeta = shouldShowMetadata(message);
        const formattedContent = convertMarkdownToHtml(message.content);
        
        return (
          <div key={message.id} className="flex justify-start mb-6">
            <div className="flex items-start space-x-3 max-w-4xl">
              <div className="flex-shrink-0 w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
                <Scale className="w-4 h-4 text-purple-600" />
              </div>
              <div className="bg-white border border-gray-200 rounded-lg px-4 py-3 shadow-sm">
                <div className="prose prose-sm max-w-none">
                  <div 
                    className="text-gray-800 leading-relaxed"
                    dangerouslySetInnerHTML={{ __html: formattedContent }}
                  />
                </div>
                
                {/* Answer Metadata - Only show for actual legal questions */}
                {shouldShowMeta && (
                  <div className="mt-4 pt-3 border-t border-gray-100">
                    <div className="flex flex-wrap items-center gap-4 text-xs text-gray-500">
                      <div className="flex items-center space-x-1">
                        <CheckCircle className="w-3 h-3" />
                        <span>Confidence:</span>
                        <span className={`px-1.5 py-0.5 rounded text-xs font-medium ${confidenceInfo.bg} ${confidenceInfo.color}`}>
                          {confidenceInfo.label} ({Math.round(message.confidence * 100)}%)
                        </span>
                      </div>
                      {message.retrievedDocuments > 0 && (
                        <div className="flex items-center space-x-1">
                          <FileText className="w-3 h-3" />
                          <span>{message.retrievedDocuments} sources analyzed</span>
                        </div>
                      )}
                      {message.modelUsed && message.modelUsed !== 'greeting_handler' && (
                        <div className="flex items-center space-x-1">
                          <Bot className="w-3 h-3" />
                          <span>{message.modelUsed}</span>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Sources - Only show for actual legal questions */}
                {shouldShowMeta && message.sources && message.sources.length > 0 && (
                  <div className="mt-4 pt-3 border-t border-gray-100">
                    <h4 className="text-sm font-medium text-gray-700 mb-2 flex items-center">
                      <FileText className="w-4 h-4 mr-1" />
                      Legal Sources Referenced:
                    </h4>
                    <div className="space-y-2">
                      {message.sources.slice(0, 3).map((source, index) => (
                        <div key={index} className="bg-gray-50 rounded p-2 text-xs">
                          <div className="font-medium text-gray-800">{source.title}</div>
                          <div className="text-gray-600 mt-1">
                            {source.jurisdiction && (
                              <span className="inline-block bg-blue-100 text-blue-800 px-1.5 py-0.5 rounded mr-2">
                                {source.jurisdiction}
                              </span>
                            )}
                            {source.legal_domain && (
                              <span className="inline-block bg-green-100 text-green-800 px-1.5 py-0.5 rounded mr-2">
                                {source.legal_domain.replace('_', ' ')}
                              </span>
                            )}
                            {source.source && (
                              <span className="text-gray-500">Source: {source.source}</span>
                            )}
                          </div>
                          {source.url && (
                            <a 
                              href={source.url} 
                              target="_blank" 
                              rel="noopener noreferrer"
                              className="inline-flex items-center text-blue-600 hover:text-blue-800 mt-1"
                            >
                              <ExternalLink className="w-3 h-3 mr-1" />
                              View Source
                            </a>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        );

      case 'system':
        return (
          <div key={message.id} className="flex justify-center mb-4">
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg px-4 py-2 max-w-2xl">
              <p className="text-sm text-yellow-800 text-center">{message.content}</p>
            </div>
          </div>
        );

      case 'error':
        return (
          <div key={message.id} className="flex justify-start mb-4">
            <div className="flex items-start space-x-2 max-w-3xl">
              <div className="flex-shrink-0 w-8 h-8 bg-red-100 rounded-full flex items-center justify-center">
                <AlertCircle className="w-4 h-4 text-red-600" />
              </div>
              <div className="bg-red-50 border border-red-200 text-red-800 rounded-lg px-4 py-3">
                <p className="text-sm">{message.content}</p>
              </div>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="max-w-6xl mx-auto p-6">
      {/* Header */}
      <div className="mb-8 text-center">
        <div className="flex items-center justify-center mb-4">
          <div className="bg-purple-100 p-3 rounded-full mr-4">
            <Gavel className="w-8 h-8 text-purple-600" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Legal Question Answering</h1>
            <p className="text-gray-600 mt-2">AI-powered legal research with RAG technology</p>
          </div>
        </div>
        
        {/* System Status */}
        <div className="flex items-center justify-center space-x-6 text-sm text-gray-600">
          {ragStats && (
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-green-400 rounded-full"></div>
              <span>RAG System Active</span>
            </div>
          )}
          {knowledgeBaseStats && (
            <div className="flex items-center space-x-2">
              <FileText className="w-4 h-4" />
              <span>{knowledgeBaseStats.total_documents} Legal Documents</span>
            </div>
          )}
          <button
            onClick={() => setShowInitializationPanel(!showInitializationPanel)}
            className="flex items-center space-x-1 text-blue-600 hover:text-blue-800"
          >
            <Bot className="w-4 h-4" />
            <span>System Settings</span>
            <ChevronDown className={`w-4 h-4 transition-transform ${showInitializationPanel ? 'rotate-180' : ''}`} />
          </button>
        </div>

        {/* System Settings Panel */}
        {showInitializationPanel && (
          <div className="mt-4 bg-gray-50 rounded-lg p-6 border">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="text-lg font-semibold mb-3">Knowledge Base Status</h3>
                {knowledgeBaseStats ? (
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span>Total Documents:</span>
                      <span className="font-medium">{knowledgeBaseStats.total_documents}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>US Federal:</span>
                      <span>{knowledgeBaseStats.by_jurisdiction?.us_federal || 0}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>US State Laws:</span>
                      <span>{(knowledgeBaseStats.by_jurisdiction?.us_california || 0) + (knowledgeBaseStats.by_jurisdiction?.us_new_york || 0) + (knowledgeBaseStats.by_jurisdiction?.us_texas || 0)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>India Central:</span>
                      <span>{knowledgeBaseStats.by_jurisdiction?.india_central || 0}</span>
                    </div>
                  </div>
                ) : (
                  <p className="text-gray-500">No knowledge base loaded</p>
                )}
              </div>
              
              <div>
                <h3 className="text-lg font-semibold mb-3">System Actions</h3>
                <div className="space-y-2">
                  <button
                    onClick={initializeKnowledgeBase}
                    disabled={isInitializing}
                    className="w-full bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                  >
                    {isInitializing ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        Initializing...
                      </>
                    ) : (
                      <>
                        <Search className="w-4 h-4 mr-2" />
                        Initialize Knowledge Base
                      </>
                    )}
                  </button>
                  <p className="text-xs text-gray-500">
                    This will collect and index legal documents from authoritative sources
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Sidebar */}
        <div className="lg:col-span-1 space-y-6">
          {/* Query Configuration */}
          <div className="bg-white rounded-lg border p-4">
            <h3 className="font-semibold text-gray-900 mb-4 flex items-center">
              <Shield className="w-4 h-4 mr-2" />
              Query Settings
            </h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Jurisdiction
                </label>
                <select
                  value={selectedJurisdiction}
                  onChange={(e) => setSelectedJurisdiction(e.target.value)}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  {jurisdictions.map(jurisdiction => (
                    <option key={jurisdiction.value} value={jurisdiction.value}>
                      {jurisdiction.label}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Legal Domain
                </label>
                <select
                  value={selectedDomain}
                  onChange={(e) => setSelectedDomain(e.target.value)}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  {legalDomains.map(domain => (
                    <option key={domain.value} value={domain.value}>
                      {domain.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          {/* Sample Questions */}
          <div className="bg-white rounded-lg border p-4">
            <h3 className="font-semibold text-gray-900 mb-4">Sample Questions</h3>
            <div className="space-y-2">
              {sampleQuestions.slice(0, 6).map((question, index) => (
                <button
                  key={index}
                  onClick={() => handleSampleQuestion(question)}
                  className="w-full text-left text-sm text-gray-600 hover:text-blue-600 hover:bg-blue-50 p-2 rounded transition-colors"
                  disabled={isLoading}
                >
                  {question}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Main Chat Area */}
        <div className="lg:col-span-3">
          <div className="bg-white rounded-lg border shadow-sm flex flex-col h-[600px]">
            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto p-6 space-y-4">
              {messages.map(renderMessage)}
              {isLoading && (
                <div className="flex justify-start">
                  <div className="flex items-start space-x-3">
                    <div className="flex-shrink-0 w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
                      <Scale className="w-4 h-4 text-purple-600" />
                    </div>
                    <div className="bg-white border border-gray-200 rounded-lg px-4 py-3">
                      <div className="flex items-center space-x-2 text-gray-500">
                        <Loader2 className="w-4 h-4 animate-spin" />
                        <span className="text-sm">Analyzing legal sources and generating response...</span>
                      </div>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="border-t p-4">
              <form onSubmit={handleSubmit} className="flex space-x-3">
                <div className="flex-1">
                  <input
                    type="text"
                    value={currentQuestion}
                    onChange={(e) => setCurrentQuestion(e.target.value)}
                    placeholder="Ask a legal question..."
                    className="w-full border border-gray-300 rounded-lg px-4 py-3 focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                    disabled={isLoading}
                  />
                </div>
                <button
                  type="submit"
                  disabled={isLoading || !currentQuestion.trim()}
                  className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
                >
                  <Send className="w-4 h-4" />
                </button>
              </form>
              
              <p className="text-xs text-gray-500 mt-2 text-center">
                This system provides informational content only and does not constitute legal advice.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LegalQuestionAnswering;