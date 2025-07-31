import React, { useState } from 'react';
import { X, Upload, Plus, Trash2, ExternalLink, CheckCircle, AlertCircle } from 'lucide-react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Textarea } from '../ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { useAuth } from '../../contexts/AuthContext';
import { verificationService } from '../../services/verificationService';

const VerificationApplicationModal = ({ isOpen, onClose, onSuccess }) => {
  const { user } = useAuth();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [uploadProgress, setUploadProgress] = useState({});
  
  // Form data
  const [formData, setFormData] = useState({
    fullName: '',
    contactEmail: user?.email || '',
    country: '',
    addressLine1: '',
    addressLine2: '',
    city: '',
    postcode: '',
    nationalIdType: 'national_id'
  });

  // File states
  const [nationalIdFile, setNationalIdFile] = useState(null);
  const [additionalFiles, setAdditionalFiles] = useState([]);
  const [links, setLinks] = useState([{ url: '', description: '' }]);

  // Validation errors
  const [errors, setErrors] = useState({});

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: null }));
    }
  };

  const handleNationalIdFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      // Validate file size (10MB max)
      if (file.size > 10 * 1024 * 1024) {
        setErrors(prev => ({ ...prev, nationalId: 'File size must be less than 10MB' }));
        return;
      }
      
      // Validate file type
      const allowedTypes = ['image/jpeg', 'image/png', 'image/jpg', 'application/pdf'];
      if (!allowedTypes.includes(file.type)) {
        setErrors(prev => ({ ...prev, nationalId: 'Only JPEG, PNG, and PDF files are allowed' }));
        return;
      }

      setNationalIdFile(file);
      setErrors(prev => ({ ...prev, nationalId: null }));
    }
  };

  const handleAdditionalFileChange = (e) => {
    const files = Array.from(e.target.files);
    const currentCount = additionalFiles.length;
    
    if (currentCount + files.length > 10) {
      setErrors(prev => ({ ...prev, additionalFiles: 'Maximum 10 additional files allowed' }));
      return;
    }

    const validFiles = [];
    for (const file of files) {
      if (file.size > 10 * 1024 * 1024) {
        setErrors(prev => ({ ...prev, additionalFiles: 'Each file must be less than 10MB' }));
        continue;
      }
      
      const allowedTypes = ['image/jpeg', 'image/png', 'image/jpg', 'application/pdf', 'text/plain', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
      if (!allowedTypes.includes(file.type)) {
        setErrors(prev => ({ ...prev, additionalFiles: 'Only images, PDFs, text files, and Word documents are allowed' }));
        continue;
      }
      
      validFiles.push(file);
    }

    setAdditionalFiles(prev => [...prev, ...validFiles]);
    setErrors(prev => ({ ...prev, additionalFiles: null }));
  };

  const removeAdditionalFile = (index) => {
    setAdditionalFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleLinkChange = (index, field, value) => {
    setLinks(prev => prev.map((link, i) => 
      i === index ? { ...link, [field]: value } : link
    ));
  };

  const addLink = () => {
    setLinks(prev => [...prev, { url: '', description: '' }]);
  };

  const removeLink = (index) => {
    if (links.length > 1) {
      setLinks(prev => prev.filter((_, i) => i !== index));
    }
  };

  const validateForm = () => {
    const newErrors = {};

    if (!formData.fullName.trim()) {
      newErrors.fullName = 'Full name is required';
    }

    if (!formData.contactEmail.trim()) {
      newErrors.contactEmail = 'Contact email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.contactEmail)) {
      newErrors.contactEmail = 'Please enter a valid email address';
    }

    if (!formData.country.trim()) {
      newErrors.country = 'Country is required';
    }

    if (!formData.address.trim()) {
      newErrors.address = 'Address is required';
    }

    if (!nationalIdFile) {
      newErrors.nationalId = 'National ID/Passport/Driving License is required';
    }

    if (additionalFiles.length === 0) {
      newErrors.additionalFiles = 'At least one additional document is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);

    try {
      // Upload national ID document
      setUploadProgress({ nationalId: 'Uploading national ID...' });
      const nationalIdUpload = await verificationService.uploadVerificationFile(
        nationalIdFile, 
        user.id, 
        'national_id'
      );

      // Upload additional documents
      const additionalDocuments = [];
      for (let i = 0; i < additionalFiles.length; i++) {
        const file = additionalFiles[i];
        setUploadProgress({ [`additional_${i}`]: `Uploading ${file.name}...` });
        
        const upload = await verificationService.uploadVerificationFile(
          file, 
          user.id, 
          `additional_${i}`
        );
        
        additionalDocuments.push({
          url: upload.url,
          path: upload.path,
          fileName: upload.fileName,
          originalName: file.name
        });
      }

      // Filter out empty links
      const validLinks = links.filter(link => link.url.trim());

      // Prepare application data
      const applicationData = {
        user_id: user.id,
        full_name: formData.fullName.trim(),
        contact_email: formData.contactEmail.trim(),
        country_residence: formData.country.trim(),
        address: formData.address.trim(),
        national_id_type: formData.nationalIdType,
        national_id_file_url: nationalIdUpload.url,
        additional_documents: additionalDocuments,
        links: validLinks
      };

      setUploadProgress({ submit: 'Submitting application...' });

      // Submit application
      await verificationService.submitVerificationApplication(applicationData);

      // Success
      onSuccess && onSuccess();
      onClose();

      // Show success message
      alert('✅ Verification application submitted successfully! You will receive a notification once your application is reviewed.');

    } catch (error) {
      console.error('Error submitting verification application:', error);
      alert('❌ Failed to submit verification application. Please try again.');
    } finally {
      setIsSubmitting(false);
      setUploadProgress({});
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-4 flex items-center justify-between">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            Seller Verification Application
          </h2>
          <Button
            variant="ghost"
            size="sm"
            onClick={onClose}
            disabled={isSubmitting}
          >
            <X size={20} />
          </Button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Personal Information */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <CheckCircle className="mr-2" size={20} />
                Personal Information
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="fullName">Full Name *</Label>
                <Input
                  id="fullName"
                  value={formData.fullName}
                  onChange={(e) => handleInputChange('fullName', e.target.value)}
                  placeholder="Enter your full legal name"
                  disabled={isSubmitting}
                />
                {errors.fullName && (
                  <p className="text-red-500 text-sm mt-1">{errors.fullName}</p>
                )}
              </div>

              <div>
                <Label htmlFor="contactEmail">Contact Email *</Label>
                <Input
                  id="contactEmail"
                  type="email"
                  value={formData.contactEmail}
                  onChange={(e) => handleInputChange('contactEmail', e.target.value)}
                  placeholder="Your primary email address"
                  disabled={isSubmitting}
                />
                {errors.contactEmail && (
                  <p className="text-red-500 text-sm mt-1">{errors.contactEmail}</p>
                )}
              </div>

              <div>
                <Label htmlFor="country">Country of Residence *</Label>
                <Input
                  id="country"
                  value={formData.country}
                  onChange={(e) => handleInputChange('country', e.target.value)}
                  placeholder="Enter your country of residence"
                  disabled={isSubmitting}
                />
                {errors.country && (
                  <p className="text-red-500 text-sm mt-1">{errors.country}</p>
                )}
              </div>

              <div>
                <Label htmlFor="address">Full Address *</Label>
                <Textarea
                  id="address"
                  value={formData.address}
                  onChange={(e) => handleInputChange('address', e.target.value)}
                  placeholder="Enter your complete residential address"
                  rows={3}
                  disabled={isSubmitting}
                />
                {errors.address && (
                  <p className="text-red-500 text-sm mt-1">{errors.address}</p>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Identity Verification */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <AlertCircle className="mr-2" size={20} />
                Identity Verification
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="nationalIdType">ID Document Type *</Label>
                <select
                  id="nationalIdType"
                  value={formData.nationalIdType}
                  onChange={(e) => handleInputChange('nationalIdType', e.target.value)}
                  className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  disabled={isSubmitting}
                >
                  <option value="national_id">National ID</option>
                  <option value="driving_license">Driving License</option>
                  <option value="passport">Passport</option>
                </select>
              </div>

              <div>
                <Label htmlFor="nationalIdFile">Upload ID Document *</Label>
                <div 
                  className="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-6 text-center cursor-pointer hover:border-[#0097B2] transition-colors"
                  onDragOver={(e) => e.preventDefault()}
                  onDrop={(e) => {
                    e.preventDefault();
                    const files = e.dataTransfer.files;
                    if (files.length > 0) {
                      handleNationalIdFileChange({ target: { files } });
                    }
                  }}
                >
                  <input
                    type="file"
                    id="nationalIdFile"
                    onChange={handleNationalIdFileChange}
                    accept="image/*,.pdf"
                    className="hidden"
                    disabled={isSubmitting}
                  />
                  <label htmlFor="nationalIdFile" className="cursor-pointer">
                    <Upload className="mx-auto mb-2" size={32} />
                    <p className="text-gray-600 dark:text-gray-400">
                      {nationalIdFile ? nationalIdFile.name : 'Click to upload or drag and drop'}
                    </p>
                    <p className="text-sm text-gray-500 mt-1">
                      JPEG, PNG, or PDF (max 10MB)
                    </p>
                  </label>
                </div>
                {errors.nationalId && (
                  <p className="text-red-500 text-sm mt-1">{errors.nationalId}</p>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Additional Documents */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span className="flex items-center">
                  <Upload className="mr-2" size={20} />
                  Additional Documents * (up to 10 files)
                </span>
                <Badge variant="outline">
                  {additionalFiles.length}/10
                </Badge>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <input
                  type="file"
                  id="additionalFiles"
                  onChange={handleAdditionalFileChange}
                  accept="image/*,.pdf,.txt,.doc,.docx"
                  multiple
                  className="hidden"
                  disabled={isSubmitting}
                />
                <label
                  htmlFor="additionalFiles"
                  className="block border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-6 text-center cursor-pointer hover:border-[#0097B2] transition-colors"
                >
                  <Plus className="mx-auto mb-2" size={32} />
                  <p className="text-gray-600 dark:text-gray-400">
                    Add certificates, diplomas, trading performance evidence
                  </p>
                  <p className="text-sm text-gray-500 mt-1">
                    Images, PDFs, Word docs (max 10MB each)
                  </p>
                </label>
              </div>

              {additionalFiles.length > 0 && (
                <div className="space-y-2">
                  <h4 className="font-medium">Uploaded Files:</h4>
                  {additionalFiles.map((file, index) => (
                    <div
                      key={index}
                      className="flex items-center justify-between bg-gray-50 dark:bg-gray-700 p-3 rounded-lg"
                    >
                      <span className="text-sm truncate">{file.name}</span>
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        onClick={() => removeAdditionalFile(index)}
                        disabled={isSubmitting}
                      >
                        <Trash2 size={16} />
                      </Button>
                    </div>
                  ))}
                </div>
              )}

              {errors.additionalFiles && (
                <p className="text-red-500 text-sm mt-1">{errors.additionalFiles}</p>
              )}
            </CardContent>
          </Card>

          {/* Links */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <ExternalLink className="mr-2" size={20} />
                Portfolio/Performance Links (Optional)
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {links.map((link, index) => (
                <div key={index} className="flex gap-2">
                  <div className="flex-1">
                    <Input
                      value={link.url}
                      onChange={(e) => handleLinkChange(index, 'url', e.target.value)}
                      placeholder="https://example.com/your-portfolio"
                      disabled={isSubmitting}
                    />
                  </div>
                  <div className="flex-1">
                    <Input
                      value={link.description}
                      onChange={(e) => handleLinkChange(index, 'description', e.target.value)}
                      placeholder="Description (e.g., Trading account, Portfolio)"
                      disabled={isSubmitting}
                    />
                  </div>
                  {links.length > 1 && (
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      onClick={() => removeLink(index)}
                      disabled={isSubmitting}
                    >
                      <Trash2 size={16} />
                    </Button>
                  )}
                </div>
              ))}
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={addLink}
                disabled={isSubmitting}
              >
                <Plus size={16} className="mr-2" />
                Add Another Link
              </Button>
            </CardContent>
          </Card>

          {/* Upload Progress */}
          {Object.keys(uploadProgress).length > 0 && (
            <div className="space-y-2">
              {Object.entries(uploadProgress).map(([key, message]) => (
                <div key={key} className="flex items-center space-x-2">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-[#0097B2]"></div>
                  <span className="text-sm text-gray-600 dark:text-gray-400">{message}</span>
                </div>
              ))}
            </div>
          )}

          {/* Actions */}
          <div className="flex gap-4 pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={onClose}
              disabled={isSubmitting}
              className="flex-1"
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={isSubmitting}
              className="flex-1 bg-[#0097B2] hover:bg-[#0097B2]/90"
            >
              {isSubmitting ? 'Submitting...' : 'Submit Application'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default VerificationApplicationModal;