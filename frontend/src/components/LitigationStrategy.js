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
import {
  Lightbulb, Target, TrendingUp, Clock, DollarSign,
  Users, FileText, AlertTriangle, CheckCircle, RefreshCw,
  Brain, Scale, BookOpen, Gavel, Calendar, MessageSquare
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const LitigationStrategy = () => {
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
    client_budget: '',
    timeline_constraints: '',
    opposing_counsel: '',
    strategic_goals: []
  });

  const [recommendations, setRecommendations] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const caseTypes = [
    { value: 'civil', label: 'Civil' },
    { value: 'criminal', label: 'Criminal' },
    { value: 'commercial', label: 'Commercial' },
    { value: 'employment', label: 'Employment' },
    { value: 'intellectual_property', label: 'Intellectual Property' },
    { value: 'family', label: 'Family Law' },
    { value: 'personal_injury', label: 'Personal Injury' },
    { value: 'bankruptcy', label: 'Bankruptcy' },
    { value: 'environmental', label: 'Environmental' },
    { value: 'tax', label: 'Tax Law' }
  ];

  const jurisdictions = [
    { value: 'federal', label: 'Federal' },
    { value: 'california', label: 'California' },
    { value: 'new_york', label: 'New York' },
    { value: 'texas', label: 'Texas' },
    { value: 'florida', label: 'Florida' },
    { value: 'illinois', label: 'Illinois' }
  ];

  const courtLevels = [
    { value: 'district', label: 'District Court' },
    { value: 'circuit', label: 'Circuit Court' },
    { value: 'supreme', label: 'Supreme Court' },
    { value: 'state_trial', label: 'State Trial Court' },
    { value: 'state_appellate', label: 'State Appellate Court' }
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const requestData = {
        ...caseData,
        case_value: caseData.case_value ? parseFloat(caseData.case_value) : null,
        client_budget: caseData.client_budget ? parseFloat(caseData.client_budget) : null,
        witness_count: caseData.witness_count ? parseInt(caseData.witness_count) : null,
        evidence_strength: parseFloat(caseData.evidence_strength),
        case_complexity: parseFloat(caseData.case_complexity)
      };

      const response = await axios.post(`${API}/litigation/strategy-recommendations`, requestData);
      setRecommendations(response.data);
    } catch (err) {
      console.error('Strategy recommendations error:', err);
      setError(err.response?.data?.detail || 'Failed to generate strategy recommendations');
    } finally {
      setLoading(false);
    }
  };

  const getPriorityColor = (priority) => {
    const colors = {
      'high': 'bg-red-100 text-red-800 border-red-200',
      'medium': 'bg-yellow-100 text-yellow-800 border-yellow-200',
      'low': 'bg-green-100 text-green-800 border-green-200'
    };
    return colors[priority] || 'bg-gray-100 text-gray-800 border-gray-200';
  };

  const formatStrategy = (strategy) => {
    if (!strategy || typeof strategy !== 'string') {
      return 'N/A';
    }
    return strategy.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  return (
    <div className="space-y-6">
      {/* Strategy Input Form */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Lightbulb className="h-5 w-5" />
            <span>AI-Powered Litigation Strategy Optimizer</span>
          </CardTitle>
          <CardDescription>
            Get comprehensive strategic recommendations tailored to your case specifics and objectives
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
                <Label htmlFor="court_level">Court Level</Label>
                <Select 
                  value={caseData.court_level} 
                  onValueChange={(value) => setCaseData(prev => ({...prev, court_level: value}))}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {courtLevels.map(level => (
                      <SelectItem key={level.value} value={level.value}>
                        {level.label}
                      </SelectItem>
                    ))}
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
                <Label htmlFor="case_value">Case Value ($)</Label>
                <Input
                  id="case_value"
                  type="number"
                  placeholder="e.g., 750000"
                  value={caseData.case_value}
                  onChange={(e) => setCaseData(prev => ({...prev, case_value: e.target.value}))}
                />
              </div>

              <div>
                <Label htmlFor="client_budget">Client Budget ($)</Label>
                <Input
                  id="client_budget"
                  type="number"
                  placeholder="e.g., 100000"
                  value={caseData.client_budget}
                  onChange={(e) => setCaseData(prev => ({...prev, client_budget: e.target.value}))}
                />
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

              <div>
                <Label htmlFor="opposing_counsel">Opposing Counsel (if known)</Label>
                <Input
                  id="opposing_counsel"
                  placeholder="e.g., Smith & Associates"
                  value={caseData.opposing_counsel}
                  onChange={(e) => setCaseData(prev => ({...prev, opposing_counsel: e.target.value}))}
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
                  {caseData.evidence_strength}/10 ({parseFloat(caseData.evidence_strength) >= 8 ? 'Very Strong' : parseFloat(caseData.evidence_strength) >= 6 ? 'Strong' : parseFloat(caseData.evidence_strength) >= 4 ? 'Moderate' : 'Weak'})
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
              <Label htmlFor="case_facts">Case Facts & Key Issues *</Label>
              <Textarea
                id="case_facts"
                placeholder="Provide detailed case background, legal issues, key facts, and any strategic considerations..."
                value={caseData.case_facts}
                onChange={(e) => setCaseData(prev => ({...prev, case_facts: e.target.value}))}
                className="min-h-32"
              />
            </div>

            <div>
              <Label htmlFor="timeline_constraints">Timeline Constraints or Deadlines</Label>
              <Textarea
                id="timeline_constraints"
                placeholder="Any specific deadlines, urgency factors, or timeline considerations..."
                value={caseData.timeline_constraints}
                onChange={(e) => setCaseData(prev => ({...prev, timeline_constraints: e.target.value}))}
                className="min-h-20"
              />
            </div>

            {error && (
              <Alert>
                <AlertTriangle className="h-4 w-4" />
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            <Button 
              type="submit" 
              disabled={loading || !caseData.case_type || !caseData.jurisdiction || !caseData.case_facts}
              className="w-full"
            >
              {loading ? (
                <>
                  <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                  Generating Strategic Recommendations...
                </>
              ) : (
                <>
                  <Brain className="h-4 w-4 mr-2" />
                  Generate Litigation Strategy
                </>
              )}
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Strategy Recommendations Results */}
      {recommendations && (
        <div className="space-y-6">
          {/* Overview Card */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Target className="h-5 w-5" />
                <span>Strategic Analysis Overview</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Key Metrics */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="text-center p-4 bg-blue-50 rounded-lg">
                  <Scale className="h-6 w-6 text-blue-600 mx-auto mb-2" />
                  <div className="text-2xl font-bold text-blue-900">
                    {formatStrategy(recommendations.recommended_strategy)}
                  </div>
                  <div className="text-sm text-blue-600">Primary Strategy</div>
                </div>

                <div className="text-center p-4 bg-green-50 rounded-lg">
                  <Target className="h-6 w-6 text-green-600 mx-auto mb-2" />
                  <div className="text-2xl font-bold text-green-900">
                    {(recommendations.success_probability * 100).toFixed(1)}%
                  </div>
                  <div className="text-sm text-green-600">Success Probability</div>
                </div>

                <div className="text-center p-4 bg-purple-50 rounded-lg">
                  <Clock className="h-6 w-6 text-purple-600 mx-auto mb-2" />
                  <div className="text-2xl font-bold text-purple-900">
                    {Math.round(recommendations.estimated_duration / 30)} months
                  </div>
                  <div className="text-sm text-purple-600">Est. Duration</div>
                </div>

                <div className="text-center p-4 bg-orange-50 rounded-lg">
                  <DollarSign className="h-6 w-6 text-orange-600 mx-auto mb-2" />
                  <div className="text-2xl font-bold text-orange-900">
                    ${recommendations.estimated_costs?.toLocaleString() || 'N/A'}
                  </div>
                  <div className="text-sm text-orange-600">Est. Costs</div>
                </div>
              </div>

              {/* Confidence Score */}
              <div className="p-4 bg-gray-50 rounded-lg">
                <h3 className="text-lg font-semibold mb-2">Analysis Confidence</h3>
                <div className="flex items-center space-x-4">
                  <Progress value={recommendations.confidence_score * 100} className="flex-1 h-3" />
                  <span className="text-lg font-bold">
                    {(recommendations.confidence_score * 100).toFixed(1)}%
                  </span>
                </div>
                <p className="text-sm text-gray-600 mt-2">
                  Based on case analysis, legal precedents, and strategic factors
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Strategic Recommendations */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Lightbulb className="h-5 w-5" />
                <span>Strategic Recommendations</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              {recommendations.strategic_recommendations && recommendations.strategic_recommendations.length > 0 ? (
                <div className="space-y-3">
                  {recommendations.strategic_recommendations.map((rec, index) => (
                    <div key={index} className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                      <div className="flex items-start space-x-3">
                        <div className="flex-shrink-0 w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-bold">
                          {index + 1}
                        </div>
                        <div className="flex-1">
                          <p className="text-blue-800">{rec}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500">AI-powered strategic recommendations analyzing...</p>
              )}
            </CardContent>
          </Card>

          {/* Risk Assessment */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="text-red-700 flex items-center space-x-2">
                  <AlertTriangle className="h-5 w-5" />
                  <span>Risk Factors</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                {recommendations.risk_factors && recommendations.risk_factors.length > 0 ? (
                  <ul className="space-y-2">
                    {recommendations.risk_factors.map((risk, index) => (
                      <li key={index} className="text-sm text-red-600 flex items-start">
                        <span className="text-red-400 mr-2 mt-1">⚠</span>
                        {risk}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-gray-500">Risk analysis in progress...</p>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-green-700 flex items-center space-x-2">
                  <CheckCircle className="h-5 w-5" />
                  <span>Strategic Advantages</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                {recommendations.strategic_advantages && recommendations.strategic_advantages.length > 0 ? (
                  <ul className="space-y-2">
                    {recommendations.strategic_advantages.map((advantage, index) => (
                      <li key={index} className="text-sm text-green-600 flex items-start">
                        <span className="text-green-400 mr-2 mt-1">✓</span>
                        {advantage}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-gray-500">Strategic advantage analysis in progress...</p>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Action Plan */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Calendar className="h-5 w-5" />
                <span>Recommended Action Plan</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              {recommendations.action_plan && recommendations.action_plan.length > 0 ? (
                <div className="space-y-4">
                  {recommendations.action_plan.map((action, index) => (
                    <div key={index} className="flex items-start space-x-4 p-4 bg-white border border-gray-200 rounded-lg">
                      <div className="flex-shrink-0">
                        <div className="w-8 h-8 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center font-semibold">
                          {index + 1}
                        </div>
                      </div>
                      <div className="flex-1">
                        <div className="font-medium text-gray-900">{action.action || action}</div>
                        {action.timeline && (
                          <div className="text-sm text-gray-500 mt-1">
                            <Clock className="h-3 w-3 inline mr-1" />
                            {action.timeline}
                          </div>
                        )}
                        {action.priority && (
                          <Badge className={`mt-2 text-xs ${getPriorityColor(action.priority)}`}>
                            {action.priority} Priority
                          </Badge>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500">Action plan generation in progress...</p>
              )}
            </CardContent>
          </Card>

          {/* Alternative Strategies */}
          {recommendations.alternative_strategies && recommendations.alternative_strategies.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <BookOpen className="h-5 w-5" />
                  <span>Alternative Strategies</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {recommendations.alternative_strategies.map((strategy, index) => (
                    <div key={index} className="p-4 bg-gray-50 border rounded-lg">
                      <h4 className="font-semibold text-gray-900 mb-2">
                        {formatStrategy(strategy.name || `Alternative ${index + 1}`)}
                      </h4>
                      <p className="text-sm text-gray-600 mb-3">{strategy.description || strategy}</p>
                      {strategy.pros && (
                        <div className="mb-2">
                          <div className="text-xs font-medium text-green-700 mb-1">Pros:</div>
                          <ul className="text-xs text-green-600 space-y-1">
                            {strategy.pros.map((pro, proIndex) => (
                              <li key={proIndex} className="flex items-start">
                                <span className="text-green-400 mr-1">+</span>
                                {pro}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                      {strategy.cons && (
                        <div>
                          <div className="text-xs font-medium text-red-700 mb-1">Cons:</div>
                          <ul className="text-xs text-red-600 space-y-1">
                            {strategy.cons.map((con, conIndex) => (
                              <li key={conIndex} className="flex items-start">
                                <span className="text-red-400 mr-1">-</span>
                                {con}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      )}
    </div>
  );
};

export default LitigationStrategy;