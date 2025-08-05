import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Alert, AlertDescription } from './ui/alert';
import { 
  Scale, Clock, CheckCircle, XCircle, AlertTriangle, 
  RefreshCw, FileText, User, MessageSquare, Calendar
} from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

export default function ReviewStatus({ reviewId, onStatusChange, autoRefresh = true }) {
  const [reviewStatus, setReviewStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [lastUpdated, setLastUpdated] = useState(null);

  useEffect(() => {
    if (reviewId) {
      fetchReviewStatus();
      
      if (autoRefresh) {
        const interval = setInterval(fetchReviewStatus, 30000); // Refresh every 30 seconds
        return () => clearInterval(interval);
      }
    }
  }, [reviewId, autoRefresh]);

  const fetchReviewStatus = async () => {
    try {
      setError('');
      const response = await axios.get(`${API}/api/attorney/review/status/${reviewId}`);
      const newStatus = response.data;
      
      // Check if status changed
      if (reviewStatus?.status !== newStatus.status) {
        onStatusChange?.(newStatus);
      }
      
      setReviewStatus(newStatus);
      setLastUpdated(new Date());
      
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to fetch review status');
      console.error('Failed to fetch review status:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusInfo = (status) => {
    const statusMap = {
      pending: {
        icon: <Clock className="h-5 w-5 text-yellow-500" />,
        label: 'Pending Review',
        description: 'Your document is in the attorney review queue',
        color: 'bg-yellow-50 border-yellow-200 text-yellow-800',
        badgeColor: 'bg-yellow-100 text-yellow-800'
      },
      in_review: {
        icon: <Scale className="h-5 w-5 text-blue-500" />,
        label: 'Under Review',
        description: 'An attorney is currently reviewing your document',
        color: 'bg-blue-50 border-blue-200 text-blue-800',
        badgeColor: 'bg-blue-100 text-blue-800'
      },
      approved: {
        icon: <CheckCircle className="h-5 w-5 text-green-500" />,
        label: 'Approved',
        description: 'Your document has been approved by an attorney',
        color: 'bg-green-50 border-green-200 text-green-800',
        badgeColor: 'bg-green-100 text-green-800'
      },
      rejected: {
        icon: <XCircle className="h-5 w-5 text-red-500" />,
        label: 'Rejected',
        description: 'Your document requires revision before approval',
        color: 'bg-red-50 border-red-200 text-red-800',
        badgeColor: 'bg-red-100 text-red-800'
      },
      needs_revision: {
        icon: <AlertTriangle className="h-5 w-5 text-orange-500" />,
        label: 'Needs Revision',
        description: 'Please review attorney feedback and make requested changes',
        color: 'bg-orange-50 border-orange-200 text-orange-800',
        badgeColor: 'bg-orange-100 text-orange-800'
      }
    };
    
    return statusMap[status] || statusMap.pending;
  };

  const formatTimeRemaining = (estimatedCompletion) => {
    if (!estimatedCompletion) return null;
    
    const now = new Date();
    const completion = new Date(estimatedCompletion);
    const diffMs = completion.getTime() - now.getTime();
    
    if (diffMs <= 0) return 'Overdue';
    
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffMinutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));
    
    if (diffHours > 24) {
      const days = Math.floor(diffHours / 24);
      return `${days} day${days > 1 ? 's' : ''} remaining`;
    } else if (diffHours > 0) {
      return `${diffHours}h ${diffMinutes}m remaining`;
    } else {
      return `${diffMinutes}m remaining`;
    }
  };

  if (loading && !reviewStatus) {
    return (
      <Card className="animate-pulse">
        <CardHeader>
          <div className="flex items-center space-x-2">
            <div className="w-5 h-5 bg-gray-300 rounded"></div>
            <div className="w-32 h-4 bg-gray-300 rounded"></div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <div className="w-full h-3 bg-gray-300 rounded"></div>
            <div className="w-3/4 h-3 bg-gray-300 rounded"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error && !reviewStatus) {
    return (
      <Alert className="border-red-200 bg-red-50">
        <XCircle className="h-4 w-4 text-red-600" />
        <AlertDescription className="text-red-800">
          <div className="flex items-center justify-between">
            <span>{error}</span>
            <Button
              onClick={fetchReviewStatus}
              variant="outline"
              size="sm"
              className="ml-2"
            >
              <RefreshCw className="h-3 w-3 mr-1" />
              Retry
            </Button>
          </div>
        </AlertDescription>
      </Alert>
    );
  }

  if (!reviewStatus) return null;

  const statusInfo = getStatusInfo(reviewStatus.status);
  const timeRemaining = formatTimeRemaining(reviewStatus.estimated_completion);

  return (
    <Card className={`border-2 ${statusInfo.color}`}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            {statusInfo.icon}
            <CardTitle className="text-lg">{statusInfo.label}</CardTitle>
          </div>
          <div className="flex items-center space-x-2">
            <Badge className={statusInfo.badgeColor}>
              {reviewStatus.status.replace('_', ' ').toUpperCase()}
            </Badge>
            <Button
              onClick={fetchReviewStatus}
              variant="ghost"
              size="sm"
              disabled={loading}
            >
              <RefreshCw className={`h-3 w-3 ${loading ? 'animate-spin' : ''}`} />
            </Button>
          </div>
        </div>
        <CardDescription>{statusInfo.description}</CardDescription>
        
        {reviewId && (
          <div className="text-xs font-mono text-gray-500">
            Review ID: {reviewId}
          </div>
        )}
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* Progress Bar */}
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="font-medium">Progress</span>
            <span>{reviewStatus.progress_percentage || 0}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className={`h-2 rounded-full transition-all duration-500 ${
                reviewStatus.status === 'approved' ? 'bg-green-500' :
                reviewStatus.status === 'rejected' ? 'bg-red-500' :
                'bg-blue-500'
              }`}
              style={{ width: `${reviewStatus.progress_percentage || 0}%` }}
            />
          </div>
        </div>

        {/* Timeline Information */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          {reviewStatus.created_at && (
            <div className="flex items-center space-x-2">
              <Calendar className="h-4 w-4 text-gray-400" />
              <div>
                <span className="font-medium">Submitted:</span>
                <p className="text-gray-600">
                  {new Date(reviewStatus.created_at).toLocaleDateString()} at{' '}
                  {new Date(reviewStatus.created_at).toLocaleTimeString()}
                </p>
              </div>
            </div>
          )}
          
          {timeRemaining && reviewStatus.status !== 'approved' && reviewStatus.status !== 'rejected' && (
            <div className="flex items-center space-x-2">
              <Clock className="h-4 w-4 text-gray-400" />
              <div>
                <span className="font-medium">Time Remaining:</span>
                <p className="text-gray-600">{timeRemaining}</p>
              </div>
            </div>
          )}
        </div>

        {/* Attorney Information */}
        {reviewStatus.attorney && (
          <div className="bg-gray-50 p-3 rounded">
            <div className="flex items-center space-x-2 mb-2">
              <User className="h-4 w-4 text-gray-600" />
              <span className="font-medium text-sm">Assigned Attorney</span>
            </div>
            <p className="text-sm font-medium">{reviewStatus.attorney.name}</p>
            {reviewStatus.attorney.specializations && (
              <p className="text-xs text-gray-600">
                Specializations: {reviewStatus.attorney.specializations.join(', ')}
              </p>
            )}
            {reviewStatus.attorney.years_experience && (
              <p className="text-xs text-gray-600">
                {reviewStatus.attorney.years_experience} years of experience
              </p>
            )}
          </div>
        )}

        {/* Attorney Comments */}
        {reviewStatus.comments && (
          <div className="bg-blue-50 p-3 rounded border border-blue-200">
            <div className="flex items-center space-x-2 mb-2">
              <MessageSquare className="h-4 w-4 text-blue-600" />
              <span className="font-medium text-sm text-blue-800">Attorney Comments</span>
            </div>
            <p className="text-sm text-blue-700 whitespace-pre-wrap">
              {reviewStatus.comments}
            </p>
          </div>
        )}

        {/* Status-specific alerts */}
        {reviewStatus.status === 'approved' && (
          <Alert className="border-green-200 bg-green-50">
            <CheckCircle className="h-4 w-4 text-green-600" />
            <AlertDescription className="text-green-800">
              <strong>Document Approved!</strong> Your document has been reviewed and approved by an attorney. 
              You can now use it with confidence.
            </AlertDescription>
          </Alert>
        )}

        {reviewStatus.status === 'rejected' && (
          <Alert className="border-red-200 bg-red-50">
            <XCircle className="h-4 w-4 text-red-600" />
            <AlertDescription className="text-red-800">
              <strong>Document Rejected.</strong> Please review the attorney's feedback and make the 
              necessary revisions before resubmitting.
            </AlertDescription>
          </Alert>
        )}

        {reviewStatus.status === 'needs_revision' && (
          <Alert className="border-orange-200 bg-orange-50">
            <AlertTriangle className="h-4 w-4 text-orange-600" />
            <AlertDescription className="text-orange-800">
              <strong>Revisions Required.</strong> The attorney has provided feedback for improvements. 
              Please make the requested changes and resubmit for approval.
            </AlertDescription>
          </Alert>
        )}

        {/* Last updated indicator */}
        {lastUpdated && (
          <div className="text-xs text-gray-500 text-center pt-2 border-t">
            Last updated: {lastUpdated.toLocaleTimeString()}
            {autoRefresh && ' (auto-refreshing every 30s)'}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export function ReviewStatusBadge({ status, className = '' }) {
  const statusInfo = {
    pending: { label: 'Pending', color: 'bg-yellow-100 text-yellow-800' },
    in_review: { label: 'In Review', color: 'bg-blue-100 text-blue-800' },
    approved: { label: 'Approved', color: 'bg-green-100 text-green-800' },
    rejected: { label: 'Rejected', color: 'bg-red-100 text-red-800' },
    needs_revision: { label: 'Needs Revision', color: 'bg-orange-100 text-orange-800' }
  };

  const info = statusInfo[status] || statusInfo.pending;

  return (
    <Badge className={`${info.color} ${className}`}>
      {info.label}
    </Badge>
  );
}