import React, { useState, useEffect } from 'react';
import { Alert, AlertDescription } from './ui/alert';
import { Badge } from './ui/badge';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { 
  AlertTriangle, Shield, Scale, CheckCircle, 
  XCircle, Clock, Info, ExternalLink 
} from 'lucide-react';

export function ComplianceBanner({ message, type = 'warning', isVisible = true }) {
  if (!isVisible) return null;

  const icons = {
    error: <XCircle className="h-4 w-4" />,
    warning: <AlertTriangle className="h-4 w-4" />,
    info: <Info className="h-4 w-4" />,
    success: <CheckCircle className="h-4 w-4" />
  };

  const styles = {
    error: 'bg-red-50 border-red-200 text-red-800',
    warning: 'bg-yellow-50 border-yellow-200 text-yellow-800', 
    info: 'bg-blue-50 border-blue-200 text-blue-800',
    success: 'bg-green-50 border-green-200 text-green-800'
  };

  return (
    <div className={`border-l-4 p-4 mb-4 ${styles[type]}`}>
      <div className="flex items-center">
        {icons[type]}
        <p className="ml-3 text-sm font-medium">
          {message}
        </p>
      </div>
    </div>
  );
}

export function AttorneySupervisionNotice({ 
  isVisible = true, 
  showDetails = false,
  onToggleDetails 
}) {
  if (!isVisible) return null;

  return (
    <Alert className="mb-6 border-orange-200 bg-orange-50">
      <Scale className="h-4 w-4 text-orange-600" />
      <AlertDescription className="text-orange-800">
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <strong>⚖️ ATTORNEY SUPERVISION REQUIRED</strong>
            <Badge className="bg-orange-100 text-orange-800 border-orange-300">
              COMPLIANCE MODE
            </Badge>
          </div>
          <p>
            This content requires attorney supervision and review before use. 
            All legal documents and advice must be approved by a licensed attorney.
          </p>
          {showDetails && (
            <div className="mt-3 p-3 bg-orange-100 rounded text-sm">
              <p className="font-medium mb-2">Why is attorney supervision required?</p>
              <ul className="list-disc list-inside space-y-1 text-orange-700">
                <li>To prevent Unauthorized Practice of Law (UPL) violations</li>
                <li>To ensure legal content meets professional standards</li>
                <li>To provide proper legal oversight and accountability</li>
                <li>To comply with state bar regulations and requirements</li>
              </ul>
            </div>
          )}
          {onToggleDetails && (
            <button
              onClick={onToggleDetails}
              className="text-orange-600 hover:text-orange-800 underline text-sm"
            >
              {showDetails ? 'Hide details' : 'Learn more'}
            </button>
          )}
        </div>
      </AlertDescription>
    </Alert>
  );
}

