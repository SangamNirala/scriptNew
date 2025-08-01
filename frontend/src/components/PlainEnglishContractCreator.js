import React, { useState, useCallback, useEffect } from 'react';
import axios from 'axios';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { Alert, AlertDescription } from './ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { 
  FileText, 
  Zap, 
  Download, 
  Eye, 
  ArrowLeft, 
  Lightbulb,
  CheckCircle,
  AlertTriangle,
  Copy,
  Edit,
  FileDown,
  Sparkles
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const PlainEnglishContractCreator = ({ onBack, contractTypes, jurisdictions }) => {
  const [inputText, setInputText] = useState('');
  const [selectedContractType, setSelectedContractType] = useState('auto_detect');
  const [selectedJurisdiction, setSelectedJurisdiction] = useState('US');
  const [selectedIndustry, setSelectedIndustry] = useState('general_business');
  const [outputFormat, setOutputFormat] = useState('legal_clauses');
  const [isProcessing, setIsProcessing] = useState(false);
  const [result, setResult] = useState(null);
  const [activeTab, setActiveTab] = useState('input');
  const [exportFormat, setExportFormat] = useState('pdf');
  const [isExporting, setIsExporting] = useState(false);
  const [conversions, setConversions] = useState([]);

  // Industry options
  const industries = [
    'Technology', 'Healthcare', 'Finance', 'Real Estate', 'Manufacturing',
    'Consulting', 'Marketing', 'Legal', 'Education', 'Retail', 'Construction',
    'Transportation', 'Entertainment', 'Food & Beverage', 'Other'
  ];

  // Example prompts to help users
  const examplePrompts = [
    "I want to hire a freelance web developer to build an e-commerce website for $10,000. The project should take 3 months, include responsive design, payment integration, and maintenance for 6 months after launch.",
    "I need a non-disclosure agreement for sharing my startup idea with potential investors. The information should remain confidential for 5 years and cover technical specifications, business plans, and financial projections.",
    "I want to partner with another company to jointly develop a mobile app. We'll split development costs 60/40, share revenues equally, and I'll handle marketing while they handle technical development.",
    "I need a contract for renting office space for my consulting business. Monthly rent is $3,000, 2-year lease, includes utilities, parking for 5 cars, and allows for small business signage."
  ];

  useEffect(() => {
    loadRecentConversions();
  }, []);

  const loadRecentConversions = async () => {
    try {
      const response = await axios.get(`${API}/plain-english-conversions`);
      setConversions(response.data.conversions || []);
    } catch (error) {
      console.error('Error loading recent conversions:', error);
    }
  };

  const handleConvert = async () => {
    if (!inputText.trim()) {
      alert('Please enter some text to convert to legal clauses.');
      return;
    }

    setIsProcessing(true);
    try {
      const response = await axios.post(`${API}/plain-english-to-legal`, {
        plain_text: inputText,
        contract_type: selectedContractType === 'auto_detect' ? null : selectedContractType || null,
        jurisdiction: selectedJurisdiction,
        industry: selectedIndustry === 'general_business' ? null : selectedIndustry || null,
        output_format: outputFormat
      });

      setResult(response.data);
      setActiveTab('results');
      loadRecentConversions(); // Refresh the list
    } catch (error) {
      console.error('Error converting plain English:', error);
      alert('Failed to convert plain English to legal clauses. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleExport = async (format) => {
    if (!result?.id) {
      alert('No conversion result to export');
      return;
    }

    setIsExporting(true);
    try {
      if (format === 'json') {
        const response = await axios.post(`${API}/plain-english-conversions/${result.id}/export?format=json`);
        
        // Download JSON file
        const dataStr = JSON.stringify(response.data, null, 2);
        const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
        
        const exportFileDefaultName = `legal_clauses_${result.id}.json`;
        const linkElement = document.createElement('a');
        linkElement.setAttribute('href', dataUri);
        linkElement.setAttribute('download', exportFileDefaultName);
        linkElement.click();

      } else if (format === 'pdf') {
        const response = await axios.post(`${API}/plain-english-conversions/${result.id}/export?format=pdf`, {}, {
          responseType: 'blob'
        });
        
        // Download PDF file
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `legal_clauses_${result.id}.pdf`);
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(url);

      } else if (format === 'docx') {
        // For DOCX, we get structured data and can implement frontend generation
        const response = await axios.post(`${API}/plain-english-conversions/${result.id}/export?format=docx`);
        alert('DOCX export data received. In a full implementation, this would generate a DOCX file using a library like docx.js');
        console.log('DOCX export data:', response.data);
      }

    } catch (error) {
      console.error('Error exporting:', error);
      alert('Failed to export. Please try again.');
    } finally {
      setIsExporting(false);
    }
  };

  const copyClauseToClipboard = (clause) => {
    navigator.clipboard.writeText(clause.content);
    alert('Clause copied to clipboard!');
  };

  const useExamplePrompt = (prompt) => {
    setInputText(prompt);
    setActiveTab('input');
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-4 mb-4">
            <Button variant="outline" onClick={onBack}>
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back
            </Button>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Plain English Contract Creator</h1>
              <p className="text-gray-600">Transform plain English into legally compliant contract clauses using AI</p>
            </div>
          </div>
          
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-start gap-3">
              <Sparkles className="h-5 w-5 text-blue-600 mt-0.5" />
              <div>
                <h3 className="font-semibold text-blue-900">How it works</h3>
                <p className="text-blue-700 text-sm">
                  Describe your contract needs in plain English, and our AI will convert it into professional legal clauses. 
                  You can then edit, export, and use these clauses in your contracts.
                </p>
              </div>
            </div>
          </div>
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="input">
              <Edit className="mr-2 h-4 w-4" />
              Input & Settings
            </TabsTrigger>
            <TabsTrigger value="results" disabled={!result}>
              <Eye className="mr-2 h-4 w-4" />
              Generated Clauses
            </TabsTrigger>
            <TabsTrigger value="history">
              <FileText className="mr-2 h-4 w-4" />
              Recent Conversions
            </TabsTrigger>
          </TabsList>

          {/* Input Tab */}
          <TabsContent value="input" className="mt-6">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Main Input */}
              <div className="lg:col-span-2">
                <Card>
                  <CardHeader>
                    <CardTitle>Describe Your Contract Needs</CardTitle>
                    <CardDescription>
                      Write in plain English what you want your contract to cover
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <Label htmlFor="plainText">Contract Description</Label>
                      <Textarea
                        id="plainText"
                        placeholder="Example: I want to hire a freelancer to design my company logo for $500. The work should be completed in 2 weeks and I want full ownership of the design..."
                        value={inputText}
                        onChange={(e) => setInputText(e.target.value)}
                        className="min-h-32"
                      />
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <Label htmlFor="contractType">Contract Type (Optional)</Label>
                        <Select value={selectedContractType} onValueChange={setSelectedContractType}>
                          <SelectTrigger>
                            <SelectValue placeholder="Auto-detect or select type" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="auto_detect">Auto-detect from description</SelectItem>
                            {contractTypes.map((type) => (
                              <SelectItem key={type.id} value={type.id}>
                                {type.name}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>

                      <div>
                        <Label htmlFor="jurisdiction">Jurisdiction</Label>
                        <Select value={selectedJurisdiction} onValueChange={setSelectedJurisdiction}>
                          <SelectTrigger>
                            <SelectValue placeholder="Select jurisdiction" />
                          </SelectTrigger>
                          <SelectContent>
                            {jurisdictions.filter(j => j.supported).map((jurisdiction) => (
                              <SelectItem key={jurisdiction.code} value={jurisdiction.code}>
                                {jurisdiction.name}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>

                      <div>
                        <Label htmlFor="industry">Industry (Optional)</Label>
                        <Select value={selectedIndustry} onValueChange={setSelectedIndustry}>
                          <SelectTrigger>
                            <SelectValue placeholder="Select industry" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="general_business">General Business</SelectItem>
                            {industries.map((industry) => (
                              <SelectItem key={industry} value={industry}>
                                {industry}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>

                      <div>
                        <Label htmlFor="outputFormat">Output Format</Label>
                        <Select value={outputFormat} onValueChange={setOutputFormat}>
                          <SelectTrigger>
                            <SelectValue placeholder="Select output format" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="legal_clauses">Individual Legal Clauses</SelectItem>
                            <SelectItem value="full_contract">Complete Contract</SelectItem>
                            <SelectItem value="json">Structured JSON</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                    </div>

                    <Button 
                      onClick={handleConvert}
                      disabled={isProcessing || !inputText.trim()}
                      className="w-full bg-blue-600 hover:bg-blue-700"
                      size="lg"
                    >
                      {isProcessing ? (
                        <>
                          <Zap className="mr-2 h-4 w-4 animate-spin" />
                          Converting to Legal Clauses...
                        </>
                      ) : (
                        <>
                          <FileText className="mr-2 h-4 w-4" />
                          Convert to Legal Clauses
                        </>
                      )}
                    </Button>
                  </CardContent>
                </Card>
              </div>

              {/* Examples Sidebar */}
              <div>
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Lightbulb className="h-4 w-4" />
                      Example Prompts
                    </CardTitle>
                    <CardDescription>Click to use these examples</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    {examplePrompts.map((prompt, index) => (
                      <div
                        key={index}
                        onClick={() => useExamplePrompt(prompt)}
                        className="p-3 bg-gray-50 rounded-lg cursor-pointer hover:bg-gray-100 transition-colors"
                      >
                        <p className="text-sm text-gray-700 line-clamp-3">
                          {prompt}
                        </p>
                      </div>
                    ))}
                  </CardContent>
                </Card>
              </div>
            </div>
          </TabsContent>

          {/* Results Tab */}
          <TabsContent value="results" className="mt-6">
            {result && (
              <div className="space-y-6">
                {/* Summary Card */}
                <Card>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <div>
                        <CardTitle>Conversion Results</CardTitle>
                        <CardDescription>
                          Generated {result.generated_clauses?.length || 0} legal clauses from your plain English description
                        </CardDescription>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge variant={result.confidence_score > 0.8 ? 'default' : 'secondary'}>
                          {(result.confidence_score * 100).toFixed(0)}% Confidence
                        </Badge>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <Progress value={result.confidence_score * 100} className="w-full mb-4" />
                    
                    {/* Original Text */}
                    <div className="mb-4">
                      <h4 className="font-semibold text-sm text-gray-700 mb-2">Original Description:</h4>
                      <div className="bg-gray-50 p-3 rounded border text-sm">
                        {result.original_text}
                      </div>
                    </div>

                    {/* Warnings */}
                    {result.legal_warnings?.length > 0 && (
                      <Alert className="mb-4">
                        <AlertTriangle className="h-4 w-4" />
                        <AlertDescription>
                          <strong>Legal Warnings:</strong> {result.legal_warnings.join(', ')}
                        </AlertDescription>
                      </Alert>
                    )}

                    {/* Export Options */}
                    <div className="flex flex-wrap gap-2">
                      <Button
                        onClick={() => handleExport('pdf')}
                        disabled={isExporting}
                        variant="outline"
                        size="sm"
                      >
                        <FileDown className="mr-2 h-4 w-4" />
                        Export PDF
                      </Button>
                      <Button
                        onClick={() => handleExport('json')}
                        disabled={isExporting}
                        variant="outline"
                        size="sm"
                      >
                        <FileDown className="mr-2 h-4 w-4" />
                        Export JSON
                      </Button>
                      <Button
                        onClick={() => handleExport('docx')}
                        disabled={isExporting}
                        variant="outline"
                        size="sm"
                      >
                        <FileDown className="mr-2 h-4 w-4" />
                        Export DOCX
                      </Button>
                    </div>
                  </CardContent>
                </Card>

                {/* Generated Clauses */}
                <div className="space-y-4">
                  <h3 className="text-xl font-semibold">Generated Legal Clauses</h3>
                  
                  {result.generated_clauses?.map((clause, index) => (
                    <Card key={index}>
                      <CardContent className="p-6">
                        <div className="flex items-start justify-between mb-3">
                          <div>
                            <h4 className="font-semibold text-lg">{clause.title}</h4>
                            <Badge variant="outline" className="mt-1">
                              {clause.clause_type}
                            </Badge>
                          </div>
                          <div className="flex items-center gap-2">
                            <Badge variant={clause.confidence > 0.8 ? 'default' : 'secondary'}>
                              {(clause.confidence * 100).toFixed(0)}%
                            </Badge>
                            <Button
                              onClick={() => copyClauseToClipboard(clause)}
                              variant="outline"
                              size="sm"
                            >
                              <Copy className="h-4 w-4" />
                            </Button>
                          </div>
                        </div>

                        <div className="space-y-4">
                          <div>
                            <h5 className="font-medium text-sm text-gray-700 mb-2">Legal Clause:</h5>
                            <div className="bg-gray-50 p-4 rounded border font-mono text-sm whitespace-pre-wrap">
                              {clause.content}
                            </div>
                          </div>

                          <div>
                            <h5 className="font-medium text-sm text-gray-700 mb-2">Explanation:</h5>
                            <p className="text-sm text-gray-600">{clause.explanation}</p>
                          </div>

                          {clause.suggestions?.length > 0 && (
                            <div>
                              <h5 className="font-medium text-sm text-gray-700 mb-2">Suggestions:</h5>
                              <ul className="text-sm text-gray-600 list-disc list-inside">
                                {clause.suggestions.map((suggestion, idx) => (
                                  <li key={idx}>{suggestion}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>

                {/* Full Contract (if generated) */}
                {result.full_contract && (
                  <Card>
                    <CardHeader>
                      <CardTitle>Complete Contract</CardTitle>
                      <CardDescription>Full contract document with all clauses integrated</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="bg-gray-50 p-4 rounded border max-h-96 overflow-y-auto">
                        <div className="font-mono text-sm whitespace-pre-wrap">
                          {result.full_contract}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                )}

                {/* Recommendations */}
                {result.recommendations?.length > 0 && (
                  <Card>
                    <CardHeader>
                      <CardTitle>Recommendations</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <ul className="space-y-2">
                        {result.recommendations.map((rec, index) => (
                          <li key={index} className="flex items-start gap-2">
                            <CheckCircle className="h-4 w-4 text-green-600 mt-0.5" />
                            <span className="text-sm">{rec}</span>
                          </li>
                        ))}
                      </ul>
                    </CardContent>
                  </Card>
                )}
              </div>
            )}
          </TabsContent>

          {/* History Tab */}
          <TabsContent value="history" className="mt-6">
            <Card>
              <CardHeader>
                <CardTitle>Recent Conversions</CardTitle>
                <CardDescription>Your previous plain English to legal clause conversions</CardDescription>
              </CardHeader>
              <CardContent>
                {conversions.length === 0 ? (
                  <div className="text-center py-12">
                    <FileText className="h-16 w-16 mx-auto text-gray-400 mb-4" />
                    <p className="text-gray-500">No conversions yet. Create your first one!</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {conversions.slice(0, 10).map((conversion, index) => (
                      <Card key={conversion.id || index} className="cursor-pointer hover:shadow-md transition-shadow">
                        <CardContent className="p-4">
                          <div className="flex items-center justify-between">
                            <div className="flex-1">
                              <p className="font-medium text-sm mb-1">
                                {conversion.original_text?.substring(0, 100)}...
                              </p>
                              <div className="flex items-center gap-2 text-xs text-gray-500">
                                <span>{new Date(conversion.created_at).toLocaleDateString()}</span>
                                <span>•</span>
                                <span>{conversion.generated_clauses?.length || 0} clauses</span>
                                <span>•</span>
                                <Badge variant="outline" className="text-xs">
                                  {conversion.jurisdiction}
                                </Badge>
                              </div>
                            </div>
                            <Badge variant={conversion.confidence_score > 0.8 ? 'default' : 'secondary'}>
                              {(conversion.confidence_score * 100).toFixed(0)}%
                            </Badge>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {/* Legal Disclaimer */}
        <div className="mt-8">
          <Alert>
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>
              <strong>Legal Disclaimer:</strong> This tool generates AI-powered legal clauses for informational purposes only and does not constitute legal advice. 
              Always consult with a qualified attorney before using these clauses in any legal agreement.
            </AlertDescription>
          </Alert>
        </div>
      </div>
    </div>
  );
};

export default PlainEnglishContractCreator;