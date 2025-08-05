import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  Card, CardContent, CardDescription, CardHeader, CardTitle 
} from '../ui/card';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Textarea } from '../ui/textarea';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Alert, AlertDescription } from '../ui/alert';
import {
  Scale, CheckCircle, XCircle, Clock, AlertTriangle, 
  FileText, User, Award, BarChart3, MessageSquare
} from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

export default function AttorneyDashboard({ onClose }) {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [attorney, setAttorney] = useState(null);
  const [loginData, setLoginData] = useState({ email: '', password: '' });
  const [reviewQueue, setReviewQueue] = useState([]);
  const [selectedReview, setSelectedReview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [reviewAction, setReviewAction] = useState({
    action: '',
    comments: '',
    approved_content: '',
    rejection_reason: ''
  });

  useEffect(() => {
    // Check for existing token
    const token = localStorage.getItem('attorney_token');
    if (token) {
      verifyToken(token);
    }
  }, []);

  useEffect(() => {
    if (isAuthenticated && attorney) {
      loadReviewQueue();
    }
  }, [isAuthenticated, attorney]);

  const verifyToken = async (token) => {
    try {
      // In a real implementation, we'd verify the JWT token
      // For now, we'll assume it's valid if it exists
      const attorneyData = JSON.parse(localStorage.getItem('attorney_data') || '{}');
      if (attorneyData.id) {
        setAttorney(attorneyData);
        setIsAuthenticated(true);
      }
    } catch (error) {
      localStorage.removeItem('attorney_token');
      localStorage.removeItem('attorney_data');
    }
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await axios.post(`${API}/attorney/login`, loginData);
      
      localStorage.setItem('attorney_token', response.data.token);
      localStorage.setItem('attorney_data', JSON.stringify(response.data.attorney));
      
      setAttorney(response.data.attorney);
      setIsAuthenticated(true);
      setLoginData({ email: '', password: '' });
    } catch (error) {
      setError(error.response?.data?.detail || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('attorney_token');
    localStorage.removeItem('attorney_data');
    setIsAuthenticated(false);
    setAttorney(null);
    setReviewQueue([]);
    setSelectedReview(null);
  };

  const loadReviewQueue = async () => {
    try {
      const response = await axios.get(`${API}/attorney/review/queue/${attorney.id}`);
      setReviewQueue(response.data.reviews || []);
    } catch (error) {
      console.error('Failed to load review queue:', error);
    }
  };

  const handleReviewAction = async () => {
    if (!selectedReview || !reviewAction.action) return;

    setLoading(true);
    try {
      const actionData = {
        review_id: selectedReview.id,
        attorney_id: attorney.id,
        action: reviewAction.action,
        comments: reviewAction.comments,
        ...(reviewAction.action === 'approve' && { approved_content: reviewAction.approved_content }),
        ...(reviewAction.action === 'reject' && { rejection_reason: reviewAction.rejection_reason })
      };

      await axios.post(`${API}/attorney/review/action`, actionData);
      
      // Refresh queue and clear selection
      await loadReviewQueue();
      setSelectedReview(null);
      setReviewAction({ action: '', comments: '', approved_content: '', rejection_reason: '' });
      
      alert(`Document ${reviewAction.action}d successfully!`);
    } catch (error) {
      alert(`Failed to ${reviewAction.action} document: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'pending': return <Clock className="h-4 w-4 text-yellow-500" />;
      case 'in_review': return <FileText className="h-4 w-4 text-blue-500" />;
      case 'approved': return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'rejected': return <XCircle className="h-4 w-4 text-red-500" />;
      case 'needs_revision': return <AlertTriangle className="h-4 w-4 text-orange-500" />;
      default: return <Clock className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusBadge = (status) => {
    const colors = {
      pending: 'bg-yellow-100 text-yellow-800',
      in_review: 'bg-blue-100 text-blue-800',
      approved: 'bg-green-100 text-green-800',
      rejected: 'bg-red-100 text-red-800',
      needs_revision: 'bg-orange-100 text-orange-800'
    };
    
    return (
      <Badge className={colors[status] || 'bg-gray-100 text-gray-800'}>
        {status.replace('_', ' ').toUpperCase()}
      </Badge>
    );
  };

  const getPriorityBadge = (priority) => {
    const colors = {
      low: 'bg-gray-100 text-gray-800',
      normal: 'bg-blue-100 text-blue-800',
      high: 'bg-orange-100 text-orange-800',
      urgent: 'bg-red-100 text-red-800'
    };
    
    return (
      <Badge className={colors[priority] || 'bg-gray-100 text-gray-800'}>
        {priority.toUpperCase()}
      </Badge>
    );
  };

  if (!isAuthenticated) {
    return (
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
        <Card className="w-full max-w-md mx-4">
          <CardHeader className="text-center">
            <div className="flex items-center justify-center mb-4">
              <Scale className="h-12 w-12 text-blue-600" />
            </div>
            <CardTitle className="text-2xl">Attorney Login</CardTitle>
            <CardDescription>
              Access the attorney supervision dashboard
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleLogin} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  value={loginData.email}
                  onChange={(e) => setLoginData({ ...loginData, email: e.target.value })}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="password">Password</Label>
                <Input
                  id="password"
                  type="password"
                  value={loginData.password}
                  onChange={(e) => setLoginData({ ...loginData, password: e.target.value })}
                  required
                />
              </div>
              
              {error && (
                <Alert>
                  <AlertTriangle className="h-4 w-4" />
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}
              
              <div className="flex gap-2">
                <Button type="submit" disabled={loading} className="flex-1">
                  {loading ? 'Logging in...' : 'Login'}
                </Button>
                <Button type="button" variant="outline" onClick={onClose}>
                  Cancel
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-2xl w-full max-w-7xl h-full max-h-[90vh] overflow-hidden">
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="bg-blue-600 text-white p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <Scale className="h-8 w-8" />
                <div>
                  <h1 className="text-2xl font-bold">Attorney Dashboard</h1>
                  <p className="text-blue-100">
                    Welcome, {attorney.first_name} {attorney.last_name}
                  </p>
                </div>
              </div>
              <div className="flex items-center space-x-4">
                <Badge variant="secondary" className="bg-blue-500 text-white">
                  {attorney.role.replace('_', ' ').toUpperCase()}
                </Badge>
                <Button variant="outline" onClick={handleLogout} className="text-blue-600 border-blue-200">
                  Logout
                </Button>
                <Button variant="outline" onClick={onClose} className="text-blue-600 border-blue-200">
                  Close
                </Button>
              </div>
            </div>
          </div>

          {/* Main Content */}
          <div className="flex-1 overflow-hidden">
            <Tabs defaultValue="queue" className="h-full flex flex-col">
              <TabsList className="w-full justify-start px-6 py-3 bg-gray-50">
                <TabsTrigger value="queue" className="flex items-center space-x-2">
                  <FileText className="h-4 w-4" />
                  <span>Review Queue ({reviewQueue.length})</span>
                </TabsTrigger>
                <TabsTrigger value="profile" className="flex items-center space-x-2">
                  <User className="h-4 w-4" />
                  <span>Profile</span>
                </TabsTrigger>
                <TabsTrigger value="analytics" className="flex items-center space-x-2">
                  <BarChart3 className="h-4 w-4" />
                  <span>Analytics</span>
                </TabsTrigger>
              </TabsList>

              <div className="flex-1 overflow-auto p-6">
                <TabsContent value="queue" className="h-full">
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 h-full">
                    {/* Review Queue List */}
                    <div className="space-y-4">
                      <h3 className="text-lg font-semibold">Pending Reviews</h3>
                      <div className="space-y-3 max-h-96 overflow-y-auto">
                        {reviewQueue.length === 0 ? (
                          <Card>
                            <CardContent className="p-6 text-center">
                              <FileText className="h-12 w-12 mx-auto text-gray-400 mb-4" />
                              <p className="text-gray-500">No pending reviews</p>
                            </CardContent>
                          </Card>
                        ) : (
                          reviewQueue.map((review) => (
                            <Card 
                              key={review.id} 
                              className={`cursor-pointer transition-colors ${
                                selectedReview?.id === review.id ? 'ring-2 ring-blue-500' : 'hover:bg-gray-50'
                              }`}
                              onClick={() => setSelectedReview(review)}
                            >
                              <CardContent className="p-4">
                                <div className="flex items-start justify-between">
                                  <div className="flex-1">
                                    <div className="flex items-center space-x-2 mb-2">
                                      {getStatusIcon(review.status)}
                                      <span className="font-medium">
                                        {review.document_type?.replace('_', ' ').toUpperCase()}
                                      </span>
                                      {getPriorityBadge(review.priority)}
                                    </div>
                                    <p className="text-sm text-gray-600 mb-2">
                                      Submitted: {new Date(review.created_at).toLocaleDateString()}
                                    </p>
                                    <p className="text-xs text-gray-500 line-clamp-2">
                                      {review.document_content?.substring(0, 100)}...
                                    </p>
                                  </div>
                                  <div className="ml-4">
                                    {getStatusBadge(review.status)}
                                  </div>
                                </div>
                              </CardContent>
                            </Card>
                          ))
                        )}
                      </div>
                    </div>

                    {/* Review Details and Actions */}
                    <div className="space-y-4">
                      {selectedReview ? (
                        <>
                          <h3 className="text-lg font-semibold">Review Details</h3>
                          <Card>
                            <CardHeader>
                              <div className="flex items-center justify-between">
                                <CardTitle className="text-lg">
                                  {selectedReview.document_type?.replace('_', ' ').toUpperCase()}
                                </CardTitle>
                                <div className="flex items-center space-x-2">
                                  {getPriorityBadge(selectedReview.priority)}
                                  {getStatusBadge(selectedReview.status)}
                                </div>
                              </div>
                              <CardDescription>
                                Submitted: {new Date(selectedReview.created_at).toLocaleDateString()}
                              </CardDescription>
                            </CardHeader>
                            <CardContent className="space-y-4">
                              <div>
                                <Label>Document Content</Label>
                                <Textarea
                                  value={selectedReview.document_content}
                                  readOnly
                                  className="min-h-32 mt-2"
                                />
                              </div>

                              {/* Review Actions */}
                              <div className="space-y-4">
                                <Label>Review Action</Label>
                                <div className="flex gap-2">
                                  <Button
                                    variant={reviewAction.action === 'approve' ? 'default' : 'outline'}
                                    onClick={() => setReviewAction({ ...reviewAction, action: 'approve' })}
                                    className="flex-1"
                                  >
                                    <CheckCircle className="h-4 w-4 mr-2" />
                                    Approve
                                  </Button>
                                  <Button
                                    variant={reviewAction.action === 'reject' ? 'default' : 'outline'}
                                    onClick={() => setReviewAction({ ...reviewAction, action: 'reject' })}
                                    className="flex-1"
                                  >
                                    <XCircle className="h-4 w-4 mr-2" />
                                    Reject
                                  </Button>
                                </div>
                              </div>

                              {reviewAction.action === 'approve' && (
                                <div>
                                  <Label>Approved Content (if modified)</Label>
                                  <Textarea
                                    value={reviewAction.approved_content}
                                    onChange={(e) => setReviewAction({ ...reviewAction, approved_content: e.target.value })}
                                    placeholder="Leave empty to approve original content"
                                    className="min-h-24 mt-2"
                                  />
                                </div>
                              )}

                              {reviewAction.action === 'reject' && (
                                <div>
                                  <Label>Rejection Reason</Label>
                                  <Textarea
                                    value={reviewAction.rejection_reason}
                                    onChange={(e) => setReviewAction({ ...reviewAction, rejection_reason: e.target.value })}
                                    placeholder="Explain why this document is being rejected"
                                    className="min-h-24 mt-2"
                                    required
                                  />
                                </div>
                              )}

                              <div>
                                <Label>Comments (Optional)</Label>
                                <Textarea
                                  value={reviewAction.comments}
                                  onChange={(e) => setReviewAction({ ...reviewAction, comments: e.target.value })}
                                  placeholder="Additional comments for the client"
                                  className="min-h-20 mt-2"
                                />
                              </div>

                              <Button
                                onClick={handleReviewAction}
                                disabled={loading || !reviewAction.action}
                                className="w-full"
                              >
                                {loading ? 'Processing...' : `${reviewAction.action?.charAt(0).toUpperCase() + reviewAction.action?.slice(1)} Document`}
                              </Button>
                            </CardContent>
                          </Card>
                        </>
                      ) : (
                        <Card>
                          <CardContent className="p-8 text-center">
                            <MessageSquare className="h-12 w-12 mx-auto text-gray-400 mb-4" />
                            <p className="text-gray-500">Select a review from the queue to get started</p>
                          </CardContent>
                        </Card>
                      )}
                    </div>
                  </div>
                </TabsContent>

                <TabsContent value="profile">
                  <Card>
                    <CardHeader>
                      <CardTitle>Attorney Profile</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <Label>Name</Label>
                          <Input value={`${attorney.first_name} ${attorney.last_name}`} readOnly />
                        </div>
                        <div>
                          <Label>Email</Label>
                          <Input value={attorney.email} readOnly />
                        </div>
                        <div>
                          <Label>Role</Label>
                          <Input value={attorney.role?.replace('_', ' ').toUpperCase()} readOnly />
                        </div>
                        <div>
                          <Label>Specializations</Label>
                          <Input value={attorney.specializations?.join(', ') || 'General Practice'} readOnly />
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </TabsContent>

                <TabsContent value="analytics">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <Card>
                      <CardHeader>
                        <CardTitle className="flex items-center space-x-2">
                          <Award className="h-5 w-5" />
                          <span>Reviews Completed</span>
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="text-3xl font-bold">
                          {attorney.reviews_completed || 0}
                        </div>
                      </CardContent>
                    </Card>
                    
                    <Card>
                      <CardHeader>
                        <CardTitle className="flex items-center space-x-2">
                          <Clock className="h-5 w-5" />
                          <span>Pending Reviews</span>
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="text-3xl font-bold">
                          {reviewQueue.length}
                        </div>
                      </CardContent>
                    </Card>
                    
                    <Card>
                      <CardHeader>
                        <CardTitle className="flex items-center space-x-2">
                          <BarChart3 className="h-5 w-5" />
                          <span>Avg Review Time</span>
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="text-3xl font-bold">
                          {attorney.average_review_time?.toFixed(1) || '0.0'}h
                        </div>
                      </CardContent>
                    </Card>
                  </div>
                </TabsContent>
              </div>
            </Tabs>
          </div>
        </div>
      </div>
    </div>
  );
}