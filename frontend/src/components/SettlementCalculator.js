import React, { useState } from 'react';
import axios from 'axios';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Alert, AlertDescription } from './ui/alert';
import { Switch } from './ui/switch';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import {
  Calculator, DollarSign, Target, Clock, TrendingUp,
  AlertTriangle, CheckCircle, RefreshCw, PieChart,
  BarChart3, Calendar, Users, Brain, Zap, LineChart,
  TrendingDown, Activity, Layers, Settings
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const SettlementCalculator = () => {
  const [caseData, setCaseData] = useState({
    case_type: '',
    case_value: '',
    evidence_strength: 5,
    case_complexity: 0.5,
    jurisdiction: '',
    judge_name: '',
    case_facts: '',
    legal_issues: [],
    witness_count: '',
    opposing_party_resources: 'medium'
  });

  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [advancedMode, setAdvancedMode] = useState(false);
  const [analysisMode, setAnalysisMode] = useState('advanced');
  const [monteCarloIterations, setMonteCarloIterations] = useState(10000);

  const caseTypes = [
    { value: 'commercial', label: 'Commercial' },
    { value: 'employment', label: 'Employment' },
    { value: 'personal_injury', label: 'Personal Injury' },
    { value: 'intellectual_property', label: 'Intellectual Property' },
    { value: 'civil', label: 'Civil' },
    { value: 'family', label: 'Family Law' },
    { value: 'environmental', label: 'Environmental' }
  ];

  const jurisdictions = [
    { value: 'federal', label: 'Federal' },
    { value: 'california', label: 'California' },
    { value: 'new_york', label: 'New York' },
    { value: 'texas', label: 'Texas' },
    { value: 'florida', label: 'Florida' }
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
        evidence_strength: parseFloat(caseData.evidence_strength),
        case_complexity: parseFloat(caseData.case_complexity)
      };

      // Add advanced options if in advanced mode
      if (advancedMode) {
        requestData.analysis_mode = analysisMode;
        requestData.monte_carlo_iterations = monteCarloIterations;
        requestData.include_comparative = true;
        requestData.include_market_analysis = true;
      }

      const endpoint = advancedMode 
        ? `${API}/litigation/settlement-probability-advanced` 
        : `${API}/litigation/settlement-probability`;
        
      const response = await axios.post(endpoint, requestData);
      setAnalysis(response.data);
    } catch (err) {
      console.error('Settlement analysis error:', err);
      setError(err.response?.data?.detail || 'Failed to calculate settlement probability');
    } finally {
      setLoading(false);
    }
  };

  const getUrgencyColor = (urgency) => {
    if (urgency > 0.7) return 'text-red-600 bg-red-100';
    if (urgency > 0.5) return 'text-yellow-600 bg-yellow-100';
    return 'text-green-600 bg-green-100';
  };

  const formatTiming = (timing) => {
    return timing?.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()) || 'Not specified';
  };

  return (
    <div className="space-y-6">
      {/* Settlement Calculator Form */}
      <Card>
        <CardHeader>
          <div className="flex justify-between items-start">
            <div>
              <CardTitle className="flex items-center space-x-2">
                <Calculator className="h-5 w-5" />
                <span>Settlement Probability Calculator</span>
                {advancedMode && <Badge className="ml-2 bg-gradient-to-r from-blue-500 to-purple-500 text-white"><Brain className="h-3 w-3 mr-1" />Advanced</Badge>}
              </CardTitle>
              <CardDescription>
                {advancedMode 
                  ? "Enhanced settlement analysis with AI consensus, Monte Carlo simulation, and market intelligence" 
                  : "Calculate settlement likelihood and optimal negotiation strategies using AI analysis"
                }
              </CardDescription>
            </div>
            <div className="flex items-center space-x-2">
              <Label htmlFor="advanced-mode" className="text-sm">Advanced Mode</Label>
              <Switch 
                id="advanced-mode"
                checked={advancedMode}
                onCheckedChange={setAdvancedMode}
              />
            </div>
          </div>
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
                <Label htmlFor="jurisdiction">Jurisdiction</Label>
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
                <Label htmlFor="case_value">Case Value ($) *</Label>
                <Input
                  id="case_value"
                  type="number"
                  placeholder="e.g., 500000"
                  value={caseData.case_value}
                  onChange={(e) => setCaseData(prev => ({...prev, case_value: e.target.value}))}
                />
              </div>

              <div>
                <Label htmlFor="opposing_party_resources">Opposing Party Resources</Label>
                <Select 
                  value={caseData.opposing_party_resources} 
                  onValueChange={(value) => setCaseData(prev => ({...prev, opposing_party_resources: value}))}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="low">Low Resources</SelectItem>
                    <SelectItem value="medium">Medium Resources</SelectItem>
                    <SelectItem value="high">High Resources</SelectItem>
                    <SelectItem value="very_high">Very High Resources</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label htmlFor="judge_name">Judge Name (if known)</Label>
                <Input
                  id="judge_name"
                  placeholder="e.g., Judge Sarah Martinez"
                  value={caseData.judge_name}
                  onChange={(e) => setCaseData(prev => ({...prev, judge_name: e.target.value}))}
                />
              </div>

              <div>
                <Label htmlFor="witness_count">Number of Witnesses</Label>
                <Input
                  id="witness_count"
                  type="number"
                  placeholder="e.g., 8"
                  value={caseData.witness_count}
                  onChange={(e) => setCaseData(prev => ({...prev, witness_count: e.target.value}))}
                />
              </div>
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

            <div>
              <Label htmlFor="case_facts">Case Background & Key Issues</Label>
              <Textarea
                id="case_facts"
                placeholder="Describe the case background, key legal issues, and any relevant circumstances..."
                value={caseData.case_facts}
                onChange={(e) => setCaseData(prev => ({...prev, case_facts: e.target.value}))}
                className="min-h-24"
              />
            </div>

            {/* Advanced Options */}
            {advancedMode && (
              <Card className="bg-gradient-to-r from-blue-50 to-purple-50 border-blue-200">
                <CardHeader className="pb-3">
                  <CardTitle className="text-lg flex items-center">
                    <Settings className="h-4 w-4 mr-2" />
                    Advanced Analytics Options
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="analysis_mode">Analysis Mode</Label>
                      <Select 
                        value={analysisMode} 
                        onValueChange={setAnalysisMode}
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="basic">Basic Enhanced</SelectItem>
                          <SelectItem value="advanced">Full Advanced (Recommended)</SelectItem>
                          <SelectItem value="monte_carlo">Monte Carlo Focus</SelectItem>
                          <SelectItem value="comparative">Comparative Analysis</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    <div>
                      <Label htmlFor="monte_carlo_iterations">Monte Carlo Iterations</Label>
                      <Select 
                        value={monteCarloIterations.toString()} 
                        onValueChange={(value) => setMonteCarloIterations(parseInt(value))}
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="5000">5,000 (Fast)</SelectItem>
                          <SelectItem value="10000">10,000 (Recommended)</SelectItem>
                          <SelectItem value="25000">25,000 (Comprehensive)</SelectItem>
                          <SelectItem value="50000">50,000 (Maximum)</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>

                  <div className="flex items-center space-x-4 text-sm text-blue-700">
                    <div className="flex items-center">
                      <Brain className="h-4 w-4 mr-1" />
                      <span>Multi-AI Consensus</span>
                    </div>
                    <div className="flex items-center">
                      <Activity className="h-4 w-4 mr-1" />
                      <span>Monte Carlo Simulation</span>
                    </div>
                    <div className="flex items-center">
                      <LineChart className="h-4 w-4 mr-1" />
                      <span>Market Analysis</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {error && (
              <Alert>
                <AlertTriangle className="h-4 w-4" />
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            <Button 
              type="submit" 
              disabled={loading || !caseData.case_type || !caseData.case_value}
              className={`w-full ${advancedMode ? 'bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600' : ''}`}
            >
              {loading ? (
                <>
                  <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                  {advancedMode ? 'Running Advanced AI Analysis...' : 'Calculating Settlement Probability...'}
                </>
              ) : (
                <>
                  {advancedMode ? <Brain className="h-4 w-4 mr-2" /> : <Calculator className="h-4 w-4 mr-2" />}
                  {advancedMode ? 'Run Advanced Settlement Analysis' : 'Calculate Settlement Analysis'}
                </>
              )}
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Settlement Analysis Results */}
      {analysis && (
        <div className="space-y-6">
          {/* Primary Settlement Metrics */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Target className="h-5 w-5" />
                <span>Settlement Analysis Results</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Key Metrics Grid */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="text-center p-6 bg-blue-50 rounded-lg">
                  <Target className="h-8 w-8 text-blue-600 mx-auto mb-3" />
                  <div className="text-3xl font-bold text-blue-900 mb-2">
                    {(analysis.settlement_probability * 100).toFixed(1)}%
                  </div>
                  <div className="text-sm text-blue-600">Settlement Probability</div>
                  <Progress value={analysis.settlement_probability * 100} className="mt-2 h-2" />
                  {advancedMode && analysis.ai_consensus_score && (
                    <div className="text-xs text-blue-500 mt-1">
                      AI Consensus: {(analysis.ai_consensus_score * 100).toFixed(0)}%
                    </div>
                  )}
                </div>

                <div className="text-center p-6 bg-green-50 rounded-lg">
                  <DollarSign className="h-8 w-8 text-green-600 mx-auto mb-3" />
                  <div className="text-3xl font-bold text-green-900 mb-2">
                    ${analysis.expected_settlement_value?.toLocaleString() || 'N/A'}
                  </div>
                  <div className="text-sm text-green-600">Expected Settlement</div>
                  {advancedMode && analysis.volatility_index && (
                    <div className="text-xs text-green-500 mt-1">
                      Volatility: {(analysis.volatility_index * 100).toFixed(0)}%
                    </div>
                  )}
                </div>

                <div className="text-center p-6 bg-purple-50 rounded-lg">
                  <Clock className="h-8 w-8 text-purple-600 mx-auto mb-3" />
                  <div className="text-3xl font-bold text-purple-900 mb-2">
                    {formatTiming(analysis.optimal_timing)}
                  </div>
                  <div className="text-sm text-purple-600">Optimal Timing</div>
                  {advancedMode && analysis.strategic_advantage_score && (
                    <div className="text-xs text-purple-500 mt-1">
                      Strategic Advantage: {(analysis.strategic_advantage_score * 100).toFixed(0)}%
                    </div>
                  )}
                </div>
              </div>

              {/* Advanced Metrics Display */}
              {advancedMode && (analysis.monte_carlo_results || analysis.market_trend_adjustment !== null) && (
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                    <Activity className="h-5 w-5 mr-2" />
                    Advanced Analytics
                  </h3>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    {/* Monte Carlo Results */}
                    {analysis.monte_carlo_results && (
                      <div className="p-4 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg border border-blue-200">
                        <div className="flex items-center mb-2">
                          <PieChart className="h-4 w-4 text-blue-600 mr-2" />
                          <span className="text-sm font-semibold text-blue-900">Monte Carlo</span>
                        </div>
                        <div className="space-y-1 text-xs">
                          <div>Mean: {(analysis.monte_carlo_results.mean_settlement_probability * 100).toFixed(1)}%</div>
                          <div>Std Dev: ±{(analysis.monte_carlo_results.std_settlement_probability * 100).toFixed(1)}%</div>
                          <div>Simulations: {analysis.monte_carlo_results.simulation_count?.toLocaleString()}</div>
                          {analysis.monte_carlo_results.confidence_intervals?.['95%'] && (
                            <div className="text-blue-600 font-medium">
                              95% CI: {(analysis.monte_carlo_results.confidence_intervals['95%'][0] * 100).toFixed(0)}%-{(analysis.monte_carlo_results.confidence_intervals['95%'][1] * 100).toFixed(0)}%
                            </div>
                          )}
                        </div>
                      </div>
                    )}

                    {/* Market Trends */}
                    {analysis.market_trend_adjustment !== null && (
                      <div className="p-4 bg-gradient-to-br from-green-50 to-emerald-50 rounded-lg border border-green-200">
                        <div className="flex items-center mb-2">
                          <LineChart className="h-4 w-4 text-green-600 mr-2" />
                          <span className="text-sm font-semibold text-green-900">Market Trends</span>
                        </div>
                        <div className="space-y-1 text-xs">
                          <div className={`font-medium ${analysis.market_trend_adjustment >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {analysis.market_trend_adjustment >= 0 ? '+' : ''}{(analysis.market_trend_adjustment * 100).toFixed(1)}%
                          </div>
                          <div className="text-gray-600">
                            {analysis.market_trend_adjustment > 0.02 ? 'Favorable' : 
                             analysis.market_trend_adjustment < -0.02 ? 'Challenging' : 'Neutral'}
                          </div>
                          <div className="text-gray-500">Market conditions</div>
                        </div>
                      </div>
                    )}

                    {/* AI Analysis */}
                    {analysis.ai_consensus_score && (
                      <div className="p-4 bg-gradient-to-br from-purple-50 to-violet-50 rounded-lg border border-purple-200">
                        <div className="flex items-center mb-2">
                          <Brain className="h-4 w-4 text-purple-600 mr-2" />
                          <span className="text-sm font-semibold text-purple-900">AI Consensus</span>
                        </div>
                        <div className="space-y-1 text-xs">
                          <div className="font-medium text-purple-600">
                            {(analysis.ai_consensus_score * 100).toFixed(0)}% Agreement
                          </div>
                          <div className="text-gray-600">
                            {analysis.ai_consensus_score > 0.8 ? 'High' : 
                             analysis.ai_consensus_score > 0.6 ? 'Medium' : 'Mixed'} Consensus
                          </div>
                          <div className="text-gray-500">Multi-AI analysis</div>
                        </div>
                      </div>
                    )}

                    {/* Processing Time */}
                    {analysis.processing_time && (
                      <div className="p-4 bg-gradient-to-br from-gray-50 to-slate-50 rounded-lg border border-gray-200">
                        <div className="flex items-center mb-2">
                          <Zap className="h-4 w-4 text-gray-600 mr-2" />
                          <span className="text-sm font-semibold text-gray-900">Performance</span>
                        </div>
                        <div className="space-y-1 text-xs">
                          <div className="font-medium text-gray-600">
                            {analysis.processing_time.toFixed(2)}s
                          </div>
                          <div className="text-gray-500">Analysis time</div>
                          <div className="text-gray-500 capitalize">
                            {analysis.analysis_mode || 'advanced'} mode
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Settlement Range */}
              {(analysis.plaintiff_settlement_range || analysis.defendant_settlement_range) && (
                <div>
                  <h3 className="text-lg font-semibold mb-3">Expected Settlement Range</h3>
                  <div className="p-4 bg-gray-50 rounded-lg">
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-sm text-gray-600">Conservative</span>
                      <span className="text-sm text-gray-600">Optimistic</span>
                    </div>
                    <div className="relative">
                      <div className="h-8 bg-gradient-to-r from-red-200 via-yellow-200 to-green-200 rounded-full"></div>
                      <div className="absolute top-0 left-0 right-0 h-8 flex items-center justify-between px-4">
                        <span className="text-sm font-semibold text-gray-800">
                          ${(analysis.plaintiff_settlement_range?.low || analysis.defendant_settlement_range?.low || 0).toLocaleString()}
                        </span>
                        <span className="text-sm font-semibold text-gray-800">
                          ${(analysis.plaintiff_settlement_range?.high || analysis.defendant_settlement_range?.high || 0).toLocaleString()}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Settlement Urgency */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-4 bg-white border rounded-lg">
                  <h4 className="font-semibold mb-2 flex items-center">
                    <TrendingUp className="h-4 w-4 mr-2" />
                    Settlement Urgency
                  </h4>
                  <div className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${getUrgencyColor(analysis.settlement_urgency_score)}`}>
                    {analysis.settlement_urgency_score > 0.7 ? 'High Urgency' :
                     analysis.settlement_urgency_score > 0.5 ? 'Medium Urgency' : 'Low Urgency'}
                  </div>
                  <div className="mt-2">
                    <Progress value={analysis.settlement_urgency_score * 100} className="h-2" />
                  </div>
                </div>

                <div className="p-4 bg-white border rounded-lg">
                  <h4 className="font-semibold mb-2 flex items-center">
                    <BarChart3 className="h-4 w-4 mr-2" />
                    Confidence Level
                  </h4>
                  <div className="text-2xl font-bold text-gray-900">
                    {(analysis.confidence_score * 100).toFixed(1)}%
                  </div>
                  <div className="mt-2">
                    <Progress value={analysis.confidence_score * 100} className="h-2" />
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Strategic Insights */}
          <Card>
            <CardHeader>
              <CardTitle>Strategic Settlement Insights</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Key Settlement Factors */}
              {analysis.key_settlement_factors && analysis.key_settlement_factors.length > 0 && (
                <div>
                  <h3 className="text-lg font-semibold mb-2 text-blue-700 flex items-center">
                    <CheckCircle className="h-4 w-4 mr-2" />
                    Key Settlement Factors
                  </h3>
                  <ul className="space-y-2">
                    {analysis.key_settlement_factors.map((factor, index) => (
                      <li key={index} className="text-sm text-blue-600 flex items-start">
                        <span className="text-blue-400 mr-2">•</span>
                        {factor}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* General Recommendations */}
              {analysis.recommendations && analysis.recommendations.length > 0 && (
                <div>
                  <h3 className="text-lg font-semibold mb-2 text-green-700 flex items-center">
                    <Users className="h-4 w-4 mr-2" />
                    Recommendations
                  </h3>
                  <ul className="space-y-2">
                    {analysis.recommendations.map((recommendation, index) => (
                      <li key={index} className="text-sm text-green-600 flex items-start">
                        <span className="text-green-400 mr-2">→</span>
                        {recommendation}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* AI Analysis Summary */}
              {analysis.ai_insights && (
                <div className="p-4 bg-blue-50 rounded-lg">
                  <h3 className="font-semibold mb-2">AI Analysis Summary</h3>
                  <p className="text-sm text-gray-700">{analysis.ai_insights}</p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Timeline Recommendations */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Calendar className="h-5 w-5" />
                <span>Settlement Timeline Recommendations</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                  <div>
                    <div className="font-semibold text-green-800">Immediate (0-30 days)</div>
                    <div className="text-sm text-green-600">Initial settlement discussions</div>
                  </div>
                  <div className="text-green-600">
                    {analysis.settlement_probability > 0.7 ? '✓ Recommended' : '○ Optional'}
                  </div>
                </div>

                <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                  <div>
                    <div className="font-semibold text-blue-800">Early Discovery (30-90 days)</div>
                    <div className="text-sm text-blue-600">Post-discovery settlement talks</div>
                  </div>
                  <div className="text-blue-600">
                    {formatTiming(analysis.optimal_timing) === 'Early' ? '✓ Optimal Window' : '○ Alternative'}
                  </div>
                </div>

                <div className="flex items-center justify-between p-3 bg-yellow-50 rounded-lg">
                  <div>
                    <div className="font-semibold text-yellow-800">Pre-Trial (90+ days)</div>
                    <div className="text-sm text-yellow-600">Final settlement opportunity</div>
                  </div>
                  <div className="text-yellow-600">
                    {analysis.settlement_urgency_score < 0.5 ? '✓ Viable Option' : '○ Last Resort'}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
};

export default SettlementCalculator;