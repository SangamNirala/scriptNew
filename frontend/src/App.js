import React, { useState, useEffect, useCallback, memo } from 'react';
import './App.css';
import axios from 'axios';
import { Button } from './components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/card';
import { Input } from './components/ui/input';
import { Label } from './components/ui/label';
import { Textarea } from './components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './components/ui/select';
import { Badge } from './components/ui/badge';
import { Progress } from './components/ui/progress';
import { Alert, AlertDescription } from './components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs';
import { FileText, Zap, Shield, Users, CheckCircle, AlertTriangle, Download, Eye } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function App() {
  const [contractTypes, setContractTypes] = useState([]);
  const [jurisdictions, setJurisdictions] = useState([]);
  const [currentStep, setCurrentStep] = useState(1);
  const [contractData, setContractData] = useState({
    contract_type: '',
    jurisdiction: 'US',
    parties: {},
    terms: {},
    special_clauses: []
  });
  const [generatedContract, setGeneratedContract] = useState(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [contracts, setContracts] = useState([]);

  useEffect(() => {
    loadContractTypes();
    loadJurisdictions();
    loadContracts();
  }, []);

  const loadContractTypes = async () => {
    try {
      const response = await axios.get(`${API}/contract-types`);
      setContractTypes(response.data.types);
    } catch (error) {
      console.error('Error loading contract types:', error);
    }
  };

  const loadJurisdictions = async () => {
    try {
      const response = await axios.get(`${API}/jurisdictions`);
      setJurisdictions(response.data.jurisdictions);
    } catch (error) {
      console.error('Error loading jurisdictions:', error);
    }
  };

  const loadContracts = async () => {
    try {
      const response = await axios.get(`${API}/contracts`);
      setContracts(response.data);
    } catch (error) {
      console.error('Error loading contracts:', error);
    }
  };

  const generateContract = useCallback(async () => {
    setIsGenerating(true);
    try {
      const response = await axios.post(`${API}/generate-contract`, contractData);
      setGeneratedContract(response.data);
      setCurrentStep(4);
      loadContracts(); // Refresh the contracts list
    } catch (error) {
      console.error('Error generating contract:', error);
      alert('Failed to generate contract. Please try again.');
    } finally {
      setIsGenerating(false);
    }
  }, [contractData]);

  const updateParties = useCallback((field, value) => {
    setContractData(prev => ({
      ...prev,
      parties: { ...prev.parties, [field]: value }
    }));
  }, []);

  const updateTerms = useCallback((field, value) => {
    setContractData(prev => ({
      ...prev,
      terms: { ...prev.terms, [field]: value }
    }));
  }, []);

  const ContractTypeStep = () => (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader className="text-center">
        <CardTitle className="text-2xl">Choose Contract Type</CardTitle>
        <CardDescription>Select the type of legal document you need</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid gap-4">
          {contractTypes.map((type) => (
            <Card 
              key={type.id}
              className={`cursor-pointer transition-all hover:shadow-md ${
                contractData.contract_type === type.id ? 'ring-2 ring-blue-500 bg-blue-50' : ''
              }`}
              onClick={() => setContractData(prev => ({ ...prev, contract_type: type.id }))}
            >
              <CardContent className="p-4">
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="font-semibold text-lg">{type.name}</h3>
                    <p className="text-gray-600 mt-1">{type.description}</p>
                  </div>
                  <Badge variant={type.complexity === 'Simple' ? 'secondary' : 
                                type.complexity === 'Medium' ? 'default' : 'destructive'}>
                    {type.complexity}
                  </Badge>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
        
        {contractData.contract_type && (
          <div className="mt-6">
            <Label htmlFor="jurisdiction">Jurisdiction</Label>
            <Select value={contractData.jurisdiction} onValueChange={(value) => 
              setContractData(prev => ({ ...prev, jurisdiction: value }))
            }>
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
        )}

        <Button 
          onClick={() => setCurrentStep(2)} 
          disabled={!contractData.contract_type}
          className="w-full mt-6"
        >
          Next: Party Information
        </Button>
      </CardContent>
    </Card>
  );

  const PartiesStep = memo(() => (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle className="text-2xl">Party Information</CardTitle>
        <CardDescription>Enter details about the parties involved</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <Label htmlFor="party1_name">Party 1 Name</Label>
            <Input 
              key="party1_name"
              id="party1_name"
              placeholder="Company or Individual Name"
              value={contractData.parties.party1_name || ''}
              onChange={(e) => updateParties('party1_name', e.target.value)}
            />
          </div>
          <div>
            <Label htmlFor="party1_type">Party 1 Type</Label>
            <Select value={contractData.parties.party1_type || ''} onValueChange={(value) => 
              updateParties('party1_type', value)
            }>
              <SelectTrigger>
                <SelectValue placeholder="Select type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="individual">Individual</SelectItem>
                <SelectItem value="company">Company</SelectItem>
                <SelectItem value="llc">LLC</SelectItem>
                <SelectItem value="corporation">Corporation</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div>
            <Label htmlFor="party2_name">Party 2 Name</Label>
            <Input 
              key="party2_name"
              id="party2_name"
              placeholder="Company or Individual Name"
              value={contractData.parties.party2_name || ''}
              onChange={(e) => updateParties('party2_name', e.target.value)}
            />
          </div>
          <div>
            <Label htmlFor="party2_type">Party 2 Type</Label>
            <Select value={contractData.parties.party2_type || ''} onValueChange={(value) => 
              updateParties('party2_type', value)
            }>
              <SelectTrigger>
                <SelectValue placeholder="Select type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="individual">Individual</SelectItem>
                <SelectItem value="company">Company</SelectItem>
                <SelectItem value="llc">LLC</SelectItem>
                <SelectItem value="corporation">Corporation</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        <div className="flex gap-4 mt-6">
          <Button variant="outline" onClick={() => setCurrentStep(1)}>
            Back
          </Button>
          <Button 
            onClick={() => setCurrentStep(3)} 
            disabled={!contractData.parties.party1_name || !contractData.parties.party2_name}
            className="flex-1"
          >
            Next: Terms & Conditions
          </Button>
        </div>
      </CardContent>
    </Card>
  ));

  const TermsStep = () => (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle className="text-2xl">Terms & Conditions</CardTitle>
        <CardDescription>Specify the key terms of your contract</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {contractData.contract_type === 'NDA' && (
          <>
            <div>
              <Label htmlFor="purpose">Purpose of Disclosure</Label>
              <Textarea
                id="purpose"
                placeholder="Describe why confidential information will be shared..."
                value={contractData.terms.purpose || ''}
                onChange={(e) => updateTerms('purpose', e.target.value)}
              />
            </div>
            <div>
              <Label htmlFor="duration">Agreement Duration</Label>
              <Select value={contractData.terms.duration || ''} onValueChange={(value) => 
                updateTerms('duration', value)
              }>
                <SelectTrigger>
                  <SelectValue placeholder="Select duration" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="1_year">1 Year</SelectItem>
                  <SelectItem value="2_years">2 Years</SelectItem>
                  <SelectItem value="3_years">3 Years</SelectItem>
                  <SelectItem value="5_years">5 Years</SelectItem>
                  <SelectItem value="indefinite">Indefinite</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </>
        )}

        {contractData.contract_type === 'freelance_agreement' && (
          <>
            <div>
              <Label htmlFor="scope">Scope of Work</Label>
              <Textarea
                id="scope"
                placeholder="Describe the services to be provided..."
                value={contractData.terms.scope || ''}
                onChange={(e) => updateTerms('scope', e.target.value)}
              />
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="payment_amount">Payment Amount</Label>
                <Input
                  id="payment_amount"
                  placeholder="$5,000"
                  value={contractData.terms.payment_amount || ''}
                  onChange={(e) => updateTerms('payment_amount', e.target.value)}
                />
              </div>
              <div>
                <Label htmlFor="payment_terms">Payment Terms</Label>
                <Select value={contractData.terms.payment_terms || ''} onValueChange={(value) => 
                  updateTerms('payment_terms', value)
                }>
                  <SelectTrigger>
                    <SelectValue placeholder="Select terms" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="upfront">100% Upfront</SelectItem>
                    <SelectItem value="milestone">Milestone-based</SelectItem>
                    <SelectItem value="net30">Net 30 Days</SelectItem>
                    <SelectItem value="net15">Net 15 Days</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </>
        )}

        {contractData.contract_type === 'partnership_agreement' && (
          <>
            <div>
              <Label htmlFor="business_purpose">Business Purpose</Label>
              <Textarea
                id="business_purpose"
                placeholder="Describe the purpose of the partnership..."
                value={contractData.terms.business_purpose || ''}
                onChange={(e) => updateTerms('business_purpose', e.target.value)}
              />
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="profit_split">Profit Split (%)</Label>
                <Input
                  id="profit_split"
                  placeholder="50/50"
                  value={contractData.terms.profit_split || ''}
                  onChange={(e) => updateTerms('profit_split', e.target.value)}
                />
              </div>
              <div>
                <Label htmlFor="capital_contribution">Capital Contribution</Label>
                <Input
                  id="capital_contribution"
                  placeholder="$10,000 each"
                  value={contractData.terms.capital_contribution || ''}
                  onChange={(e) => updateTerms('capital_contribution', e.target.value)}
                />
              </div>
            </div>
          </>
        )}

        <div>
          <Label htmlFor="special_clauses">Special Clauses (Optional)</Label>
          <Textarea
            id="special_clauses"
            placeholder="Any additional clauses or terms..."
            value={contractData.special_clauses.join('\n')}
            onChange={(e) => setContractData(prev => ({ 
              ...prev, 
              special_clauses: e.target.value.split('\n').filter(c => c.trim())
            }))}
          />
        </div>

        <div className="flex gap-4 mt-6">
          <Button variant="outline" onClick={() => setCurrentStep(2)}>
            Back
          </Button>
          <Button 
            onClick={generateContract} 
            disabled={isGenerating}
            className="flex-1 bg-blue-600 hover:bg-blue-700"
          >
            {isGenerating ? (
              <>
                <Zap className="mr-2 h-4 w-4 animate-spin" />
                Generating Contract...
              </>
            ) : (
              <>
                <FileText className="mr-2 h-4 w-4" />
                Generate Contract
              </>
            )}
          </Button>
        </div>
      </CardContent>
    </Card>
  );

  const ContractResult = () => (
    <div className="w-full max-w-4xl mx-auto space-y-6">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-2xl">Contract Generated Successfully</CardTitle>
              <CardDescription>
                Your {contractTypes.find(t => t.id === generatedContract.contract.contract_type)?.name} is ready
              </CardDescription>
            </div>
            <div className="flex items-center space-x-2">
              <Badge variant={generatedContract.contract.compliance_score > 80 ? 'default' : 'secondary'}>
                {generatedContract.contract.compliance_score.toFixed(0)}% Compliance
              </Badge>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <Progress value={generatedContract.contract.compliance_score} className="w-full" />
            
            {generatedContract.warnings?.length > 0 && (
              <Alert>
                <AlertTriangle className="h-4 w-4" />
                <AlertDescription>
                  <strong>Warnings:</strong> {generatedContract.warnings.join(', ')}
                </AlertDescription>
              </Alert>
            )}

            <Tabs defaultValue="preview" className="w-full">
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="preview">
                  <Eye className="mr-2 h-4 w-4" />
                  Preview
                </TabsTrigger>
                <TabsTrigger value="clauses">
                  <FileText className="mr-2 h-4 w-4" />
                  Clauses ({generatedContract.contract.clauses.length})
                </TabsTrigger>
              </TabsList>

              <TabsContent value="preview" className="mt-4">
                <Card>
                  <CardContent className="p-6">
                    <div className="max-h-96 overflow-y-auto bg-gray-50 p-4 rounded border">
                      <pre className="whitespace-pre-wrap text-sm font-mono">
                        {generatedContract.contract.content}
                      </pre>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="clauses" className="mt-4">
                <div className="space-y-3">
                  {generatedContract.contract.clauses.map((clause, index) => (
                    <Card key={index}>
                      <CardContent className="p-4">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <h4 className="font-semibold text-sm">{clause.title}</h4>
                            <p className="text-sm text-gray-600 mt-1">{clause.content}</p>
                          </div>
                          <Badge variant="outline" className="ml-2">
                            {clause.type}
                          </Badge>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </TabsContent>
            </Tabs>

            <div className="flex gap-4 mt-6">
              <Button 
                onClick={() => {
                  setCurrentStep(1);
                  setGeneratedContract(null);
                  setContractData({
                    contract_type: '',
                    jurisdiction: 'US',
                    parties: {},
                    terms: {},
                    special_clauses: []
                  });
                }}
                variant="outline"
                className="flex-1"
              >
                Create New Contract
              </Button>
              <Button className="flex-1 bg-green-600 hover:bg-green-700">
                <Download className="mr-2 h-4 w-4" />
                Download PDF
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );

  const Hero = () => (
    <div className="relative bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 text-white py-16 px-6">
      <div className="absolute inset-0 bg-black/20"></div>
      <div className="relative max-w-6xl mx-auto text-center">
        <div className="mb-8">
          <img 
            src="https://images.unsplash.com/photo-1599840448769-f4ac7aac8d8b?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzR8MHwxfHNlYXJjaHwyfHxsZWdhbCUyMHRlY2hub2xvZ3l8ZW58MHx8fGJsdWV8MTc1MzgzNzA1NHww&ixlib=rb-4.1.0&q=85"
            alt="LegalMate AI"
            className="w-32 h-20 mx-auto rounded-lg shadow-2xl object-cover"
          />
        </div>
        <h1 className="text-5xl font-bold mb-4">
          LegalMate AI
        </h1>
        <p className="text-xl text-blue-100 mb-8 max-w-3xl mx-auto">
          Generate professional, jurisdiction-specific legal contracts in minutes using advanced AI. 
          Perfect for freelancers, agencies, and small businesses.
        </p>
        <div className="flex flex-wrap justify-center gap-4 text-sm">
          <div className="flex items-center space-x-2">
            <Shield className="h-5 w-5 text-green-400" />
            <span>Legally Compliant</span>
          </div>
          <div className="flex items-center space-x-2">
            <Zap className="h-5 w-5 text-yellow-400" />
            <span>AI-Powered</span>
          </div>
          <div className="flex items-center space-x-2">
            <Users className="h-5 w-5 text-blue-400" />
            <span>Multi-Jurisdiction</span>
          </div>
        </div>
      </div>
    </div>
  );

  const ContractLibrary = () => (
    <Card className="w-full max-w-4xl mx-auto">
      <CardHeader>
        <CardTitle className="text-2xl">Your Contract Library</CardTitle>
        <CardDescription>Previously generated contracts</CardDescription>
      </CardHeader>
      <CardContent>
        {contracts.length === 0 ? (
          <div className="text-center py-12">
            <FileText className="h-16 w-16 mx-auto text-gray-400 mb-4" />
            <p className="text-gray-500">No contracts generated yet. Create your first contract above!</p>
          </div>
        ) : (
          <div className="space-y-4">
            {contracts.slice(0, 5).map((contract) => (
              <Card key={contract.id} className="cursor-pointer hover:shadow-md transition-shadow">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-semibold">
                        {contractTypes.find(t => t.id === contract.contract_type)?.name || contract.contract_type}
                      </h3>
                      <p className="text-sm text-gray-600">
                        {new Date(contract.created_at).toLocaleDateString()}
                      </p>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Badge variant="outline">{contract.jurisdiction}</Badge>
                      <Badge variant={contract.compliance_score > 80 ? 'default' : 'secondary'}>
                        {contract.compliance_score.toFixed(0)}%
                      </Badge>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );

  return (
    <div className="min-h-screen bg-gray-50">
      <Hero />
      
      <div className="py-12 px-6">
        <div className="max-w-6xl mx-auto">
          {currentStep < 4 && (
            <div className="mb-8">
              <div className="flex items-center justify-center space-x-8 mb-6">
                {[1, 2, 3].map((step) => (
                  <div key={step} className="flex items-center">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold ${
                      currentStep >= step ? 'bg-blue-600 text-white' : 'bg-gray-300 text-gray-600'
                    }`}>
                      {currentStep > step ? <CheckCircle className="h-5 w-5" /> : step}
                    </div>
                    <span className="ml-2 text-sm font-medium">
                      {step === 1 && 'Contract Type'}
                      {step === 2 && 'Parties'}
                      {step === 3 && 'Terms'}
                    </span>
                    {step < 3 && <div className="w-16 h-px bg-gray-300 ml-4"></div>}
                  </div>
                ))}
              </div>
            </div>
          )}

          {currentStep === 1 && <ContractTypeStep />}
          {currentStep === 2 && <PartiesStep />}
          {currentStep === 3 && <TermsStep />}
          {currentStep === 4 && <ContractResult />}

          {currentStep === 1 && <div className="mt-12"><ContractLibrary /></div>}
        </div>
      </div>
    </div>
  );
}

export default App;