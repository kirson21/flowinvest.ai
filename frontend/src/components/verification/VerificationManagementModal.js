import React, { useState, useEffect } from 'react';
import { X, FileText, Download, CheckCircle, XCircle, Clock, User, Mail, MapPin, ExternalLink, Eye } from 'lucide-react';
import { Button } from '../ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Textarea } from '../ui/textarea';
import { verificationService } from '../../services/verificationService';

const VerificationManagementModal = ({ isOpen, onClose }) => {
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedApplication, setSelectedApplication] = useState(null);
  const [reviewData, setReviewData] = useState({
    adminNotes: '',
    rejectionReason: ''
  });
  const [isProcessing, setIsProcessing] = useState(false);

  useEffect(() => {
    if (isOpen) {
      loadApplications();
    }
  }, [isOpen]);

  const loadApplications = async () => {
    try {
      setLoading(true);
      const data = await verificationService.getAllApplications();
      setApplications(data);
    } catch (error) {
      console.error('Error loading applications:', error);
      alert('Failed to load verification applications');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'pending': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'approved': return 'bg-green-100 text-green-800 border-green-200';
      case 'rejected': return 'bg-red-100 text-red-800 border-red-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'pending': return <Clock size={16} />;
      case 'approved': return <CheckCircle size={16} />;
      case 'rejected': return <XCircle size={16} />;
      default: return <Clock size={16} />;
    }
  };

  const handleViewApplication = (application) => {
    setSelectedApplication(application);
    setReviewData({
      adminNotes: application.admin_notes || '',
      rejectionReason: application.rejection_reason || ''
    });
  };

  const handleApproveApplication = async () => {
    if (!selectedApplication) return;

    setIsProcessing(true);
    try {
      await verificationService.approveApplication(
        selectedApplication.id,
        reviewData.adminNotes
      );
      
      alert('✅ Application approved successfully! User has been notified.');
      setSelectedApplication(null);
      await loadApplications(); // Reload applications
    } catch (error) {
      console.error('Error approving application:', error);
      alert('❌ Failed to approve application. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleRejectApplication = async () => {
    if (!selectedApplication || !reviewData.rejectionReason.trim()) {
      alert('Please provide a rejection reason');
      return;
    }

    setIsProcessing(true);
    try {
      await verificationService.rejectApplication(
        selectedApplication.id,
        reviewData.rejectionReason,
        reviewData.adminNotes
      );
      
      alert('✅ Application rejected. User has been notified.');
      setSelectedApplication(null);
      await loadApplications(); // Reload applications
    } catch (error) {
      console.error('Error rejecting application:', error);
      alert('❌ Failed to reject application. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const openFileInNewTab = async (url, filePath) => {
    try {
      // If it's a stored file path, create a fresh signed URL for secure access
      if (filePath && !url.startsWith('data:') && !url.startsWith('http')) {
        const signedUrl = await verificationService.createSignedUrlForDocument(filePath);
        window.open(signedUrl, '_blank');
      } else {
        // Use the provided URL (for base64 or already signed URLs)
        window.open(url, '_blank');
      }
    } catch (error) {
      console.error('Error opening file:', error);
      // Fallback to original URL
      window.open(url, '_blank');
    }
  };

  if (!isOpen) return null;

  // Application Details View
  if (selectedApplication) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-y-auto">
          <div className="sticky top-0 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-4 flex items-center justify-between">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
              Application Review - {selectedApplication.full_name}
            </h2>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setSelectedApplication(null)}
              disabled={isProcessing}
            >
              <X size={20} />
            </Button>
          </div>

          <div className="p-6 space-y-6">
            {/* Status & Basic Info */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span>Application Status</span>
                  <Badge className={getStatusColor(selectedApplication.status)}>
                    {getStatusIcon(selectedApplication.status)}
                    <span className="ml-1 capitalize">{selectedApplication.status}</span>
                  </Badge>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <span className="text-sm font-medium text-gray-500">Submitted:</span>
                    <p className="text-gray-900 dark:text-white">{formatDate(selectedApplication.created_at)}</p>
                  </div>
                  {selectedApplication.reviewed_at && (
                    <div>
                      <span className="text-sm font-medium text-gray-500">Reviewed:</span>
                      <p className="text-gray-900 dark:text-white">{formatDate(selectedApplication.reviewed_at)}</p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Personal Information */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <User className="mr-2" size={20} />
                  Personal Information
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <span className="text-sm font-medium text-gray-500">Full Name:</span>
                    <p className="text-gray-900 dark:text-white">{selectedApplication.full_name}</p>
                  </div>
                  <div>
                    <span className="text-sm font-medium text-gray-500">Email:</span>
                    <p className="text-gray-900 dark:text-white">{selectedApplication.contact_email}</p>
                  </div>
                </div>
                <div>
                  <span className="text-sm font-medium text-gray-500">Country:</span>
                  <p className="text-gray-900 dark:text-white">{selectedApplication.country_residence}</p>
                </div>
                <div>
                  <span className="text-sm font-medium text-gray-500">Address:</span>
                  <p className="text-gray-900 dark:text-white">{selectedApplication.address}</p>
                </div>
              </CardContent>
            </Card>

            {/* Identity Document */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <FileText className="mr-2" size={20} />
                  Identity Verification
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div>
                  <span className="text-sm font-medium text-gray-500">Document Type:</span>
                  <p className="text-gray-900 dark:text-white capitalize">
                    {selectedApplication.national_id_type.replace('_', ' ')}
                  </p>
                </div>
                <div>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => openFileInNewTab(selectedApplication.national_id_file_url, selectedApplication.national_id_file_path)}
                    className="flex items-center"
                  >
                    <Eye size={16} className="mr-2" />
                    View ID Document
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Additional Documents */}
            {selectedApplication.additional_documents && selectedApplication.additional_documents.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Download className="mr-2" size={20} />
                    Additional Documents ({selectedApplication.additional_documents.length})
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 gap-2">
                    {selectedApplication.additional_documents.map((doc, index) => (
                      <Button
                        key={index}
                        variant="outline"
                        size="sm"
                        onClick={() => openFileInNewTab(doc.url, doc.path)}
                        className="justify-start text-left"
                      >
                        <FileText size={16} className="mr-2" />
                        <span className="truncate">{doc.fileName || doc.originalName || `Document ${index + 1}`}</span>
                      </Button>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Links */}
            {selectedApplication.links && selectedApplication.links.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <ExternalLink className="mr-2" size={20} />
                    Portfolio/Performance Links
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  {selectedApplication.links.map((link, index) => (
                    <div key={index} className="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-700 rounded">
                      <div>
                        <p className="font-medium text-sm">{link.description || 'Link'}</p>
                        <p className="text-xs text-gray-600 dark:text-gray-400 truncate">{link.url}</p>
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => window.open(link.url, '_blank')}
                      >
                        <ExternalLink size={16} />
                      </Button>
                    </div>
                  ))}
                </CardContent>
              </Card>
            )}

            {/* Review Section */}
            {selectedApplication.status === 'pending' && (
              <Card>
                <CardHeader>
                  <CardTitle>Admin Review</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">Admin Notes (Optional)</label>
                    <Textarea
                      value={reviewData.adminNotes}
                      onChange={(e) => setReviewData(prev => ({ ...prev, adminNotes: e.target.value }))}
                      placeholder="Internal notes about this application..."
                      rows={3}
                      disabled={isProcessing}
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">Rejection Reason (Required for rejection)</label>
                    <Textarea
                      value={reviewData.rejectionReason}
                      onChange={(e) => setReviewData(prev => ({ ...prev, rejectionReason: e.target.value }))}
                      placeholder="Reason for rejection (will be sent to the user)..."
                      rows={3}
                      disabled={isProcessing}
                    />
                  </div>

                  <div className="flex gap-3 pt-4">
                    <Button
                      variant="outline"
                      onClick={handleRejectApplication}
                      disabled={isProcessing || !reviewData.rejectionReason.trim()}
                      className="flex-1 border-red-300 text-red-700 hover:bg-red-50"
                    >
                      {isProcessing ? 'Processing...' : 'Reject Application'}
                    </Button>
                    <Button
                      onClick={handleApproveApplication}
                      disabled={isProcessing}
                      className="flex-1 bg-green-600 hover:bg-green-700"
                    >
                      {isProcessing ? 'Processing...' : 'Approve Application'}
                    </Button>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Previous Review Info */}
            {selectedApplication.status !== 'pending' && (
              <Card>
                <CardHeader>
                  <CardTitle>Review Information</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div>
                    <span className="text-sm font-medium text-gray-500">Reviewed By:</span>
                    <p className="text-gray-900 dark:text-white">{selectedApplication.reviewed_by || 'System'}</p>
                  </div>
                  <div>
                    <span className="text-sm font-medium text-gray-500">Review Date:</span>
                    <p className="text-gray-900 dark:text-white">{formatDate(selectedApplication.reviewed_at)}</p>
                  </div>
                  {selectedApplication.admin_notes && (
                    <div>
                      <span className="text-sm font-medium text-gray-500">Admin Notes:</span>
                      <p className="text-gray-900 dark:text-white">{selectedApplication.admin_notes}</p>
                    </div>
                  )}
                  {selectedApplication.rejection_reason && (
                    <div>
                      <span className="text-sm font-medium text-gray-500">Rejection Reason:</span>
                      <p className="text-gray-900 dark:text-white">{selectedApplication.rejection_reason}</p>
                    </div>
                  )}
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
    );
  }

  // Applications List View
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-2xl w-full max-w-6xl max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-4 flex items-center justify-between">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            Seller Verification Management
          </h2>
          <Button
            variant="ghost"
            size="sm"
            onClick={onClose}
          >
            <X size={20} />
          </Button>
        </div>

        <div className="p-6">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#0097B2]"></div>
              <span className="ml-3 text-gray-600 dark:text-gray-400">Loading applications...</span>
            </div>
          ) : applications.length === 0 ? (
            <div className="text-center py-12">
              <FileText className="mx-auto mb-4 text-gray-400" size={48} />
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                No verification applications
              </h3>
              <p className="text-gray-600 dark:text-gray-400">
                When users submit seller verification applications, they will appear here.
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="grid grid-cols-4 gap-4 mb-6">
                <Card>
                  <CardContent className="p-4 text-center">
                    <div className="text-2xl font-bold text-yellow-600">
                      {applications.filter(app => app.status === 'pending').length}
                    </div>
                    <div className="text-sm text-gray-600">Pending</div>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="p-4 text-center">
                    <div className="text-2xl font-bold text-green-600">
                      {applications.filter(app => app.status === 'approved').length}
                    </div>
                    <div className="text-sm text-gray-600">Approved</div>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="p-4 text-center">
                    <div className="text-2xl font-bold text-red-600">
                      {applications.filter(app => app.status === 'rejected').length}
                    </div>
                    <div className="text-sm text-gray-600">Rejected</div>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="p-4 text-center">
                    <div className="text-2xl font-bold text-blue-600">
                      {applications.length}
                    </div>
                    <div className="text-sm text-gray-600">Total</div>
                  </CardContent>
                </Card>
              </div>

              {applications.map((application) => (
                <Card key={application.id} className="hover:shadow-md transition-shadow">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-4">
                        <div className="flex-1">
                          <h3 className="font-semibold text-gray-900 dark:text-white">
                            {application.full_name}
                          </h3>
                          <p className="text-sm text-gray-600 dark:text-gray-400">
                            {application.contact_email}
                          </p>
                          <p className="text-xs text-gray-500 mt-1">
                            {application.country_residence} • {formatDate(application.created_at)}
                          </p>
                        </div>
                        
                        <div className="text-center">
                          <Badge className={getStatusColor(application.status)}>
                            {getStatusIcon(application.status)}
                            <span className="ml-1 capitalize">{application.status}</span>
                          </Badge>
                        </div>
                        
                        <div className="text-right">
                          <div className="text-sm text-gray-600 dark:text-gray-400">
                            Documents: {1 + (application.additional_documents?.length || 0)}
                          </div>
                          {application.links && application.links.length > 0 && (
                            <div className="text-xs text-gray-500">
                              Links: {application.links.length}
                            </div>
                          )}
                        </div>
                      </div>
                      
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleViewApplication(application)}
                      >
                        <Eye size={16} className="mr-2" />
                        Review
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default VerificationManagementModal;