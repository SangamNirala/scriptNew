import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  BarChart, Bar, PieChart, Pie, Cell, AreaChart, Area, ComposedChart, ScatterChart, Scatter,
  RadialBarChart, RadialBar, Treemap
} from 'recharts';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { 
  TrendingUp, TrendingDown, DollarSign, Clock, Users, Shield, 
  BarChart3, PieChart as PieChartIcon, Activity, Target,
  Briefcase, AlertTriangle, CheckCircle, ArrowLeft, Download,
  RefreshCw, Brain, Zap, Eye, Settings, FileDown, Share2,
  Cpu, Server, Gauge, TrendingUpIcon
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Enhanced color schemes for charts
const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#06B6D4', '#EC4899', '#14B8A6'];
const RISK_COLORS = { LOW: '#10B981', MEDIUM: '#F59E0B', HIGH: '#EF4444', CRITICAL: '#DC2626' };
const GRADIENT_COLORS = {
  primary: ['#3B82F6', '#1D4ED8'],
  success: ['#10B981', '#047857'],
  warning: ['#F59E0B', '#D97706'],
  danger: ['#EF4444', '#DC2626']
};

// Enhanced Metric Card with more visual appeal
const EnhancedMetricCard = ({ title, value, change, icon: Icon, color = "blue", trend, subtitle, loading = false }) => (
  <Card className="relative overflow-hidden transition-all duration-300 hover:shadow-lg">
    <CardContent className="p-6">
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-600 mb-1">{title}</p>
          <p className="text-3xl font-bold text-gray-900 mb-1">
            {loading ? <div className="animate-pulse bg-gray-200 h-8 w-20 rounded"></div> : value}
          </p>
          {subtitle && <p className="text-xs text-gray-500">{subtitle}</p>}
          {change !== undefined && (
            <div className={`flex items-center mt-2 text-sm ${change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {change >= 0 ? <TrendingUp className="h-4 w-4 mr-1" /> : <TrendingDown className="h-4 w-4 mr-1" />}
              {Math.abs(change)}% from last period
            </div>
          )}
          {trend && (
            <div className="mt-2">
              <div className={`text-xs px-2 py-1 rounded-full inline-block ${
                trend === 'up' ? 'bg-green-100 text-green-800' : 
                trend === 'down' ? 'bg-red-100 text-red-800' : 
                'bg-gray-100 text-gray-800'
              }`}>
                {trend === 'up' ? '↗ Trending Up' : trend === 'down' ? '↘ Trending Down' : '→ Stable'}
              </div>
            </div>
          )}
        </div>
        <div className={`p-4 rounded-full bg-gradient-to-br from-${color}-100 to-${color}-200`}>
          <Icon className={`h-8 w-8 text-${color}-600`} />
        </div>
      </div>
    </CardContent>
    <div className={`absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-${color}-400 to-${color}-600`}></div>
  </Card>
);

// Real-time indicator component
const RealTimeIndicator = ({ lastUpdated, isLive = true }) => (
  <div className="flex items-center text-sm text-gray-500">
    <div className={`w-2 h-2 rounded-full mr-2 ${isLive ? 'bg-green-500 animate-pulse' : 'bg-gray-400'}`}></div>
    {isLive ? 'Live' : `Updated ${lastUpdated}`}
  </div>
);

// Export functionality component
const ExportControls = ({ onExport, loading = false }) => (
  <div className="flex items-center space-x-2">
    <Select onValueChange={(value) => onExport(value)} disabled={loading}>
      <SelectTrigger className="w-40">
        <SelectValue placeholder="Export as..." />
      </SelectTrigger>
      <SelectContent>
        <SelectItem value="pdf">PDF Report</SelectItem>
        <SelectItem value="excel">Excel File</SelectItem>
        <SelectItem value="csv">CSV Data</SelectItem>
      </SelectContent>
    </Select>
    <Button variant="outline" size="sm" disabled={loading}>
      <Share2 className="h-4 w-4 mr-2" />
      Share
    </Button>
  </div>
);

const AnalyticsDashboard = ({ onBack }) => {
  const [dashboardData, setDashboardData] = useState(null);
  const [performanceMetrics, setPerformanceMetrics] = useState(null);
  const [costAnalysis, setCostAnalysis] = useState(null);
  const [negotiationInsights, setNegotiationInsights] = useState(null);
  const [marketIntelligence, setMarketIntelligence] = useState(null);
  
  // New enhanced state
  const [predictiveInsights, setPredictiveInsights] = useState(null);
  const [advancedMetrics, setAdvancedMetrics] = useState(null);
  const [realTimeStats, setRealTimeStats] = useState(null);
  const [complianceDeepDive, setComplianceDeepDive] = useState(null);
  const [integrationMetrics, setIntegrationMetrics] = useState(null);
  
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [filters, setFilters] = useState({
    dateRange: '',
    contractTypes: '',
    jurisdictions: ''
  });
  const [refreshing, setRefreshing] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(false);

  useEffect(() => {
    loadAnalyticsData();
  }, []);

  // Auto-refresh functionality
  useEffect(() => {
    let interval;
    if (autoRefresh) {
      interval = setInterval(() => {
        loadRealTimeData();
      }, 30000); // Refresh every 30 seconds
    }
    return () => clearInterval(interval);
  }, [autoRefresh]);

  const loadAnalyticsData = async () => {
    try {
      setLoading(true);
      
      // Load all analytics data including new enhanced endpoints
      const [
        dashboardRes, performanceRes, costRes, negotiationRes, marketRes,
        advancedRes, realTimeRes, complianceRes, integrationRes
      ] = await Promise.all([
        axios.get(`${API}/analytics/dashboard`),
        axios.get(`${API}/analytics/performance-metrics`),
        axios.get(`${API}/analytics/cost-analysis`),
        axios.get(`${API}/analytics/negotiation-insights`),
        axios.get(`${API}/analytics/market-intelligence`),
        axios.get(`${API}/analytics/advanced-metrics`).catch(() => ({ data: null })),
        axios.get(`${API}/analytics/real-time-stats`).catch(() => ({ data: null })),
        axios.get(`${API}/analytics/compliance-deep-dive`).catch(() => ({ data: null })),
        axios.get(`${API}/analytics/integration-metrics`).catch(() => ({ data: null }))
      ]);
      
      setDashboardData(dashboardRes.data);
      setPerformanceMetrics(performanceRes.data);
      setCostAnalysis(costRes.data);
      setNegotiationInsights(negotiationRes.data);
      setMarketIntelligence(marketRes.data);
      setAdvancedMetrics(advancedRes.data);
      setRealTimeStats(realTimeRes.data);
      setComplianceDeepDive(complianceRes.data);
      setIntegrationMetrics(integrationRes.data);
      
    } catch (error) {
      console.error('Error loading analytics data:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadRealTimeData = async () => {
    try {
      setRefreshing(true);
      const realTimeRes = await axios.get(`${API}/analytics/real-time-stats`);
      setRealTimeStats(realTimeRes.data);
    } catch (error) {
      console.error('Error loading real-time data:', error);
    } finally {
      setRefreshing(false);
    }
  };

  const loadPredictiveInsights = async (contractType = 'nda', jurisdiction = 'US') => {
    try {
      const response = await axios.get(`${API}/analytics/predictive-insights`, {
        params: { contract_type: contractType, jurisdiction }
      });
      setPredictiveInsights(response.data);
    } catch (error) {
      console.error('Error loading predictive insights:', error);
    }
  };

  const handleExport = async (exportType) => {
    try {
      const response = await axios.post(`${API}/analytics/export-data`, {
        export_type: exportType,
        data_types: ['overview', 'performance', 'costs', 'negotiations'],
        filters: filters
      });
      
      // In a real implementation, you would handle file download
      console.log('Export data:', response.data);
      alert(`Export initiated. File will be ready for download shortly.`);
    } catch (error) {
      console.error('Error exporting data:', error);
      alert('Export failed. Please try again.');
    }
  };

  const applyFilters = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      if (filters.dateRange) params.append('date_range', filters.dateRange);
      if (filters.contractTypes) params.append('contract_types', filters.contractTypes);
      if (filters.jurisdictions) params.append('jurisdictions', filters.jurisdictions);
      
      const response = await axios.get(`${API}/analytics/dashboard?${params}`);
      setDashboardData(response.data);
    } catch (error) {
      console.error('Error applying filters:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="text-center">
          <div className="relative">
            <div className="animate-spin rounded-full h-16 w-16 border-4 border-blue-200 border-t-blue-600 mx-auto"></div>
            <div className="animate-pulse absolute inset-0 rounded-full h-16 w-16 border-4 border-transparent border-t-blue-400 mx-auto"></div>
          </div>
          <p className="mt-6 text-lg text-gray-700 font-medium">Loading Advanced Analytics...</p>
          <p className="mt-2 text-sm text-gray-500">Gathering insights from your data</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-8xl mx-auto p-6 bg-gray-50 min-h-screen">
      {/* Enhanced Header */}
      <div className="bg-white rounded-lg shadow-sm border p-6 mb-8">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="p-3 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg">
              <BarChart3 className="h-8 w-8 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Business Intelligence & Analytics</h1>
              <p className="text-gray-600 mt-1">Comprehensive insights powered by AI and machine learning</p>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <RealTimeIndicator 
              lastUpdated="2 min ago" 
              isLive={autoRefresh}
            />
            <Button
              onClick={() => setAutoRefresh(!autoRefresh)}
              variant={autoRefresh ? "default" : "outline"}
              size="sm"
            >
              <RefreshCw className={`h-4 w-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
              {autoRefresh ? 'Live' : 'Auto-refresh'}
            </Button>
            <ExportControls onExport={handleExport} />
            <Button onClick={onBack} variant="outline" className="flex items-center">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Dashboard
            </Button>
          </div>
        </div>
      </div>

      {/* Real-time Stats Bar */}
      {realTimeStats && (
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-8">
          <Card className="border-l-4 border-l-blue-500">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Today</p>
                  <p className="text-2xl font-bold">{realTimeStats.current_stats?.contracts_today || 0}</p>
                </div>
                <Activity className="h-6 w-6 text-blue-500" />
              </div>
            </CardContent>
          </Card>
          <Card className="border-l-4 border-l-green-500">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">This Week</p>
                  <p className="text-2xl font-bold">{realTimeStats.current_stats?.contracts_this_week || 0}</p>
                </div>
                <TrendingUpIcon className="h-6 w-6 text-green-500" />
              </div>
            </CardContent>
          </Card>
          <Card className="border-l-4 border-l-purple-500">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Active Sessions</p>
                  <p className="text-2xl font-bold">{realTimeStats.current_stats?.active_sessions || 0}</p>
                </div>
                <Users className="h-6 w-6 text-purple-500" />
              </div>
            </CardContent>
          </Card>
          <Card className="border-l-4 border-l-orange-500">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Response Time</p>
                  <p className="text-2xl font-bold">{realTimeStats.system_performance?.response_time_avg || 'N/A'}</p>
                </div>
                <Gauge className="h-6 w-6 text-orange-500" />
              </div>
            </CardContent>
          </Card>
          <Card className="border-l-4 border-l-red-500">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">System Health</p>
                  <p className="text-lg font-bold text-green-600">{realTimeStats.status || 'Healthy'}</p>
                </div>
                <Server className="h-6 w-6 text-red-500" />
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Filters */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle>Filters</CardTitle>
          <CardDescription>Customize your analytics view</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <Label htmlFor="dateRange">Date Range</Label>
              <Select value={filters.dateRange} onValueChange={(value) => setFilters({...filters, dateRange: value})}>
                <SelectTrigger>
                  <SelectValue placeholder="Select period" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="7d">Last 7 days</SelectItem>
                  <SelectItem value="30d">Last 30 days</SelectItem>
                  <SelectItem value="90d">Last 90 days</SelectItem>
                  <SelectItem value="1y">Last year</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label htmlFor="contractTypes">Contract Types</Label>
              <Input
                placeholder="e.g. NDA,Employment"
                value={filters.contractTypes}
                onChange={(e) => setFilters({...filters, contractTypes: e.target.value})}
              />
            </div>
            <div>
              <Label htmlFor="jurisdictions">Jurisdictions</Label>
              <Input
                placeholder="e.g. US,UK,EU"
                value={filters.jurisdictions}
                onChange={(e) => setFilters({...filters, jurisdictions: e.target.value})}
              />
            </div>
            <div className="flex items-end">
              <Button onClick={applyFilters} className="w-full">
                Apply Filters
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Analytics Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-8 bg-white p-1 rounded-lg border">
          <TabsTrigger value="overview" className="flex items-center space-x-2">
            <BarChart3 className="h-4 w-4" />
            <span>Overview</span>
          </TabsTrigger>
          <TabsTrigger value="performance" className="flex items-center space-x-2">
            <Target className="h-4 w-4" />
            <span>Performance</span>
          </TabsTrigger>
          <TabsTrigger value="costs" className="flex items-center space-x-2">
            <DollarSign className="h-4 w-4" />
            <span>Costs</span>
          </TabsTrigger>
          <TabsTrigger value="negotiations" className="flex items-center space-x-2">
            <Users className="h-4 w-4" />
            <span>Negotiations</span>
          </TabsTrigger>
          <TabsTrigger value="market" className="flex items-center space-x-2">
            <TrendingUp className="h-4 w-4" />
            <span>Market</span>
          </TabsTrigger>
          <TabsTrigger value="predictive" className="flex items-center space-x-2">
            <Brain className="h-4 w-4" />
            <span>AI Insights</span>
          </TabsTrigger>
          <TabsTrigger value="compliance" className="flex items-center space-x-2">
            <Shield className="h-4 w-4" />
            <span>Compliance</span>
          </TabsTrigger>
          <TabsTrigger value="system" className="flex items-center space-x-2">
            <Server className="h-4 w-4" />
            <span>System</span>
          </TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-6">
          {/* Key Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <MetricCard
              title="Total Contracts"
              value={dashboardData?.overview?.total_contracts || 0}
              icon={Briefcase}
              color="blue"
            />
            <MetricCard
              title="Success Rate"
              value={`${performanceMetrics?.success_rate || 0}%`}
              change={5.2}
              icon={CheckCircle}
              color="green"
            />
            <MetricCard
              title="Cost Savings"
              value={`$${costAnalysis?.total_savings?.toLocaleString() || 0}`}
              change={12.8}
              icon={DollarSign}
              color="emerald"
            />
            <MetricCard
              title="Avg Compliance"
              value={`${performanceMetrics?.average_compliance_score?.toFixed(1) || 0}%`}
              change={3.1}
              icon={Shield}
              color="purple"
            />
          </div>

          {/* Charts Row */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Monthly Contracts Trend */}
            <Card>
              <CardHeader>
                <CardTitle>Contract Generation Trends</CardTitle>
                <CardDescription>Monthly contract creation over time</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={dashboardData?.trends?.monthly_contracts || []}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="contracts" stroke="#3B82F6" strokeWidth={3} />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Contract Type Distribution */}
            <Card>
              <CardHeader>
                <CardTitle>Contract Type Distribution</CardTitle>
                <CardDescription>Breakdown by contract type</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={Object.entries(dashboardData?.contract_distribution?.by_type || {}).map(([type, count]) => ({
                        name: type.replace('_', ' ').toUpperCase(),
                        value: count
                      }))}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {Object.entries(dashboardData?.contract_distribution?.by_type || {}).map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>

          {/* Risk Distribution */}
          <Card>
            <CardHeader>
              <CardTitle>Risk Assessment Distribution</CardTitle>
              <CardDescription>Risk levels across all contracts</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={Object.entries(dashboardData?.contract_distribution?.by_risk || {}).map(([risk, count]) => ({
                  risk,
                  count,
                  fill: RISK_COLORS[risk] || '#6B7280'
                }))}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="risk" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="count" fill="#8884d8" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Performance Tab */}
        <TabsContent value="performance" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <MetricCard
              title="Success Rate"
              value={`${performanceMetrics?.success_rate || 0}%`}
              icon={Target}
              color="green"
            />
            <MetricCard
              title="Dispute Frequency"
              value={`${performanceMetrics?.dispute_frequency || 0} per 100`}
              icon={AlertTriangle}
              color="red"
            />
            <MetricCard
              title="Renewal Rate"
              value={`${performanceMetrics?.renewal_rate || 0}%`}
              icon={Activity}
              color="blue"
            />
            <MetricCard
              title="Client Satisfaction"
              value={`${performanceMetrics?.client_satisfaction || 0}/5`}
              icon={Users}
              color="purple"
            />
            <MetricCard
              title="Avg Completion Time"
              value={`${performanceMetrics?.time_to_completion_avg || 0} days`}
              icon={Clock}
              color="orange"
            />
            <MetricCard
              title="Efficiency Improvement"
              value={`${performanceMetrics?.efficiency_improvement || 0}%`}
              icon={TrendingUp}
              color="emerald"
            />
          </div>

          {/* Performance Details */}
          <Card>
            <CardHeader>
              <CardTitle>Performance Breakdown</CardTitle>
              <CardDescription>Detailed performance metrics analysis</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <div className="flex justify-between mb-2">
                    <span>Contract Success Rate</span>
                    <span>{performanceMetrics?.success_rate || 0}%</span>
                  </div>
                  <Progress value={performanceMetrics?.success_rate || 0} />
                </div>
                <div>
                  <div className="flex justify-between mb-2">
                    <span>Compliance Score</span>
                    <span>{performanceMetrics?.average_compliance_score || 0}%</span>
                  </div>
                  <Progress value={performanceMetrics?.average_compliance_score || 0} />
                </div>
                <div>
                  <div className="flex justify-between mb-2">
                    <span>Renewal Rate</span>
                    <span>{performanceMetrics?.renewal_rate || 0}%</span>
                  </div>
                  <Progress value={performanceMetrics?.renewal_rate || 0} />
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Cost Analysis Tab */}
        <TabsContent value="costs" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <MetricCard
              title="Total Savings"
              value={`$${costAnalysis?.total_savings?.toLocaleString() || 0}`}
              icon={DollarSign}
              color="green"
            />
            <MetricCard
              title="Time Saved"
              value={`${costAnalysis?.total_time_saved_hours || 0} hrs`}
              icon={Clock}
              color="blue"
            />
            <MetricCard
              title="ROI"
              value={`${costAnalysis?.roi || 0}x`}
              icon={TrendingUp}
              color="purple"
            />
            <MetricCard
              title="Savings %"
              value={`${costAnalysis?.savings_percentage || 0}%`}
              icon={BarChart3}
              color="emerald"
            />
          </div>

          {/* Cost Breakdown */}
          <Card>
            <CardHeader>
              <CardTitle>Cost Savings Breakdown</CardTitle>
              <CardDescription>Savings by process type</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={400}>
                <BarChart data={Object.entries(costAnalysis?.process_breakdown || {}).map(([process, data]) => ({
                  process: process.charAt(0).toUpperCase() + process.slice(1),
                  savings: data.savings,
                  contracts: data.contracts,
                  time_saved: data.time_saved
                }))}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="process" />
                  <YAxis />
                  <Tooltip formatter={(value, name) => [
                    name === 'savings' ? `$${value.toLocaleString()}` : value,
                    name === 'savings' ? 'Cost Savings' : name === 'contracts' ? 'Contracts' : 'Time Saved (hrs)'
                  ]} />
                  <Legend />
                  <Bar dataKey="savings" fill="#10B981" name="Cost Savings ($)" />
                  <Bar dataKey="time_saved" fill="#3B82F6" name="Time Saved (hrs)" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Negotiations Tab */}
        <TabsContent value="negotiations" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <MetricCard
              title="Total Negotiations"
              value={negotiationInsights?.total_negotiations || 0}
              icon={Users}
              color="blue"
            />
            <MetricCard
              title="Success Rate"
              value={`${negotiationInsights?.success_rate || 0}%`}
              icon={CheckCircle}
              color="green"
            />
            <MetricCard
              title="Avg Rounds"
              value={negotiationInsights?.average_rounds || 0}
              icon={Activity}
              color="orange"
            />
            <MetricCard
              title="Avg Resolution Time"
              value={`${negotiationInsights?.time_to_resolution_avg || 0} hrs`}
              icon={Clock}
              color="purple"
            />
          </div>

          {/* Negotiation Strategies */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Most Effective Strategies</CardTitle>
                <CardDescription>Success rates by negotiation strategy</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {negotiationInsights?.most_effective_strategies?.map((strategy, index) => (
                    <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                      <div>
                        <h4 className="font-medium capitalize">{strategy.strategy}</h4>
                        <p className="text-sm text-gray-500">{strategy.usage_count} uses</p>
                      </div>
                      <Badge variant={strategy.success_rate > 80 ? "default" : strategy.success_rate > 70 ? "secondary" : "outline"}>
                        {strategy.success_rate}%
                      </Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Common Negotiation Points</CardTitle>
                <CardDescription>Most frequently negotiated terms</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {negotiationInsights?.common_negotiation_points?.map((point, index) => (
                    <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                      <div>
                        <h4 className="font-medium">{point.point}</h4>
                        <p className="text-sm text-gray-500">Frequency: {point.frequency}</p>
                      </div>
                      <Badge variant={point.success_rate > 75 ? "default" : "secondary"}>
                        {point.success_rate}%
                      </Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Seasonal Trends */}
          <Card>
            <CardHeader>
              <CardTitle>Negotiation Trends</CardTitle>
              <CardDescription>Success rates over time</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={negotiationInsights?.seasonal_trends || []}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="negotiations" stroke="#3B82F6" name="Negotiations" />
                  <Line type="monotone" dataKey="success_rate" stroke="#10B981" name="Success Rate %" />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Market Intelligence Tab */}
        <TabsContent value="market" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Industry Benchmarks</CardTitle>
              <CardDescription>How you compare to industry standards</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-medium mb-2">Your Performance</h4>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span>Average Risk Score</span>
                      <span>{marketIntelligence?.industry_benchmarks?.average_risk_score || 'N/A'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Contracts Analyzed</span>
                      <span>{marketIntelligence?.industry_benchmarks?.total_contracts_analyzed || 0}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Success Rate</span>
                      <span>{marketIntelligence?.industry_benchmarks?.success_rate_benchmark || 'N/A'}%</span>
                    </div>
                  </div>
                </div>
                <div>
                  <h4 className="font-medium mb-2">Competitive Advantage</h4>
                  <div className="space-y-2">
                    {marketIntelligence?.competitive_analysis?.our_platform_advantage && Object.entries(marketIntelligence.competitive_analysis.our_platform_advantage).map(([key, value]) => (
                      <div key={key} className="flex justify-between">
                        <span className="capitalize">{key.replace('_', ' ')}</span>
                        <Badge variant="default">{value}</Badge>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Market Trends</CardTitle>
              <CardDescription>Current industry trends and insights</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {marketIntelligence?.market_trends?.map((trend, index) => (
                  <div key={index} className="flex items-start space-x-3 p-3 border rounded-lg">
                    <TrendingUp className="h-5 w-5 text-blue-600 mt-0.5" />
                    <span className="text-sm">{trend}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Strategic Recommendations</CardTitle>
              <CardDescription>AI-powered suggestions for improvement</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {marketIntelligence?.recommendations?.map((recommendation, index) => (
                  <div key={index} className="flex items-start space-x-3 p-3 border rounded-lg bg-blue-50">
                    <CheckCircle className="h-5 w-5 text-blue-600 mt-0.5" />
                    <span className="text-sm">{recommendation}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* AI Generated Insights */}
          {marketIntelligence?.ai_generated_insights && (
            <Card>
              <CardHeader>
                <CardTitle>AI-Powered Market Analysis</CardTitle>
                <CardDescription>Deep insights generated by AI</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <pre className="whitespace-pre-wrap text-sm">{marketIntelligence.ai_generated_insights}</pre>
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default AnalyticsDashboard;