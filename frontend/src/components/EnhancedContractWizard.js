import React, { useState, useEffect, useCallback, useRef, useMemo } from 'react';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Switch } from './ui/switch';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { Alert, AlertDescription } from './ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog';
import { 
  User, 
  Building, 
  Lightbulb, 
  CheckCircle, 
  ArrowRight, 
  ArrowLeft,
  Sparkles,
  Target,
  Clock,
  Plus,
  X
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
const API = `${BACKEND_URL}/api`;

const EnhancedContractWizard = ({ 
  contractTypes, 
  jurisdictions, 
  onContractGenerated,
  onBack 
}) => {
  // State management
  const [currentStep, setCurrentStep] = useState(1);
  const [wizardData, setWizardData] = useState({});
  const [userProfile, setUserProfile] = useState(null);
  const [companyProfile, setCompanyProfile] = useState(null);
  const [suggestions, setSuggestions] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [estimatedTime, setEstimatedTime] = useState('10 minutes');
  const [showProfileDialog, setShowProfileDialog] = useState(false);
  const [profileType, setProfileType] = useState('user'); // 'user' or 'company'
  
  // Simplified flag to track user interaction - no complex timeout logic
  const [userHasInteracted, setUserHasInteracted] = useState(false);
  
  // Add refs to prevent race conditions
  const lastInputValuesRef = useRef({});
  const inputTimeoutRef = useRef(null);

  // Form data for each step
  const [stepData, setStepData] = useState({
    step1: { contract_type: '', industry: '', jurisdiction: 'US' },
    step2: { 
      party1_name: '', party1_email: '', party1_address: '',
      party2_name: '', party2_email: '', party2_address: ''
    },
    step3: { 
      payment_terms: '', project_duration: '', deliverables: '', liability_cap: ''
    },
    step4: { 
      confidentiality: false, non_compete: false, special_terms: '', execution_date: ''
    },
    step5: { review_complete: false, legal_review: false }
  });

  useEffect(() => {
    // Only initialize wizard when moving to a new step and user hasn't interacted much
    if (currentStep > 1 && 
        !stepData[`step${currentStep}`]?.initialized && 
        !userHasInteracted) {
      // Add a small delay to avoid interfering with user interactions
      const initTimer = setTimeout(() => {
        if (!userHasInteracted) {
          initializeWizard();
        }
      }, 800); // Longer delay to ensure user can start typing
      
      return () => clearTimeout(initTimer);
    }
  }, [currentStep, userHasInteracted]);

  // Cleanup timeout on unmount or when component updates
  useEffect(() => {
    return () => {
      if (inputTimeoutRef.current) {
        clearTimeout(inputTimeoutRef.current);
      }
    };
  }, []);



  const initializeWizard = async () => {
    if (currentStep === 1) return;
    
    setIsLoading(true);
    try {
      const response = await axios.post(`${API}/contract-wizard/initialize`, {
        user_id: userProfile?.id,
        company_id: companyProfile?.id,
        contract_type: stepData.step1.contract_type,
        current_step: currentStep,
        partial_data: stepData
      });

      setSuggestions(response.data.suggestions || []);
      setProgress(response.data.progress * 100);
      setEstimatedTime(response.data.estimated_completion_time);
      
      // Apply suggestions to form data only if fields are empty and after a small delay
      setTimeout(() => {
        if (!userHasInteracted) {
          applySuggestions(response.data.suggestions);
        }
      }, 1000); // Wait 1 second before applying suggestions
      
      // Mark this step as initialized
      const currentStepKey = `step${currentStep}`;
      setStepData(prev => ({
        ...prev,
        [currentStepKey]: {
          ...prev[currentStepKey],
          initialized: true
        }
      }));
    } catch (error) {
      console.error('Error initializing wizard:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const applySuggestions = (newSuggestions) => {
    // Don't apply suggestions if user has interacted, if there are no suggestions
    if (userHasInteracted || !newSuggestions || newSuggestions.length === 0) {
      return;
    }
    
    const currentStepKey = `step${currentStep}`;
    const currentStepData = stepData[currentStepKey];
    
    // Only apply suggestions to completely empty fields with very high confidence (95%+)
    const updatedStepData = { ...currentStepData };
    let hasChanges = false;
    
    newSuggestions.forEach(suggestion => {
      const fieldValue = currentStepData[suggestion.field_name];
      const fieldKey = `${currentStepKey}.${suggestion.field_name}`;
      
      // Double-check that the field is still empty and hasn't been modified by user
      const lastInputValue = lastInputValuesRef.current[fieldKey];
      
      // Only apply if field is empty AND hasn't been touched by user recently
      if (suggestion.confidence > 0.95 && 
          (!fieldValue || fieldValue.trim() === '') && 
          (!lastInputValue || lastInputValue.trim() === '')) {
        updatedStepData[suggestion.field_name] = suggestion.suggested_value;
        hasChanges = true;
      }
    });
    
    // Only update state if there are actual changes
    if (hasChanges) {
      setStepData(prev => ({
        ...prev,
        [currentStepKey]: updatedStepData
      }));
    }
  };

  const getFieldSuggestions = async (fieldName) => {
    try {
      const response = await axios.post(`${API}/contract-wizard/suggestions`, {
        contract_type: stepData.step1.contract_type,
        field_name: fieldName,
        user_id: userProfile?.id,
        company_id: companyProfile?.id,
        context: stepData
      });
      
      return response.data.suggestions || [];
    } catch (error) {
      console.error('Error getting field suggestions:', error);
      return [];
    }
  };

  // CLASSIC MODE APPROACH: Simple, direct state update function
  const updateStepData = useCallback((step, field, value) => {
    setStepData(prev => ({
      ...prev,
      [step]: {
        ...prev[step],
        [field]: value
      }
    }));
  }, []);

  const applySuggestion = (suggestion) => {
    const currentStepKey = `step${currentStep}`;
    updateStepData(currentStepKey, suggestion.field_name, suggestion.suggested_value);
  };

  const nextStep = () => {
    if (currentStep < 5) {
      setCurrentStep(currentStep + 1);
      // Reset interaction flag for the new step so suggestions can work
      setUserHasInteracted(false);
    } else {
      generateContract();
    }
  };

  const prevStep = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
      // Reset interaction flag when going back to allow suggestions
      setUserHasInteracted(false);
    }
  };

  const generateContract = async () => {
    setIsLoading(true);
    try {
      // Combine all step data into a contract request
      const contractData = {
        contract_type: stepData.step1.contract_type,
        jurisdiction: stepData.step1.jurisdiction,
        parties: {
          party1_name: stepData.step2.party1_name,
          party1_email: stepData.step2.party1_email,
          party1_address: stepData.step2.party1_address,
          party2_name: stepData.step2.party2_name,
          party2_email: stepData.step2.party2_email,
          party2_address: stepData.step2.party2_address,
        },
        terms: {
          payment_terms: stepData.step3.payment_terms,
          project_duration: stepData.step3.project_duration,
          deliverables: stepData.step3.deliverables,
          liability_cap: stepData.step3.liability_cap,
          ...stepData.step3
        },
        special_clauses: stepData.step4.special_terms ? [stepData.step4.special_terms] : [],
        execution_date: stepData.step4.execution_date
      };

      const response = await axios.post(`${API}/generate-contract`, contractData);
      onContractGenerated(response.data);
    } catch (error) {
      console.error('Error generating contract:', error);
      alert('Failed to generate contract. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  // Profile management functions
  const createUserProfile = async (profileData) => {
    try {
      const response = await axios.post(`${API}/users/profile`, {
        id: `user_${Date.now()}`,
        ...profileData,
      });
      setUserProfile(response.data);
      setShowProfileDialog(false);
    } catch (error) {
      console.error('Error creating user profile:', error);
    }
  };

  const createCompanyProfile = async (profileData) => {
    try {
      const response = await axios.post(`${API}/companies/profile`, {
        id: `company_${Date.now()}`,
        user_id: userProfile?.id || `user_${Date.now()}`,
        ...profileData,
      });
      setCompanyProfile(response.data);
      setShowProfileDialog(false);
    } catch (error) {
      console.error('Error creating company profile:', error);
    }
  };

  // Step Components
  const StepHeader = () => (
    <div className="mb-8">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Contract Wizard</h2>
          <p className="text-gray-600">Step {currentStep} of 5</p>
        </div>
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2 text-sm text-gray-600">
            <Clock className="h-4 w-4" />
            <span>{estimatedTime} remaining</span>
          </div>
          {(userProfile || companyProfile) && (
            <Badge variant="secondary" className="bg-green-100 text-green-800">
              <Sparkles className="h-3 w-3 mr-1" />
              Smart Suggestions Active
            </Badge>
          )}
        </div>
      </div>
      <Progress value={progress} className="h-2" />
    </div>
  );

  const SuggestionsPanel = () => {
    if (suggestions.length === 0) return null;
    
    return (
      <Card className="mb-6 border-blue-200 bg-blue-50">
        <CardHeader className="pb-3">
          <CardTitle className="text-sm font-medium flex items-center">
            <Lightbulb className="h-4 w-4 mr-2 text-blue-600" />
            Smart Suggestions
          </CardTitle>
        </CardHeader>
        <CardContent className="pt-0">
          <div className="space-y-2">
            {suggestions.map((suggestion, index) => (
              <div key={index} className="flex items-center justify-between p-2 bg-white rounded border">
                <div className="flex-1">
                  <p className="text-sm font-medium">{suggestion.field_name.replace('_', ' ').toUpperCase()}</p>
                  <p className="text-sm text-gray-600">{suggestion.suggested_value}</p>
                  <p className="text-xs text-gray-500">{suggestion.reasoning}</p>
                </div>
                <Button
                  size="sm"
                  onClick={() => applySuggestion(suggestion)}
                  className="ml-2 bg-blue-600 hover:bg-blue-700"
                >
                  Apply
                </Button>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    );
  };

  const ProfileSetup = () => (
    <Card className="mb-6 border-orange-200 bg-orange-50">
      <CardContent className="p-4">
        <div className="flex items-center justify-between">
          <div>
            <h4 className="font-medium text-orange-900">Setup Your Profile for Smart Suggestions</h4>
            <p className="text-sm text-orange-700">Save time by auto-filling common fields</p>
          </div>
          <div className="flex space-x-2">
            <Button
              size="sm"
              variant="outline"
              onClick={() => {
                setProfileType('user');
                setShowProfileDialog(true);
              }}
              className="border-orange-300"
            >
              <User className="h-4 w-4 mr-1" />
              User Profile
            </Button>
            <Button
              size="sm"
              variant="outline"
              onClick={() => {
                setProfileType('company');
                setShowProfileDialog(true);
              }}
              className="border-orange-300"
            >
              <Building className="h-4 w-4 mr-1" />
              Company Profile
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );

  // Individual Step Components
  const Step1ContractType = () => (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center">
          <Target className="h-5 w-5 mr-2" />
          Contract Type & Industry
        </CardTitle>
        <CardDescription>
          Select your contract type and specify any industry requirements
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div>
          <Label htmlFor="contract_type">Contract Type *</Label>
          <Select 
            value={stepData.step1.contract_type} 
            onValueChange={(value) => updateStepData('step1', 'contract_type', value)}
          >
            <SelectTrigger>
              <SelectValue placeholder="Select contract type" />
            </SelectTrigger>
            <SelectContent>
              {contractTypes.map((type) => (
                <SelectItem key={type.id} value={type.id}>
                  <div className="flex items-center justify-between w-full">
                    <span>{type.name}</span>
                    <Badge variant="outline" className="ml-2 text-xs">
                      {type.complexity}
                    </Badge>
                  </div>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div>
          <Label htmlFor="industry">Industry (Optional)</Label>
          <Select 
            value={stepData.step1.industry} 
            onValueChange={(value) => updateStepData('step1', 'industry', value)}
          >
            <SelectTrigger>
              <SelectValue placeholder="Select your industry" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="technology">Technology</SelectItem>
              <SelectItem value="healthcare">Healthcare</SelectItem>
              <SelectItem value="finance">Finance</SelectItem>
              <SelectItem value="marketing">Marketing</SelectItem>
              <SelectItem value="consulting">Consulting</SelectItem>
              <SelectItem value="real_estate">Real Estate</SelectItem>
              <SelectItem value="manufacturing">Manufacturing</SelectItem>
              <SelectItem value="other">Other</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div>
          <Label htmlFor="jurisdiction">Jurisdiction *</Label>
          <Select 
            value={stepData.step1.jurisdiction} 
            onValueChange={(value) => updateStepData('step1', 'jurisdiction', value)}
          >
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
      </CardContent>
    </Card>
  );

  const Step2PartyInfo = () => (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center">
          <User className="h-5 w-5 mr-2" />
          Party Information
        </CardTitle>
        <CardDescription>
          Enter details for all parties involved in the contract
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* First Party */}
          <div className="space-y-4">
            <h4 className="font-medium text-lg border-b pb-2">Your Information</h4>
            <div>
              <Label htmlFor="party1_name">Name/Company Name *</Label>
              <Input
                key="party1_name_stable_input"
                id="party1_name"
                value={stepData.step2.party1_name}
                onChange={(e) => updateStepData('step2', 'party1_name', e.target.value)}
                placeholder="Your name or company name"
              />
            </div>
            <div>
              <Label htmlFor="party1_email">Email</Label>
              <Input
                key="party1_email_stable_input"
                id="party1_email"
                type="email"
                value={stepData.step2.party1_email}
                onChange={(e) => updateStepData('step2', 'party1_email', e.target.value)}
                placeholder="your@email.com"
              />
            </div>
            <div>
              <Label htmlFor="party1_address">Address</Label>
              <Textarea
                key="party1_address_stable_textarea"
                id="party1_address"
                value={stepData.step2.party1_address}
                onChange={(e) => updateStepData('step2', 'party1_address', e.target.value)}
                placeholder="Full address"
                rows={3}
              />
            </div>
          </div>

          {/* Second Party */}
          <div className="space-y-4">
            <h4 className="font-medium text-lg border-b pb-2">Other Party Information</h4>
            <div>
              <Label htmlFor="party2_name">Name/Company Name *</Label>
              <Input
                key="party2_name_stable_input"
                id="party2_name"
                value={stepData.step2.party2_name}
                onChange={(e) => updateStepData('step2', 'party2_name', e.target.value)}
                placeholder="Other party name"
              />
            </div>
            <div>
              <Label htmlFor="party2_email">Email</Label>
              <Input
                key="party2_email_stable_input"
                id="party2_email"
                type="email"
                value={stepData.step2.party2_email}
                onChange={(e) => updateStepData('step2', 'party2_email', e.target.value)}
                placeholder="other@email.com"
              />
            </div>
            <div>
              <Label htmlFor="party2_address">Address</Label>
              <Textarea
                key="party2_address_stable_textarea"
                id="party2_address"
                value={stepData.step2.party2_address}
                onChange={(e) => updateStepData('step2', 'party2_address', e.target.value)}
                placeholder="Full address"
                rows={3}
              />
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );

  const Step3Terms = () => (
    <Card>
      <CardHeader>
        <CardTitle>Terms & Conditions</CardTitle>
        <CardDescription>
          Define the key terms and conditions for your contract
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <Label htmlFor="payment_terms">Payment Terms *</Label>
            <Input
              key="payment_terms_stable_input"
              id="payment_terms"
              value={stepData.step3.payment_terms}
              onChange={(e) => updateStepData('step3', 'payment_terms', e.target.value)}
              placeholder="e.g., Net 30, 50% upfront"
            />
          </div>
          <div>
            <Label htmlFor="project_duration">Project Duration</Label>
            <Input
              key="project_duration_stable_input"
              id="project_duration"
              value={stepData.step3.project_duration}
              onChange={(e) => updateStepData('step3', 'project_duration', e.target.value)}
              placeholder="e.g., 3 months, 6 weeks"
            />
          </div>
        </div>

        <div>
          <Label htmlFor="deliverables">Deliverables</Label>
          <Textarea
            key="deliverables_stable_textarea"
            id="deliverables"
            value={stepData.step3.deliverables}
            onChange={(e) => updateStepData('step3', 'deliverables', e.target.value)}
            placeholder="Describe what will be delivered..."
            rows={4}
          />
        </div>

        <div>
          <Label htmlFor="liability_cap">Liability Cap</Label>
          <Input
            key="liability_cap_stable_input"
            id="liability_cap"
            value={stepData.step3.liability_cap}
            onChange={(e) => updateStepData('step3', 'liability_cap', e.target.value)}
            placeholder="e.g., Project value, $10,000"
          />
        </div>
      </CardContent>
    </Card>
  );

  const Step4SpecialClauses = () => (
    <Card>
      <CardHeader>
        <CardTitle>Special Clauses</CardTitle>
        <CardDescription>
          Add any special clauses or requirements
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <Label htmlFor="confidentiality">Include Confidentiality Clause</Label>
              <p className="text-sm text-gray-600">Protect sensitive information</p>
            </div>
            <Switch
              id="confidentiality"
              checked={stepData.step4.confidentiality}
              onCheckedChange={(checked) => updateStepData('step4', 'confidentiality', checked)}
            />
          </div>

          <div className="flex items-center justify-between">
            <div>
              <Label htmlFor="non_compete">Include Non-Compete Clause</Label>
              <p className="text-sm text-gray-600">Prevent competition during contract term</p>
            </div>
            <Switch
              id="non_compete"
              checked={stepData.step4.non_compete}
              onCheckedChange={(checked) => updateStepData('step4', 'non_compete', checked)}
            />
          </div>
        </div>

        <div>
          <Label htmlFor="special_terms">Additional Terms</Label>
          <Textarea
            key="special_terms_stable_textarea"
            id="special_terms"
            value={stepData.step4.special_terms}
            onChange={(e) => updateStepData('step4', 'special_terms', e.target.value)}
            placeholder="Any additional terms or special requirements..."
            rows={4}
          />
        </div>

        <div>
          <Label htmlFor="execution_date">Execution Date</Label>
          <Input
            key="execution_date_stable_input"
            id="execution_date"
            type="date"
            value={stepData.step4.execution_date}
            onChange={(e) => updateStepData('step4', 'execution_date', e.target.value)}
          />
        </div>
      </CardContent>
    </Card>
  );

  const Step5Review = () => (
    <Card>
      <CardHeader>
        <CardTitle>Review & Generate</CardTitle>
        <CardDescription>
          Review your contract details and generate the final document
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Contract Summary */}
        <div className="bg-gray-50 p-4 rounded-lg">
          <h4 className="font-medium mb-3">Contract Summary</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div>
              <strong>Type:</strong> {contractTypes.find(t => t.id === stepData.step1.contract_type)?.name}
            </div>
            <div>
              <strong>Jurisdiction:</strong> {stepData.step1.jurisdiction}
            </div>
            <div>
              <strong>Parties:</strong> {stepData.step2.party1_name} ↔ {stepData.step2.party2_name}
            </div>
            <div>
              <strong>Payment:</strong> {stepData.step3.payment_terms}
            </div>
          </div>
        </div>

        <div className="space-y-4">
          <div className="flex items-center space-x-2">
            <Switch
              id="review_complete"
              checked={stepData.step5.review_complete}
              onCheckedChange={(checked) => updateStepData('step5', 'review_complete', checked)}
            />
            <Label htmlFor="review_complete">I have reviewed all details and they are correct</Label>
          </div>

          <div className="flex items-center space-x-2">
            <Switch
              id="legal_review"
              checked={stepData.step5.legal_review}
              onCheckedChange={(checked) => updateStepData('step5', 'legal_review', checked)}
            />
            <Label htmlFor="legal_review">This contract will be reviewed by legal counsel</Label>
          </div>
        </div>

        {!stepData.step5.review_complete && (
          <Alert className="border-amber-200 bg-amber-50">
            <AlertDescription>
              Please review all contract details before generating the final document.
            </AlertDescription>
          </Alert>
        )}
      </CardContent>
    </Card>
  );

  const ProfileDialog = () => (
    <Dialog open={showProfileDialog} onOpenChange={setShowProfileDialog}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>
            Create {profileType === 'user' ? 'User' : 'Company'} Profile
          </DialogTitle>
        </DialogHeader>
        <div className="p-4">
          {profileType === 'user' ? (
            <UserProfileForm onSubmit={createUserProfile} />
          ) : (
            <CompanyProfileForm onSubmit={createCompanyProfile} />
          )}
        </div>
      </DialogContent>
    </Dialog>
  );

  const UserProfileForm = ({ onSubmit }) => {
    const [formData, setFormData] = useState({
      name: '', email: '', phone: '', role: '', industry: ''
    });

    const handleSubmit = (e) => {
      e.preventDefault();
      onSubmit(formData);
    };

    return (
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <Label htmlFor="name">Full Name *</Label>
          <Input
            id="name"
            value={formData.name}
            onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
            required
          />
        </div>
        <div>
          <Label htmlFor="email">Email *</Label>
          <Input
            id="email"
            type="email"
            value={formData.email}
            onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
            required
          />
        </div>
        <div>
          <Label htmlFor="role">Role</Label>
          <Select value={formData.role} onValueChange={(value) => setFormData(prev => ({ ...prev, role: value }))}>
            <SelectTrigger>
              <SelectValue placeholder="Select your role" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="business_owner">Business Owner</SelectItem>
              <SelectItem value="freelancer">Freelancer</SelectItem>
              <SelectItem value="legal_professional">Legal Professional</SelectItem>
              <SelectItem value="other">Other</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <Button type="submit" className="w-full">Create Profile</Button>
      </form>
    );
  };

  const CompanyProfileForm = ({ onSubmit }) => {
    const [formData, setFormData] = useState({
      name: '', industry: '', size: '', legal_structure: '', email: ''
    });

    const handleSubmit = (e) => {
      e.preventDefault();
      onSubmit(formData);
    };

    return (
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <Label htmlFor="name">Company Name *</Label>
          <Input
            id="name"
            value={formData.name}
            onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
            required
          />
        </div>
        <div>
          <Label htmlFor="industry">Industry</Label>
          <Select value={formData.industry} onValueChange={(value) => setFormData(prev => ({ ...prev, industry: value }))}>
            <SelectTrigger>
              <SelectValue placeholder="Select industry" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="technology">Technology</SelectItem>
              <SelectItem value="healthcare">Healthcare</SelectItem>
              <SelectItem value="finance">Finance</SelectItem>
              <SelectItem value="other">Other</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div>
          <Label htmlFor="size">Company Size</Label>
          <Select value={formData.size} onValueChange={(value) => setFormData(prev => ({ ...prev, size: value }))}>
            <SelectTrigger>
              <SelectValue placeholder="Select size" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="startup">Startup (1-10)</SelectItem>
              <SelectItem value="small">Small (11-50)</SelectItem>
              <SelectItem value="medium">Medium (51-200)</SelectItem>
              <SelectItem value="large">Large (200+)</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <Button type="submit" className="w-full">Create Profile</Button>
      </form>
    );
  };

  // Validation helper functions
  const isStep1Valid = () => {
    return stepData.step1.contract_type && stepData.step1.jurisdiction;
  };

  const isStep2Valid = () => {
    return stepData.step2.party1_name && stepData.step2.party2_name;
  };

  const isStep3Valid = () => {
    return stepData.step3.payment_terms; // At least payment terms are required
  };

  const isStep4Valid = () => {
    return true; // Step 4 is optional
  };

  const isStep5Valid = () => {
    return stepData.step5.review_complete;
  };

  const isCurrentStepValid = () => {
    switch (currentStep) {
      case 1: return isStep1Valid();
      case 2: return isStep2Valid();
      case 3: return isStep3Valid();
      case 4: return isStep4Valid();
      case 5: return isStep5Valid();
      default: return false;
    }
  };

  // Navigation
  const Navigation = () => (
    <div className="flex justify-between mt-8">
      <Button
        variant="outline"
        onClick={currentStep === 1 ? onBack : prevStep}
        disabled={isLoading}
      >
        <ArrowLeft className="h-4 w-4 mr-2" />
        {currentStep === 1 ? 'Back to Home' : 'Previous'}
      </Button>
      
      <Button
        onClick={nextStep}
        disabled={isLoading || !isCurrentStepValid()}
        className="bg-blue-600 hover:bg-blue-700"
      >
        {isLoading ? (
          'Processing...'
        ) : currentStep === 5 ? (
          <>
            <Sparkles className="h-4 w-4 mr-2" />
            Generate Contract
          </>
        ) : (
          <>
            Next
            <ArrowRight className="h-4 w-4 ml-2" />
          </>
        )}
      </Button>
    </div>
  );

  // Main render
  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <StepHeader />
      
      {!userProfile && !companyProfile && currentStep === 1 && <ProfileSetup />}
      
      <SuggestionsPanel />
      
      {currentStep === 1 && <Step1ContractType />}
      {currentStep === 2 && <Step2PartyInfo />}
      {currentStep === 3 && <Step3Terms />}
      {currentStep === 4 && <Step4SpecialClauses />}
      {currentStep === 5 && <Step5Review />}
      
      <Navigation />
      
      <ProfileDialog />
    </div>
  );
};

export default EnhancedContractWizard;