export function ComplianceStatusCard({ status, violations, confidence }) {
  const getStatusIcon = () => {
    if (status === 'compliant') return <CheckCircle className="h-5 w-5 text-green-500" />;
    if (status === 'non_compliant') return <XCircle className="h-5 w-5 text-red-500" />;
    return <Clock className="h-5 w-5 text-yellow-500" />;
  };

  const getStatusColor = () => {
    if (status === 'compliant') return 'text-green-800 bg-green-50 border-green-200';
    if (status === 'non_compliant') return 'text-red-800 bg-red-50 border-red-200';
    return 'text-yellow-800 bg-yellow-50 border-yellow-200';
  };

  const getConfidenceColor = () => {
    if (confidence >= 0.8) return 'text-green-600';
    if (confidence >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <Card className={`border-2 ${getStatusColor()}`}>
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center space-x-2 text-base">
          {getStatusIcon()}
          <span>Compliance Status</span>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium">Status:</span>
          <Badge className={getStatusColor()}>
            {status === 'compliant' ? 'COMPLIANT' : 
             status === 'non_compliant' ? 'NON-COMPLIANT' : 'PENDING REVIEW'}
          </Badge>
        </div>
        
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium">Confidence:</span>
          <span className={`text-sm font-bold ${getConfidenceColor()}`}>
            {(confidence * 100).toFixed(1)}%
          </span>
        </div>
        
        {violations && violations.length > 0 && (
          <div>
            <span className="text-sm font-medium">Violations Found:</span>
            <ul className="mt-1 text-xs space-y-1">
              {violations.slice(0, 3).map((violation, index) => (
                <li key={index} className="flex items-start space-x-1">
                  <XCircle className="h-3 w-3 text-red-500 mt-0.5 flex-shrink-0" />
                  <span>{violation.message}</span>
                </li>
              ))}
              {violations.length > 3 && (
                <li className="text-gray-500 italic">
                  +{violations.length - 3} more violations
                </li>
              )}
            </ul>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export function DocumentReviewStatus({ 
  reviewId, 
  status, 
  attorney, 
  estimatedCompletion,
  comments,
  progressPercentage = 0 
}) {
  const getStatusInfo = () => {
    switch (status) {
      case 'pending':
        return {
          icon: <Clock className="h-4 w-4 text-yellow-500" />,
          label: 'Pending Review',
          color: 'bg-yellow-50 border-yellow-200 text-yellow-800'
        };
      case 'in_review':
        return {
          icon: <Scale className="h-4 w-4 text-blue-500" />,
          label: 'Under Attorney Review',
          color: 'bg-blue-50 border-blue-200 text-blue-800'
        };
      case 'approved':
        return {
          icon: <CheckCircle className="h-4 w-4 text-green-500" />,
          label: 'Approved',
          color: 'bg-green-50 border-green-200 text-green-800'
        };
      case 'rejected':
        return {
          icon: <XCircle className="h-4 w-4 text-red-500" />,
          label: 'Rejected',
          color: 'bg-red-50 border-red-200 text-red-800'
        };
      default:
        return {
          icon: <Clock className="h-4 w-4 text-gray-500" />,
          label: 'Unknown Status',
          color: 'bg-gray-50 border-gray-200 text-gray-800'
        };
    }
  };

  const statusInfo = getStatusInfo();

  return (
    <Card className={`border-2 ${statusInfo.color}`}>
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center justify-between text-base">
          <div className="flex items-center space-x-2">
            {statusInfo.icon}
            <span>Document Review Status</span>
          </div>
          <Badge className={statusInfo.color}>
            {statusInfo.label}
          </Badge>
        </CardTitle>
        {reviewId && (
          <CardDescription className="text-xs font-mono">
            Review ID: {reviewId}
          </CardDescription>
        )}
      </CardHeader>
      <CardContent className="space-y-3">
        {/* Progress Bar */}
        <div className="space-y-1">
          <div className="flex justify-between text-xs">
            <span>Progress</span>
            <span>{progressPercentage}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-blue-500 h-2 rounded-full transition-all duration-300"
              style={{ width: `${progressPercentage}%` }}
            />
          </div>
        </div>

        {attorney && (
          <div className="text-sm">
            <span className="font-medium">Assigned Attorney:</span>
            <div className="mt-1">
              <p className="text-sm">{attorney.name}</p>
              {attorney.specializations && (
                <p className="text-xs text-gray-600">
                  Specializations: {attorney.specializations.join(', ')}
                </p>
              )}
            </div>
          </div>
        )}

        {estimatedCompletion && status !== 'approved' && status !== 'rejected' && (
          <div className="text-sm">
            <span className="font-medium">Estimated Completion:</span>
            <p className="text-sm text-gray-600">
              {new Date(estimatedCompletion).toLocaleDateString()} at{' '}
              {new Date(estimatedCompletion).toLocaleTimeString()}
            </p>
          </div>
        )}

        {comments && (
          <div className="text-sm">
            <span className="font-medium">Attorney Comments:</span>
            <p className="text-sm text-gray-700 mt-1 p-2 bg-gray-100 rounded">
              {comments}
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export function LegalDisclaimerFooter({ 
  isVisible = true,
  disclaimerText 
}) {
  const defaultDisclaimer = `
    This application provides informational content only and does not constitute legal advice. 
    All content requires attorney supervision and review. Consult with a qualified attorney 
    licensed in your jurisdiction for advice specific to your situation. Use of this service 
    does not create an attorney-client relationship.
  `;

  if (!isVisible) return null;

  return (
    <div className="bg-gray-100 border-t border-gray-200 px-6 py-4 text-xs text-gray-600">
      <div className="max-w-6xl mx-auto">
        <div className="flex items-start space-x-2">
          <Shield className="h-4 w-4 mt-0.5 flex-shrink-0" />
          <div>
            <p className="font-medium mb-1">Legal Disclaimer:</p>
            <p className="leading-relaxed">
              {disclaimerText || defaultDisclaimer}
            </p>
            <div className="flex items-center space-x-4 mt-2">
              <a href="#privacy" className="hover:text-gray-800 underline">
                Privacy Policy
              </a>
              <a href="#terms" className="hover:text-gray-800 underline">
                Terms of Service
              </a>
              <a href="#compliance" className="hover:text-gray-800 underline">
                Compliance Information
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export function ComplianceModeIndicator({ 
  complianceMode = true,
  attorneySupervisionRequired = true 
}) {
  if (!complianceMode) return null;

  return (
    <div className="fixed top-4 right-4 z-40">
      <Card className="bg-orange-50 border-orange-200 shadow-lg">
        <CardContent className="p-3">
          <div className="flex items-center space-x-2">
            <Scale className="h-4 w-4 text-orange-600" />
            <div className="text-xs">
              <p className="font-medium text-orange-800">COMPLIANCE MODE</p>
              <p className="text-orange-600">Attorney supervision active</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

export default {
  ComplianceBanner,
  AttorneySupervisionNotice,
  ComplianceStatusCard,
  DocumentReviewStatus,
  LegalDisclaimerFooter,
  ComplianceModeIndicator
};