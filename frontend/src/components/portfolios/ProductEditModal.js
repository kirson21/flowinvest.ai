import React, { useState, useRef, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Textarea } from '../ui/textarea';
import { 
  X,
  Upload,
  Image,
  Video,
  FileText,
  DollarSign,
  Eye,
  Save,
  Trash2,
  AlertCircle,
  Check
} from 'lucide-react';
import FileUploadService from '../../services/fileUpload';

const ProductEditModal = ({ product, isOpen, onClose, onSave, onDelete }) => {
  const { user } = useAuth();
  const [step, setStep] = useState('edit'); // 'edit', 'preview', 'updated'
  const [isLoading, setIsLoading] = useState(false);
  const [uploadingFiles, setUploadingFiles] = useState(false);
  
  const [productData, setProductData] = useState({
    title: '',
    description: '',
    content: '',
    price: '',
    category: 'portfolio',
    tags: [],
    attachments: [],
    riskLevel: 'Medium',
    expectedReturn: '',
    assetAllocation: '',
    minimumInvestment: ''
  });

  const [errors, setErrors] = useState({});
  const fileInputRef = useRef(null);
  const imageInputRef = useRef(null);
  const videoInputRef = useRef(null);

  // Initialize form data when product changes
  useEffect(() => {
    if (product && isOpen) {
      setProductData({
        title: product.title || '',
        description: product.description || '',
        content: product.content || '',
        price: product.price?.toString() || '',
        category: product.category || 'portfolio',
        tags: product.tags || [],
        attachments: product.attachments || [],
        riskLevel: product.riskLevel || 'Medium',
        expectedReturn: product.expectedReturn?.replace('%', '') || '',
        assetAllocation: product.assetAllocation || '',
        minimumInvestment: product.minimumInvestment?.toString() || ''
      });
      setStep('edit');
      setErrors({});
    }
  }, [product, isOpen]);

  if (!isOpen || !product) return null;

  const handleInputChange = (field, value) => {
    setProductData(prev => ({
      ...prev,
      [field]: value
    }));
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({
        ...prev,
        [field]: null
      }));
    }
  };

  const validateForm = () => {
    const newErrors = {};
    
    if (!productData.title.trim()) {
      newErrors.title = 'Title is required';
    }
    if (!productData.description.trim()) {
      newErrors.description = 'Description is required';
    } else if (productData.description.length > 140) {
      newErrors.description = 'Description must be 140 characters or less';
    }
    if (!productData.content.trim()) {
      newErrors.content = 'Content is required';
    }
    if (!productData.price || parseFloat(productData.price) <= 0) {
      newErrors.price = 'Valid price is required';
    }
    if (productData.minimumInvestment && parseFloat(productData.minimumInvestment) <= 0) {
      newErrors.minimumInvestment = 'Minimum investment must be a positive number';
    }
    if (productData.expectedReturn && (parseFloat(productData.expectedReturn) < 0 || parseFloat(productData.expectedReturn) > 1000)) {
      newErrors.expectedReturn = 'Expected return must be between 0% and 1000%';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleFileUpload = async (event, type) => {
    const files = Array.from(event.target.files);
    if (files.length === 0) return;

    setUploadingFiles(true);
    
    try {
      const uploadPromises = files.map(async (file) => {
        const uploadResult = await FileUploadService.uploadProductAttachment(file);
        
        return {
          id: Date.now() + Math.random(),
          name: file.name,
          size: file.size,
          type: FileUploadService.getFileType(file.name),
          url: uploadResult.publicUrl,
          path: uploadResult.path,
          bucket: uploadResult.bucket
        };
      });

      const uploadedFiles = await Promise.all(uploadPromises);
      
      setProductData(prev => ({
        ...prev,
        attachments: [...prev.attachments, ...uploadedFiles]
      }));
      
    } catch (error) {
      console.error('File upload error:', error);
      alert('Error uploading files. Please try again.');
    } finally {
      setUploadingFiles(false);
    }
  };

  const removeAttachment = async (attachment) => {
    try {
      if (attachment.path && attachment.bucket) {
        await FileUploadService.deleteFile(attachment.bucket, attachment.path);
      }
      
      setProductData(prev => ({
        ...prev,
        attachments: prev.attachments.filter(att => att.id !== attachment.id)
      }));
      
    } catch (error) {
      console.error('Error removing file:', error);
      setProductData(prev => ({
        ...prev,
        attachments: prev.attachments.filter(att => att.id !== attachment.id)
      }));
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const renderAttachmentIcon = (type) => {
    switch (type) {
      case 'image':
        return <Image size={16} className="text-blue-500" />;
      case 'video':
        return <Video size={16} className="text-purple-500" />;
      case 'document':
        return <FileText size={16} className="text-green-500" />;
      default:
        return <FileText size={16} className="text-gray-500" />;
    }
  };

  const handlePreview = () => {
    if (validateForm()) {
      setStep('preview');
    }
  };

  const handleSave = async () => {
    setIsLoading(true);
    
    try {
      // Load updated seller data from localStorage
      const savedSellerData = JSON.parse(localStorage.getItem(`seller_data_${user?.id}`) || '{}');
      const isSellerMode = localStorage.getItem(`seller_mode_${user?.id}`) === 'true';
      
      // Update seller info with current data from settings
      const updatedSellerInfo = {
        ...product.seller,
        name: user?.user_metadata?.name || user?.user_metadata?.display_name || user?.email || product.seller.name,
        avatar: user?.user_metadata?.avatar_url || product.seller.avatar || `https://ui-avatars.com/api/?name=${encodeURIComponent(user?.user_metadata?.name || user?.email || 'User')}&size=150&background=0097B2&color=ffffff`,
        bio: isSellerMode && savedSellerData.bio ? savedSellerData.bio : product.seller.bio,
        socialLinks: isSellerMode ? savedSellerData.socialLinks : (product.seller.socialLinks || {}),
        specialties: isSellerMode ? savedSellerData.specialties || [] : (product.seller.specialties || []),
        experience: isSellerMode ? savedSellerData.experience : product.seller.experience
      };

      const updatedProduct = {
        ...product,
        ...productData,
        riskLevel: productData.riskLevel,
        expectedReturn: productData.expectedReturn ? `${productData.expectedReturn}%` : product.expectedReturn,
        minimumInvestment: parseFloat(productData.minimumInvestment) || parseFloat(productData.price),
        assetAllocation: productData.assetAllocation || product.assetAllocation,
        seller: updatedSellerInfo, // Update seller info
        updatedAt: new Date().toISOString()
      };

      if (onSave) {
        await onSave(updatedProduct);
      }

      setStep('updated');
      
      // Auto-close after success
      setTimeout(() => {
        onClose();
        setStep('edit');
      }, 2000);

    } catch (error) {
      console.error('Error updating product:', error);
      alert('Error updating product. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async () => {
    if (window.confirm('Are you sure you want to delete this product? This action cannot be undone.')) {
      if (onDelete) {
        await onDelete(product.id);
      }
      onClose();
    }
  };

  if (step === 'updated') {
    return (
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
        <Card className="w-full max-w-md">
          <CardContent className="pt-6 text-center">
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Check size={32} className="text-green-600" />
            </div>
            <h3 className="text-xl font-semibold mb-2">Product Updated!</h3>
            <p className="text-gray-600 mb-4">
              Your changes to "{productData.title}" have been saved successfully.
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (step === 'preview') {
    return (
      <div className="fixed inset-0 bg-black/50 flex items-start sm:items-center justify-center p-2 sm:p-4 z-50 overflow-y-auto">
        <Card className="w-full max-w-4xl my-2 sm:my-0 max-h-none sm:max-h-[90vh] overflow-visible sm:overflow-y-auto">
          <CardHeader className="border-b">
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-xl text-[#474545] dark:text-white">Preview Changes</CardTitle>
                <p className="text-sm text-gray-500 mt-1">Review your changes before saving</p>
              </div>
              <Button variant="ghost" onClick={onClose}>
                <X size={20} />
              </Button>
            </div>
          </CardHeader>

          <CardContent className="p-6 space-y-6">
            {/* Product Preview - Same structure as creation modal preview */}
            <Card className="border-[#0097B2]/20">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <CardTitle className="text-lg text-[#474545] dark:text-white mb-2">
                      {productData.title}
                    </CardTitle>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                      {productData.description}
                    </p>
                    <div className="flex items-center space-x-4 text-sm text-gray-500">
                      <span className="flex items-center">
                        <DollarSign size={14} className="mr-1" />
                        ${productData.price}
                      </span>
                      <Badge variant="outline">{productData.category}</Badge>
                      {productData.riskLevel && (
                        <Badge variant="outline" className="border-orange-200 text-orange-700">
                          {productData.riskLevel} Risk
                        </Badge>
                      )}
                    </div>
                  </div>
                </div>
              </CardHeader>
              
              <CardContent>
                <div className="prose prose-sm max-w-none">
                  <div className="whitespace-pre-wrap text-gray-700 dark:text-gray-300">
                    {productData.content}
                  </div>
                </div>

                {/* Metadata Display */}
                {(productData.expectedReturn || productData.assetAllocation || productData.minimumInvestment) && (
                  <div className="mt-6 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                    <h4 className="font-medium mb-3">Product Details</h4>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm">
                      {productData.expectedReturn && (
                        <div>
                          <span className="text-gray-500">Expected Return:</span>
                          <span className="ml-2 font-medium">{productData.expectedReturn}%</span>
                        </div>
                      )}
                      {productData.minimumInvestment && (
                        <div>
                          <span className="text-gray-500">Min. Investment:</span>
                          <span className="ml-2 font-medium">${productData.minimumInvestment}</span>
                        </div>
                      )}
                      {productData.assetAllocation && (
                        <div className="sm:col-span-2">
                          <span className="text-gray-500">Asset Allocation:</span>
                          <span className="ml-2 font-medium">{productData.assetAllocation}</span>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {productData.attachments.length > 0 && (
                  <div className="mt-6">
                    <h4 className="font-medium mb-3">Attachments</h4>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                      {productData.attachments.map((attachment) => (
                        <div key={attachment.id} className="flex items-center space-x-3 p-3 border rounded-lg">
                          {renderAttachmentIcon(attachment.type)}
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium truncate">{attachment.name}</p>
                            <p className="text-xs text-gray-500">{formatFileSize(attachment.size)}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row gap-3 pt-4 border-t">
              <Button
                variant="outline"
                onClick={() => setStep('edit')}
                className="w-full sm:flex-1 border-[#0097B2]/20"
              >
                ← Back to Edit
              </Button>
              <Button
                onClick={handleSave}
                disabled={isLoading}
                className="w-full sm:flex-1 bg-[#0097B2] hover:bg-[#0097B2]/90"
              >
                {isLoading ? 'Saving...' : 'Save Changes'}
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-start sm:items-center justify-center p-2 sm:p-4 z-50 overflow-y-auto">
      <Card className="w-full max-w-4xl my-2 sm:my-0 max-h-none sm:max-h-[90vh] overflow-visible sm:overflow-y-auto">
        <CardHeader className="border-b">
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-xl text-[#474545] dark:text-white">Edit Product</CardTitle>
              <p className="text-sm text-gray-500 mt-1">Update your product information</p>
            </div>
            <Button variant="ghost" onClick={onClose}>
              <X size={20} />
            </Button>
          </div>
        </CardHeader>

        <CardContent className="p-6 space-y-6">
          {/* Same form fields as ProductCreationModal but with "Edit" context */}
          {/* Title */}
          <div>
            <label className="block text-sm font-medium mb-2">Product Title *</label>
            <Input
              value={productData.title}
              onChange={(e) => handleInputChange('title', e.target.value)}
              placeholder="Ultimate Portfolio 2025"
              className={`text-lg font-semibold border-[#0097B2]/20 focus:border-[#0097B2] ${errors.title ? 'border-red-500' : ''}`}
            />
            {errors.title && (
              <p className="text-red-500 text-xs mt-1 flex items-center">
                <AlertCircle size={12} className="mr-1" />
                {errors.title}
              </p>
            )}
          </div>

          {/* Price & Category */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium mb-2">Price (USD) *</label>
              <div className="relative">
                <DollarSign size={16} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                <Input
                  type="number"
                  value={productData.price}
                  onChange={(e) => handleInputChange('price', e.target.value)}
                  placeholder="10"
                  min="0.01"
                  step="0.01"
                  className={`pl-9 border-[#0097B2]/20 focus:border-[#0097B2] ${errors.price ? 'border-red-500' : ''}`}
                />
              </div>
              {errors.price && (
                <p className="text-red-500 text-xs mt-1 flex items-center">
                  <AlertCircle size={12} className="mr-1" />
                  {errors.price}
                </p>
              )}
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-2">Category</label>
              <select
                value={productData.category}
                onChange={(e) => handleInputChange('category', e.target.value)}
                className="w-full p-2 border border-[#0097B2]/20 rounded-md focus:border-[#0097B2] focus:outline-none bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
              >
                <option value="portfolio">Portfolio Strategy</option>
                <option value="education">Educational Content</option>
                <option value="analysis">Market Analysis</option>
                <option value="tools">Trading Tools</option>
              </select>
            </div>
          </div>

          {/* Optional Metadata Fields */}
          <div>
            <h3 className="text-lg font-semibold text-[#474545] dark:text-white mb-3">
              Product Details (Optional)
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-6">
              {/* Risk Level */}
              <div>
                <label className="block text-sm font-medium mb-2">Risk Level</label>
                <select
                  value={productData.riskLevel}
                  onChange={(e) => handleInputChange('riskLevel', e.target.value)}
                  className="w-full p-2 border border-[#0097B2]/20 rounded-md focus:border-[#0097B2] focus:outline-none bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                >
                  <option value="Low">Low</option>
                  <option value="Medium">Medium</option>
                  <option value="High">High</option>
                </select>
              </div>

              {/* Expected Return */}
              <div>
                <label className="block text-sm font-medium mb-2">Expected Return (%)</label>
                <Input
                  type="number"
                  value={productData.expectedReturn}
                  onChange={(e) => handleInputChange('expectedReturn', e.target.value)}
                  placeholder="15"
                  min="0"
                  max="1000"
                  step="0.1"
                  className={`border-[#0097B2]/20 focus:border-[#0097B2] ${errors.expectedReturn ? 'border-red-500' : ''}`}
                />
                {errors.expectedReturn && (
                  <p className="text-red-500 text-xs mt-1 flex items-center">
                    <AlertCircle size={12} className="mr-1" />
                    {errors.expectedReturn}
                  </p>
                )}
              </div>

              {/* Minimum Investment */}
              <div>
                <label className="block text-sm font-medium mb-2">Minimum Investment (USD)</label>
                <div className="relative">
                  <DollarSign size={16} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                  <Input
                    type="number"
                    value={productData.minimumInvestment}
                    onChange={(e) => handleInputChange('minimumInvestment', e.target.value)}
                    placeholder="100"
                    min="0.01"
                    step="0.01"
                    className={`pl-9 border-[#0097B2]/20 focus:border-[#0097B2] ${errors.minimumInvestment ? 'border-red-500' : ''}`}
                  />
                </div>
                {errors.minimumInvestment && (
                  <p className="text-red-500 text-xs mt-1 flex items-center">
                    <AlertCircle size={12} className="mr-1" />
                    {errors.minimumInvestment}
                  </p>
                )}
              </div>

              {/* Asset Allocation */}
              <div>
                <label className="block text-sm font-medium mb-2">Asset Allocation</label>
                <Input
                  value={productData.assetAllocation}
                  onChange={(e) => handleInputChange('assetAllocation', e.target.value)}
                  placeholder="60% stocks, 30% bonds, 10% crypto"
                  className="border-[#0097B2]/20 focus:border-[#0097B2]"
                />
              </div>
            </div>
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-medium mb-2">
              Short Description * 
              <span className="text-xs text-gray-500 ml-2">
                ({productData.description.length}/140 characters)
              </span>
            </label>
            <Input
              value={productData.description}
              onChange={(e) => {
                const value = e.target.value;
                if (value.length <= 140) {
                  handleInputChange('description', value);
                }
              }}
              placeholder="A brief description of your product..."
              maxLength={140}
              className={`border-[#0097B2]/20 focus:border-[#0097B2] ${errors.description ? 'border-red-500' : ''}`}
            />
            <p className="text-xs text-gray-500 mt-1">
              Keep it concise and engaging - this appears on your product card
            </p>
            {errors.description && (
              <p className="text-red-500 text-xs mt-1 flex items-center">
                <AlertCircle size={12} className="mr-1" />
                {errors.description}
              </p>
            )}
          </div>

          {/* Content */}
          <div>
            <label className="block text-sm font-medium mb-2">Content *</label>
            <Textarea
              value={productData.content}
              onChange={(e) => handleInputChange('content', e.target.value)}
              placeholder="Start writing your content here..."
              className={`min-h-[200px] border-[#0097B2]/20 focus:border-[#0097B2] ${errors.content ? 'border-red-500' : ''}`}
            />
            {errors.content && (
              <p className="text-red-500 text-xs mt-1 flex items-center">
                <AlertCircle size={12} className="mr-1" />
                {errors.content}
              </p>
            )}
          </div>

          {/* File Attachments - Same as creation modal */}
          <div>
            <label className="block text-sm font-medium mb-3">Attachments</label>
            <div className="border-2 border-dashed border-[#0097B2]/20 rounded-lg p-6">
              <div className="flex flex-col sm:flex-row gap-3 mb-4">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => imageInputRef.current?.click()}
                  className="flex-1 border-[#0097B2]/20 hover:bg-[#0097B2]/5"
                >
                  <Image size={16} className="mr-2" />
                  Add Images
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => videoInputRef.current?.click()}
                  className="flex-1 border-[#0097B2]/20 hover:bg-[#0097B2]/5"
                >
                  <Video size={16} className="mr-2" />
                  Add Videos
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => fileInputRef.current?.click()}
                  className="flex-1 border-[#0097B2]/20 hover:bg-[#0097B2]/5"
                >
                  <FileText size={16} className="mr-2" />
                  Add Files
                </Button>
              </div>

              {/* Hidden file inputs */}
              <input
                ref={imageInputRef}
                type="file"
                multiple
                accept="image/*"
                onChange={(e) => handleFileUpload(e, 'image')}
                className="hidden"
              />
              <input
                ref={videoInputRef}
                type="file"
                multiple
                accept="video/*"
                onChange={(e) => handleFileUpload(e, 'video')}
                className="hidden"
              />
              <input
                ref={fileInputRef}
                type="file"
                multiple
                accept=".pdf,.doc,.docx,.txt,.xls,.xlsx"
                onChange={(e) => handleFileUpload(e, 'document')}
                className="hidden"
              />

              {/* Attachments List */}
              {productData.attachments.length > 0 && (
                <div className="space-y-2">
                  <h4 className="font-medium text-sm">Attached Files:</h4>
                  {productData.attachments.map((attachment) => (
                    <div key={attachment.id} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                      <div className="flex items-center space-x-3">
                        {renderAttachmentIcon(attachment.type)}
                        <div>
                          <p className="text-sm font-medium">{attachment.name}</p>
                          <p className="text-xs text-gray-500">{formatFileSize(attachment.size)}</p>
                        </div>
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => removeAttachment(attachment.id)}
                        className="text-red-500 hover:text-red-700"
                      >
                        <Trash2 size={16} />
                      </Button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row gap-3 pt-6 border-t pb-24 sm:pb-8">
            <Button
              variant="outline"
              onClick={handleDelete}
              className="w-full sm:w-auto border-red-200 text-red-600 hover:bg-red-50"
            >
              <Trash2 size={16} className="mr-2" />
              Delete Product
            </Button>
            <div className="flex-1" />
            <Button
              variant="outline"
              onClick={onClose}
              className="w-full sm:w-auto border-[#0097B2]/20"
            >
              Cancel
            </Button>
            <Button
              variant="outline"
              onClick={handlePreview}
              className="w-full sm:w-auto border-[#0097B2]/20 hover:bg-[#0097B2]/5"
            >
              <Eye size={16} className="mr-2" />
              Preview
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default ProductEditModal;