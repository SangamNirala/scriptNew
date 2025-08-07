import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Alert, AlertDescription } from './ui/alert';
import SettlementCalculator from './SettlementCalculator';
import LitigationStrategy from './LitigationStrategy';
import {
  BarChart3, Brain, Scale, Target, TrendingUp, TrendingDown,
  Clock, DollarSign, Shield, AlertTriangle, CheckCircle,
  Users, FileText, Gavel, PieChart, ArrowLeft, RefreshCw,
  BookOpen, Calculator, Lightbulb, Search
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Enhanced Case outcome prediction component with advanced analytics
const CaseOutcomePredictor = ({ onPredictionComplete }) => {
  const [caseData, setCaseData] = useState({
    case_type: '',
    jurisdiction: '',
    court_level: 'district',
    judge_name: '',
    case_facts: '',
    legal_issues: [],
    case_complexity: 0.5,
    case_value: '',
    evidence_strength: 5,
    witness_count: '',
    settlement_offers: []
  });
  const [prediction, setPrediction] = useState(null);
  const [similarCases, setSimilarCases] = useState(null);
  const [loading, setLoading] = useState(false);
  const [loadingSimilar, setLoadingSimilar] = useState(false);
  const [error, setError] = useState(null);
  const [showAdvancedMetrics, setShowAdvancedMetrics] = useState(false);

  const caseTypes = [
    { value: 'civil', label: 'Civil' },
    { value: 'criminal', label: 'Criminal' },
    { value: 'commercial', label: 'Commercial' },
    { value: 'employment', label: 'Employment' },
    { value: 'intellectual_property', label: 'Intellectual Property' },
    { value: 'family', label: 'Family Law' },
    { value: 'personal_injury', label: 'Personal Injury' },
    { value: 'bankruptcy', label: 'Bankruptcy' },
    { value: 'tax', label: 'Tax Law' },
    { value: 'environmental', label: 'Environmental' }
  ];

  const jurisdictions = [
    { value: 'federal', label: 'Federal' },
    { value: 'california', label: 'California' },
    { value: 'new_york', label: 'New York' },
    { value: 'texas', label: 'Texas' },
    { value: 'florida', label: 'Florida' },
    { value: 'illinois', label: 'Illinois' }
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const requestData = {
        ...caseData,
        case_value: caseData.case_value ? parseFloat(caseData.case_value) : null,
        witness_count: caseData.witness_count ? parseInt(caseData.witness_count) : null,
        case_complexity: parseFloat(caseData.case_complexity),
        evidence_strength: parseFloat(caseData.evidence_strength)
      };

      // Get case outcome prediction
      const response = await axios.post(`${API}/litigation/analyze-case`, requestData);
      setPrediction(response.data);
      
      if (onPredictionComplete) {
        onPredictionComplete(response.data);
      }

      // Fetch similar cases in parallel
      if (requestData.case_type && requestData.jurisdiction) {
        setLoadingSimilar(true);
        try {
          const similarResponse = await axios.get(`${API}/litigation/similar-cases`, {
            params: {
              case_type: requestData.case_type,
              jurisdiction: requestData.jurisdiction,
              case_value: requestData.case_value,
              limit: 5
            }
          });
          setSimilarCases(similarResponse.data);
        } catch (similarError) {
          console.error('Similar cases error:', similarError);
        } finally {
          setLoadingSimilar(false);
        }
      }
    } catch (err) {
      console.error('Case analysis error:', err);
      setError(err.response?.data?.detail || 'Failed to analyze case');
    } finally {
      setLoading(false);
    }
  };

  const formatOutcome = (outcome) => {
    return outcome.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  const getOutcomeColor = (outcome) => {
    const colors = {
      'plaintiff_win': 'bg-green-100 text-green-800',
      'defendant_win': 'bg-red-100 text-red-800', 
      'settlement': 'bg-blue-100 text-blue-800',
      'dismissed': 'bg-gray-100 text-gray-800'
    };
    return colors[outcome] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="space-y-6">
      {/* Case Input Form */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Scale className="h-5 w-5" />
            <span>Case Outcome Prediction</span>
          </CardTitle>
          <CardDescription>
            Enter case details to get AI-powered predictions for litigation outcomes
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="case_type">Case Type *</Label>
                <Select 
                  value={caseData.case_type} 
                  onValueChange={(value) => setCaseData(prev => ({...prev, case_type: value}))}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select case type" />
                  </SelectTrigger>
                  <SelectContent>
                    {caseTypes.map(type => (
                      <SelectItem key={type.value} value={type.value}>
                        {type.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label htmlFor="jurisdiction">Jurisdiction *</Label>
                <Select 
                  value={caseData.jurisdiction} 
                  onValueChange={(value) => setCaseData(prev => ({...prev, jurisdiction: value}))}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select jurisdiction" />
                  </SelectTrigger>
                  <SelectContent>
                    {jurisdictions.map(jurisdiction => (
                      <SelectItem key={jurisdiction.value} value={jurisdiction.value}>
                        {jurisdiction.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label htmlFor="judge_name">Judge Name</Label>
                <Input
                  id="judge_name"
                  placeholder="e.g., Judge Sarah Martinez"
                  value={caseData.judge_name}
                  onChange={(e) => setCaseData(prev => ({...prev, judge_name: e.target.value}))}
                />
              </div>

              <div>
                <Label htmlFor="case_value">Case Value ($)</Label>
                <Input
                  id="case_value"
                  type="number"
                  placeholder="e.g., 250000"
                  value={caseData.case_value}
                  onChange={(e) => setCaseData(prev => ({...prev, case_value: e.target.value}))}
                />
              </div>

              <div>
                <Label htmlFor="evidence_strength">Evidence Strength (1-10)</Label>
                <div className="space-y-2">
                  <input
                    type="range"
                    id="evidence_strength"
                    min="1"
                    max="10"
                    step="0.1"
                    value={caseData.evidence_strength}
                    onChange={(e) => setCaseData(prev => ({...prev, evidence_strength: e.target.value}))}
                    className="w-full"
                  />
                  <div className="text-sm text-gray-600 text-center">
                    {caseData.evidence_strength}/10
                  </div>
                </div>
              </div>

              <div>
                <Label htmlFor="witness_count">Number of Witnesses</Label>
                <Input
                  id="witness_count"
                  type="number"
                  placeholder="e.g., 5"
                  value={caseData.witness_count}
                  onChange={(e) => setCaseData(prev => ({...prev, witness_count: e.target.value}))}
                />
              </div>
            </div>

            <div>
              <Label htmlFor="case_facts">Case Facts & Background</Label>
              <Textarea
                id="case_facts"
                placeholder="Provide a detailed description of the case facts, background, and key issues..."
                value={caseData.case_facts}
                onChange={(e) => setCaseData(prev => ({...prev, case_facts: e.target.value}))}
                className="min-h-24"
              />
            </div>

            <div>
              <Label htmlFor="case_complexity">Case Complexity</Label>
              <div className="space-y-2">
                <input
                  type="range"
                  id="case_complexity"
                  min="0"
                  max="1"
                  step="0.1"
                  value={caseData.case_complexity}
                  onChange={(e) => setCaseData(prev => ({...prev, case_complexity: e.target.value}))}
                  className="w-full"
                />
                <div className="flex justify-between text-sm text-gray-600">
                  <span>Simple</span>
                  <span>{(caseData.case_complexity * 100).toFixed(0)}%</span>
                  <span>Highly Complex</span>
                </div>
              </div>
            </div>

            {error && (
              <Alert>
                <AlertTriangle className="h-4 w-4" />
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            <Button 
              type="submit" 
              disabled={loading || !caseData.case_type || !caseData.jurisdiction}
              className="w-full"
            >
              {loading ? (
                <>
                  <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                  Analyzing Case...
                </>
              ) : (
                <>
                  <Brain className="h-4 w-4 mr-2" />
                  Analyze Case Outcome
                </>
              )}
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Prediction Results */}
      {prediction && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Target className="h-5 w-5" />
              <span>Prediction Results</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Primary Prediction */}
            <div className="text-center">
              <div className={`inline-block px-4 py-2 rounded-full text-lg font-semibold ${getOutcomeColor(prediction.predicted_outcome)}`}>
                Most Likely Outcome: {formatOutcome(prediction.predicted_outcome)}
              </div>
              <div className="mt-2 text-2xl font-bold text-gray-900">
                {(prediction.confidence_score * 100).toFixed(1)}% Confidence
              </div>
              <Progress value={prediction.confidence_score * 100} className="mt-2 h-3" />
            </div>

            {/* Outcome Probabilities */}
            <div>
              <h3 className="text-lg font-semibold mb-3">Outcome Probabilities</h3>
              <div className="space-y-2">
                {Object.entries(prediction.probability_breakdown).map(([outcome, probability]) => (
                  <div key={outcome} className="flex items-center justify-between">
                    <span className="font-medium">{formatOutcome(outcome)}</span>
                    <div className="flex items-center space-x-2">
                      <Progress value={probability * 100} className="w-32 h-2" />
                      <span className="text-sm font-medium w-12">
                        {(probability * 100).toFixed(1)}%
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Key Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center p-4 bg-blue-50 rounded-lg">
                <Clock className="h-6 w-6 text-blue-600 mx-auto mb-2" />
                <div className="text-2xl font-bold text-blue-900">
                  {prediction.estimated_duration || 365} days
                </div>
                <div className="text-sm text-blue-600">Estimated Duration</div>
              </div>

              <div className="text-center p-4 bg-green-50 rounded-lg">
                <DollarSign className="h-6 w-6 text-green-600 mx-auto mb-2" />
                <div className="text-2xl font-bold text-green-900">
                  ${prediction.estimated_cost?.toLocaleString() || 'N/A'}
                </div>
                <div className="text-sm text-green-600">Estimated Cost</div>
              </div>

              <div className="text-center p-4 bg-purple-50 rounded-lg">
                <Target className="h-6 w-6 text-purple-600 mx-auto mb-2" />
                <div className="text-2xl font-bold text-purple-900">
                  {(prediction.settlement_probability * 100).toFixed(1)}%
                </div>
                <div className="text-sm text-purple-600">Settlement Probability</div>
              </div>
            </div>

            {/* Settlement Range */}
            {prediction.settlement_range && (
              <div>
                <h3 className="text-lg font-semibold mb-2">Expected Settlement Range</h3>
                <div className="p-4 bg-gray-50 rounded-lg">
                  <div className="text-xl font-bold">
                    ${prediction.settlement_range[0]?.toLocaleString()} - ${prediction.settlement_range[1]?.toLocaleString()}
                  </div>
                  <div className="text-sm text-gray-600 mt-1">
                    Based on case value and similar historical cases
                  </div>
                </div>
              </div>
            )}

            {/* Risk & Success Factors */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <h3 className="text-lg font-semibold mb-2 text-red-700 flex items-center">
                  <AlertTriangle className="h-4 w-4 mr-2" />
                  Risk Factors
                </h3>
                {prediction.risk_factors && prediction.risk_factors.length > 0 ? (
                  <ul className="space-y-1">
                    {prediction.risk_factors.map((factor, index) => (
                      <li key={index} className="text-sm text-red-600 flex items-start">
                        <span className="text-red-400 mr-2">•</span>
                        {factor}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-sm text-gray-500">AI analysis in progress...</p>
                )}
              </div>

              <div>
                <h3 className="text-lg font-semibold mb-2 text-green-700 flex items-center">
                  <CheckCircle className="h-4 w-4 mr-2" />
                  Success Factors
                </h3>
                {prediction.success_factors && prediction.success_factors.length > 0 ? (
                  <ul className="space-y-1">
                    {prediction.success_factors.map((factor, index) => (
                      <li key={index} className="text-sm text-green-600 flex items-start">
                        <span className="text-green-400 mr-2">•</span>
                        {factor}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-sm text-gray-500">AI analysis in progress...</p>
                )}
              </div>
            </div>

            {/* Recommendations */}
            {prediction.recommendations && prediction.recommendations.length > 0 && (
              <div>
                <h3 className="text-lg font-semibold mb-2 flex items-center">
                  <Lightbulb className="h-4 w-4 mr-2" />
                  Strategic Recommendations
                </h3>
                <ul className="space-y-2">
                  {prediction.recommendations.map((recommendation, index) => (
                    <li key={index} className="text-sm bg-blue-50 p-3 rounded-lg flex items-start">
                      <span className="text-blue-400 mr-2">→</span>
                      {recommendation}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
};

// Judge insights component  
const JudgeInsights = () => {
  const [judgeName, setJudgeName] = useState('');
  const [insights, setInsights] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSearch = async () => {
    if (!judgeName.trim()) return;
    
    setLoading(true);
    setError(null);

    try {
      const response = await axios.get(`${API}/litigation/judge-insights/${encodeURIComponent(judgeName)}`);
      setInsights(response.data);
    } catch (err) {
      console.error('Judge insights error:', err);
      setError(err.response?.data?.detail || 'Failed to fetch judge insights');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Gavel className="h-5 w-5" />
            <span>Judicial Behavior Analysis</span>
          </CardTitle>
          <CardDescription>
            Get insights into judge decision patterns, settlement rates, and case preferences
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex space-x-2">
            <div className="flex-1">
              <Label htmlFor="judge_name">Judge Name</Label>
              <Input
                id="judge_name"
                placeholder="e.g., Judge Sarah Martinez"
                value={judgeName}
                onChange={(e) => setJudgeName(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              />
            </div>
            <div className="flex items-end">
              <Button onClick={handleSearch} disabled={loading || !judgeName.trim()}>
                {loading ? (
                  <RefreshCw className="h-4 w-4 animate-spin" />
                ) : (
                  <Search className="h-4 w-4" />
                )}
              </Button>
            </div>
          </div>

          {error && (
            <Alert className="mt-4">
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}
        </CardContent>
      </Card>

      {insights && (
        <Card>
          <CardHeader>
            <CardTitle>Judge {insights.judge_name} - Behavioral Profile</CardTitle>
            <CardDescription>
              Court: {insights.court} | Experience: {insights.total_cases} cases analyzed
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Key Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="text-center p-4 bg-blue-50 rounded-lg">
                <Users className="h-6 w-6 text-blue-600 mx-auto mb-2" />
                <div className="text-2xl font-bold text-blue-900">
                  {insights.total_cases}
                </div>
                <div className="text-sm text-blue-600">Total Cases</div>
              </div>

              <div className="text-center p-4 bg-green-50 rounded-lg">
                <Target className="h-6 w-6 text-green-600 mx-auto mb-2" />
                <div className="text-2xl font-bold text-green-900">
                  {(insights.settlement_rate * 100).toFixed(1)}%
                </div>
                <div className="text-sm text-green-600">Settlement Rate</div>
              </div>

              <div className="text-center p-4 bg-yellow-50 rounded-lg">
                <Clock className="h-6 w-6 text-yellow-600 mx-auto mb-2" />
                <div className="text-2xl font-bold text-yellow-900">
                  {Math.round(insights.average_case_duration)} days
                </div>
                <div className="text-sm text-yellow-600">Avg Case Duration</div>
              </div>

              <div className="text-center p-4 bg-purple-50 rounded-lg">
                <TrendingUp className="h-6 w-6 text-purple-600 mx-auto mb-2" />
                <div className="text-2xl font-bold text-purple-900">
                  {(insights.appeal_rate * 100).toFixed(1)}%
                </div>
                <div className="text-sm text-purple-600">Appeal Rate</div>
              </div>
            </div>

            {/* Decision Patterns */}
            <div>
              <h3 className="text-lg font-semibold mb-3">Decision Patterns</h3>
              <div className="space-y-2">
                {Object.entries(insights.outcome_patterns).map(([outcome, rate]) => (
                  <div key={outcome} className="flex items-center justify-between">
                    <span className="font-medium capitalize">{outcome.replace('_', ' ')}</span>
                    <div className="flex items-center space-x-2">
                      <Progress value={rate * 100} className="w-32 h-2" />
                      <span className="text-sm font-medium w-12">
                        {(rate * 100).toFixed(1)}%
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Specialty Areas */}
            <div>
              <h3 className="text-lg font-semibold mb-3">Specialty Areas</h3>
              <div className="flex flex-wrap gap-2">
                {insights.specialty_areas.map((area, index) => (
                  <Badge key={index} variant="secondary">
                    {area.replace('_', ' ')}
                  </Badge>
                ))}
              </div>
            </div>

            {/* Confidence Score */}
            <div className="p-4 bg-gray-50 rounded-lg">
              <h3 className="text-lg font-semibold mb-2">Analysis Confidence</h3>
              <div className="flex items-center space-x-4">
                <Progress value={insights.confidence_score * 100} className="flex-1 h-3" />
                <span className="text-lg font-bold">
                  {(insights.confidence_score * 100).toFixed(1)}%
                </span>
              </div>
              <p className="text-sm text-gray-600 mt-2">
                Based on {insights.total_cases} analyzed cases and judicial history
              </p>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

// Main litigation analytics dashboard
const LitigationAnalytics = ({ onBack }) => {
  const [activeTab, setActiveTab] = useState('predictor');
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(false);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/litigation/analytics-dashboard`);
      setDashboardData(response.data);
    } catch (error) {
      console.error('Dashboard data error:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center space-x-4">
            <Button
              variant="outline"
              size="sm"
              onClick={onBack}
              className="flex items-center space-x-2"
            >
              <ArrowLeft className="h-4 w-4" />
              <span>Back</span>
            </Button>
            <div>
              <h1 className="text-3xl font-bold text-gray-900 flex items-center space-x-3">
                <Scale className="h-8 w-8 text-blue-600" />
                <span>Litigation Analytics Engine</span>
              </h1>
              <p className="text-gray-600 mt-1">
                AI-powered case outcome prediction and strategic litigation insights
              </p>
            </div>
          </div>
          <Badge variant="secondary" className="text-sm">
            Premium Feature
          </Badge>
        </div>

        {/* Dashboard Overview */}
        {dashboardData && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <Card>
              <CardContent className="p-4 text-center">
                <BarChart3 className="h-6 w-6 text-blue-600 mx-auto mb-2" />
                <div className="text-2xl font-bold text-blue-900">
                  {dashboardData.total_predictions || 0}
                </div>
                <div className="text-sm text-blue-600">Total Predictions</div>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent className="p-4 text-center">
                <Target className="h-6 w-6 text-green-600 mx-auto mb-2" />
                <div className="text-2xl font-bold text-green-900">
                  {((dashboardData.accuracy_rate || 0) * 100).toFixed(1)}%
                </div>
                <div className="text-sm text-green-600">Accuracy Rate</div>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent className="p-4 text-center">
                <Users className="h-6 w-6 text-purple-600 mx-auto mb-2" />
                <div className="text-2xl font-bold text-purple-900">
                  {dashboardData.judges_analyzed || 0}
                </div>
                <div className="text-sm text-purple-600">Judges Analyzed</div>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent className="p-4 text-center">
                <FileText className="h-6 w-6 text-orange-600 mx-auto mb-2" />
                <div className="text-2xl font-bold text-orange-900">
                  {dashboardData.cases_analyzed || 0}
                </div>
                <div className="text-sm text-orange-600">Cases Analyzed</div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Main Tabs Interface */}
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-4 mb-8">
            <TabsTrigger value="predictor" className="flex items-center space-x-2">
              <Brain className="h-4 w-4" />
              <span>Case Predictor</span>
            </TabsTrigger>
            <TabsTrigger value="judge" className="flex items-center space-x-2">
              <Gavel className="h-4 w-4" />
              <span>Judge Insights</span>
            </TabsTrigger>
            <TabsTrigger value="settlement" className="flex items-center space-x-2">
              <Calculator className="h-4 w-4" />
              <span>Settlement Analysis</span>
            </TabsTrigger>
            <TabsTrigger value="strategy" className="flex items-center space-x-2">
              <Lightbulb className="h-4 w-4" />
              <span>Strategy Optimizer</span>
            </TabsTrigger>
          </TabsList>

          <TabsContent value="predictor">
            <CaseOutcomePredictor />
          </TabsContent>

          <TabsContent value="judge">
            <JudgeInsights />
          </TabsContent>

          <TabsContent value="settlement">
            <SettlementCalculator />
          </TabsContent>

          <TabsContent value="strategy">
            <LitigationStrategy />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default LitigationAnalytics;