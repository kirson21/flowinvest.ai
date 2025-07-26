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
  Check,
  Plus,
  Loader2
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
    contentBlocks: [], // Rich content blocks
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
  const [showMediaMenu, setShowMediaMenu] = useState(false);
  const [currentBlockIndex, setCurrentBlockIndex] = useState(0);
  const [menuPosition, setMenuPosition] = useState('after');
  const [activeBlockId, setActiveBlockId] = useState(null);
  const [attachmentCount, setAttachmentCount] = useState(0);
  const fileInputRef = useRef(null);
  const imageInputRef = useRef(null);
  const videoInputRef = useRef(null);

  const MAX_ATTACHMENTS = 30;

  // Initialize form data when product changes
  useEffect(() => {
    if (product && isOpen) {
      setProductData({
        title: product.title || product.name || '',
        description: product.description || '',
        content: product.content || '',
        contentBlocks: product.contentBlocks || [{ type: 'text', content: product.content || '', id: Date.now() }],
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
      // Update attachment count
      setTimeout(updateAttachmentCount, 100);
    }
  }, [product, isOpen]);

  // Rich content editor functions
  const updateAttachmentCount = () => {
    const mediaBlocks = productData.contentBlocks.filter(block => 
      (block.type !== 'text') && block.file
    );
    setAttachmentCount(mediaBlocks.length);
  };

  const addContentBlock = (type, afterIndex, position = 'after') => {
    if (type !== 'text' && attachmentCount >= MAX_ATTACHMENTS) {
      alert(`Maximum ${MAX_ATTACHMENTS} attachments allowed. Please remove some attachments before adding more.`);
      setShowMediaMenu(false);
      return;
    }

    const newBlock = {
      type: type,
      content: type === 'text' ? '' : null,
      id: Date.now() + Math.random(),
      ...(type !== 'text' && { file: null, uploading: false })
    };

    const newBlocks = [...productData.contentBlocks];
    const insertIndex = position === 'after' ? afterIndex + 1 : afterIndex;
    newBlocks.splice(insertIndex, 0, newBlock);
    
    setProductData(prev => ({
      ...prev,
      contentBlocks: newBlocks
    }));
    
    setShowMediaMenu(false);
    setActiveBlockId(null);
    setTimeout(updateAttachmentCount, 100);
  };

  const updateContentBlock = (blockId, updates) => {
    setProductData(prev => ({
      ...prev,
      contentBlocks: prev.contentBlocks.map(block =>
        block.id === blockId ? { ...block, ...updates } : block
      )
    }));
    
    if (updates.file !== undefined) {
      setTimeout(updateAttachmentCount, 100);
    }
  };

  const removeContentBlock = (blockId) => {
    if (productData.contentBlocks.length <= 1) {
      alert('You must have at least one content block.');
      return;
    }

    setProductData(prev => ({
      ...prev,
      contentBlocks: prev.contentBlocks.filter(block => block.id !== blockId)
    }));
    
    setTimeout(updateAttachmentCount, 100);
  };

  const handlePlusButtonClick = (index, position = 'after') => {
    setCurrentBlockIndex(index);
    setMenuPosition(position);
    setShowMediaMenu(!showMediaMenu);
  };

  const handleTextBlockFocus = (blockId) => {
    setActiveBlockId(blockId);
  };

  const handleTextBlockKeyDown = (e, blockId, blockIndex) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      
      const textarea = e.target;
      const cursorPosition = textarea.selectionStart;
      const currentContent = textarea.value;
      
      const beforeCursor = currentContent.slice(0, cursorPosition);
      const afterCursor = currentContent.slice(cursorPosition);
      
      updateContentBlock(blockId, { content: beforeCursor });
      
      const newBlock = {
        type: 'text',
        content: afterCursor,
        id: Date.now() + Math.random()
      };
      
      const newBlocks = [...productData.contentBlocks];
      newBlocks.splice(blockIndex + 1, 0, newBlock);
      
      setProductData(prev => ({
        ...prev,
        contentBlocks: newBlocks
      }));
      
      setTimeout(() => {
        const newTextarea = document.querySelector(`[data-block-id="${newBlock.id}"]`);
        if (newTextarea) {
          newTextarea.focus();
          newTextarea.setSelectionRange(0, 0);
        }
      }, 50);
    }
  };

  const handleContentMediaUpload = async (file, blockId) => {
    if (!file) return;

    updateContentBlock(blockId, { uploading: true });

    try {
      const uploadResult = await FileUploadService.uploadProductAttachment(file);
      
      updateContentBlock(blockId, {
        file: {
          name: file.name,
          size: file.size,
          type: FileUploadService.getFileType(file.name),
          url: uploadResult.publicUrl,
          path: uploadResult.path,
          bucket: uploadResult.bucket
        },
        uploading: false
      });

    } catch (error) {
      console.error('Error uploading media:', error);
      alert('Error uploading media. Please try again.');
      updateContentBlock(blockId, { uploading: false });
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  // Close media menu when clicking outside
  React.useEffect(() => {
    const handleClickOutside = (event) => {
      if (showMediaMenu && !event.target.closest('.media-menu-container')) {
        setShowMediaMenu(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [showMediaMenu]);

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

          {/* Rich Content Editor */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="block text-sm font-medium">Content *</label>
              <div className="text-xs text-gray-500">
                Attachments: {attachmentCount}/{MAX_ATTACHMENTS}
              </div>
            </div>
            <div className={`border rounded-lg ${errors.content ? 'border-red-500' : 'border-[#0097B2]/20'} min-h-[300px] relative overflow-hidden`}>
              {productData.contentBlocks.map((block, index) => (
                <div key={block.id} className="relative group hover:bg-gray-50/30 transition-colors">
                  {/* Content Block */}
                  {block.type === 'text' ? (
                    <div className="relative">
                      <Textarea
                        data-block-id={block.id}
                        value={block.content}
                        onChange={(e) => updateContentBlock(block.id, { content: e.target.value })}
                        onFocus={() => handleTextBlockFocus(block.id)}
                        onKeyDown={(e) => handleTextBlockKeyDown(e, block.id, index)}
                        placeholder={index === 0 ? "Edit your content here... Press Enter to create new paragraphs, hover to see + button for adding media." : "Continue writing... Press Enter for new paragraph."}
                        className="border-0 resize-none focus:ring-0 min-h-[120px] w-full bg-transparent"
                        style={{ boxShadow: 'none' }}
                      />
                      
                      {/* Dynamic Plus Button for Text Blocks */}
                      <div className={`absolute -left-10 top-4 transition-opacity duration-200 ${
                        activeBlockId === block.id || (showMediaMenu && currentBlockIndex === index && menuPosition === 'after')
                          ? 'opacity-100' 
                          : 'opacity-0 group-hover:opacity-100'
                      }`}>
                        <div className="relative">
                          <Button
                            type="button"
                            size="sm"
                            onClick={() => handlePlusButtonClick(index, 'after')}
                            className="w-8 h-8 rounded-full bg-white border-2 border-[#0097B2] text-[#0097B2] hover:bg-[#0097B2] hover:text-white shadow-lg p-0 transition-all duration-200 hover:scale-110"
                          >
                            <Plus size={16} />
                          </Button>
                          
                          {/* Interactive Media Menu */}
                          {showMediaMenu && currentBlockIndex === index && menuPosition === 'after' && (
                            <div className="media-menu-container absolute left-10 top-0 bg-white border border-gray-200 rounded-lg shadow-xl py-2 min-w-[180px] z-20 animate-in fade-in-0 zoom-in-95 duration-200">
                              <div className="px-3 py-1 text-xs text-gray-500 border-b">Add Content</div>
                              <button
                                type="button"
                                onClick={() => addContentBlock('text', index, 'after')}
                                className="w-full text-left px-4 py-3 hover:bg-gray-50 flex items-center space-x-3 text-sm transition-colors"
                              >
                                <FileText size={16} className="text-blue-500" />
                                <span>Text Paragraph</span>
                              </button>
                              <button
                                type="button"
                                onClick={() => addContentBlock('image', index, 'after')}
                                disabled={attachmentCount >= MAX_ATTACHMENTS}
                                className={`w-full text-left px-4 py-3 hover:bg-gray-50 flex items-center space-x-3 text-sm transition-colors ${
                                  attachmentCount >= MAX_ATTACHMENTS ? 'opacity-50 cursor-not-allowed' : ''
                                }`}
                              >
                                <Image size={16} className="text-green-500" />
                                <div>
                                  <div>Image</div>
                                  {attachmentCount >= MAX_ATTACHMENTS && (
                                    <div className="text-xs text-red-500">Limit reached</div>
                                  )}
                                </div>
                              </button>
                              <button
                                type="button"
                                onClick={() => addContentBlock('video', index, 'after')}
                                disabled={attachmentCount >= MAX_ATTACHMENTS}
                                className={`w-full text-left px-4 py-3 hover:bg-gray-50 flex items-center space-x-3 text-sm transition-colors ${
                                  attachmentCount >= MAX_ATTACHMENTS ? 'opacity-50 cursor-not-allowed' : ''
                                }`}
                              >
                                <Video size={16} className="text-purple-500" />
                                <div>
                                  <div>Video</div>
                                  {attachmentCount >= MAX_ATTACHMENTS && (
                                    <div className="text-xs text-red-500">Limit reached</div>
                                  )}
                                </div>
                              </button>
                              <button
                                type="button"
                                onClick={() => addContentBlock('file', index, 'after')}
                                disabled={attachmentCount >= MAX_ATTACHMENTS}
                                className={`w-full text-left px-4 py-3 hover:bg-gray-50 flex items-center space-x-3 text-sm transition-colors ${
                                  attachmentCount >= MAX_ATTACHMENTS ? 'opacity-50 cursor-not-allowed' : ''
                                }`}
                              >
                                <FileText size={16} className="text-orange-500" />
                                <div>
                                  <div>Document</div>
                                  {attachmentCount >= MAX_ATTACHMENTS && (
                                    <div className="text-xs text-red-500">Limit reached</div>
                                  )}
                                </div>
                              </button>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  ) : block.type === 'image' ? (
                    <div className="p-4 border-t border-gray-200 bg-gray-50/30">
                      {block.uploading ? (
                        <div className="flex items-center justify-center p-8 bg-white rounded-lg border-2 border-dashed border-gray-300">
                          <Loader2 size={24} className="animate-spin mr-2 text-[#0097B2]" />
                          <span>Uploading image...</span>
                        </div>
                      ) : block.file ? (
                        <div className="relative bg-white rounded-lg overflow-hidden shadow-sm">
                          <img 
                            src={block.file.url} 
                            alt={block.file.name}
                            className="max-w-full h-auto rounded-lg"
                          />
                          <Button
                            type="button"
                            variant="destructive"
                            size="sm"
                            onClick={() => removeContentBlock(block.id)}
                            className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity shadow-lg"
                          >
                            <Trash2 size={14} />
                          </Button>
                          <div className="absolute bottom-0 left-0 right-0 bg-black/50 text-white text-xs p-2">
                            {block.file.name}
                          </div>
                        </div>
                      ) : (
                        <div className="flex items-center justify-center p-8 bg-white rounded-lg border-2 border-dashed border-gray-300 hover:border-[#0097B2] transition-colors">
                          <div className="text-center">
                            <Image size={48} className="mx-auto mb-3 text-gray-400" />
                            <input
                              type="file"
                              accept="image/*"
                              onChange={(e) => e.target.files[0] && handleContentMediaUpload(e.target.files[0], block.id)}
                              className="hidden"
                              id={`image-${block.id}`}
                            />
                            <label htmlFor={`image-${block.id}`} className="cursor-pointer text-[#0097B2] hover:underline font-medium">
                              Click to upload image
                            </label>
                            <p className="text-xs text-gray-500 mt-1">Supports JPG, PNG, GIF, WebP</p>
                          </div>
                        </div>
                      )}
                    </div>
                  ) : block.type === 'video' ? (
                    <div className="p-4 border-t border-gray-200 bg-gray-50/30">
                      {block.uploading ? (
                        <div className="flex items-center justify-center p-8 bg-white rounded-lg border-2 border-dashed border-gray-300">
                          <Loader2 size={24} className="animate-spin mr-2 text-[#0097B2]" />
                          <span>Uploading video...</span>
                        </div>
                      ) : block.file ? (
                        <div className="relative bg-white rounded-lg overflow-hidden shadow-sm">
                          <video 
                            src={block.file.url} 
                            controls
                            className="max-w-full h-auto rounded-lg"
                          />
                          <Button
                            type="button"
                            variant="destructive"
                            size="sm"
                            onClick={() => removeContentBlock(block.id)}
                            className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity shadow-lg"
                          >
                            <Trash2 size={14} />
                          </Button>
                          <div className="absolute bottom-0 left-0 right-0 bg-black/50 text-white text-xs p-2">
                            {block.file.name}
                          </div>
                        </div>
                      ) : (
                        <div className="flex items-center justify-center p-8 bg-white rounded-lg border-2 border-dashed border-gray-300 hover:border-[#0097B2] transition-colors">
                          <div className="text-center">
                            <Video size={48} className="mx-auto mb-3 text-gray-400" />
                            <input
                              type="file"
                              accept="video/*"
                              onChange={(e) => e.target.files[0] && handleContentMediaUpload(e.target.files[0], block.id)}
                              className="hidden"
                              id={`video-${block.id}`}
                            />
                            <label htmlFor={`video-${block.id}`} className="cursor-pointer text-[#0097B2] hover:underline font-medium">
                              Click to upload video
                            </label>
                            <p className="text-xs text-gray-500 mt-1">Supports MP4, WebM, MOV</p>
                          </div>
                        </div>
                      )}
                    </div>
                  ) : block.type === 'file' ? (
                    <div className="p-4 border-t border-gray-200 bg-gray-50/30">
                      {block.uploading ? (
                        <div className="flex items-center justify-center p-8 bg-white rounded-lg border-2 border-dashed border-gray-300">
                          <Loader2 size={24} className="animate-spin mr-2 text-[#0097B2]" />
                          <span>Uploading document...</span>
                        </div>
                      ) : block.file ? (
                        <div className="relative p-4 bg-white rounded-lg border hover:shadow-sm transition-shadow">
                          <div className="flex items-center space-x-3">
                            <FileText size={32} className="text-gray-500" />
                            <div className="flex-1">
                              <p className="font-medium text-sm">{block.file.name}</p>
                              <p className="text-xs text-gray-500">{formatFileSize(block.file.size)}</p>
                            </div>
                            <Button
                              type="button"
                              variant="destructive"
                              size="sm"
                              onClick={() => removeContentBlock(block.id)}
                              className="opacity-0 group-hover:opacity-100 transition-opacity"
                            >
                              <Trash2 size={14} />
                            </Button>
                          </div>
                        </div>
                      ) : (
                        <div className="flex items-center justify-center p-8 bg-white rounded-lg border-2 border-dashed border-gray-300 hover:border-[#0097B2] transition-colors">
                          <div className="text-center">
                            <FileText size={48} className="mx-auto mb-3 text-gray-400" />
                            <input
                              type="file"
                              accept=".pdf,.doc,.docx,.txt,.xls,.xlsx,.ppt,.pptx"
                              onChange={(e) => e.target.files[0] && handleContentMediaUpload(e.target.files[0], block.id)}
                              className="hidden"
                              id={`file-${block.id}`}
                            />
                            <label htmlFor={`file-${block.id}`} className="cursor-pointer text-[#0097B2] hover:underline font-medium">
                              Click to upload document
                            </label>
                            <p className="text-xs text-gray-500 mt-1">Supports PDF, DOC, XLS, PPT, TXT</p>
                          </div>
                        </div>
                      )}
                    </div>
                  ) : null}

                  {/* Block separator and plus button for between blocks */}
                  {index < productData.contentBlocks.length - 1 && (
                    <div className="relative h-4 flex items-center justify-center group hover:bg-gray-100/50">
                      <div className="w-full h-px bg-gray-200"></div>
                      <div className={`absolute transition-opacity duration-200 ${
                        showMediaMenu && currentBlockIndex === index && menuPosition === 'between' ? 'opacity-100' : 'opacity-0 group-hover:opacity-100'
                      }`}>
                        <div className="relative">
                          <Button
                            type="button"
                            size="sm"
                            onClick={() => handlePlusButtonClick(index, 'between')}
                            className="w-6 h-6 rounded-full bg-white border border-gray-300 text-gray-600 hover:border-[#0097B2] hover:text-[#0097B2] shadow-sm p-0 transition-all duration-200"
                          >
                            <Plus size={12} />
                          </Button>
                          
                          {/* Between blocks menu */}
                          {showMediaMenu && currentBlockIndex === index && menuPosition === 'between' && (
                            <div className="media-menu-container absolute left-8 top-0 bg-white border border-gray-200 rounded-lg shadow-xl py-2 min-w-[180px] z-20">
                              <div className="px-3 py-1 text-xs text-gray-500 border-b">Insert Content</div>
                              <button
                                type="button"
                                onClick={() => addContentBlock('text', index, 'after')}
                                className="w-full text-left px-4 py-3 hover:bg-gray-50 flex items-center space-x-3 text-sm transition-colors"
                              >
                                <FileText size={16} className="text-blue-500" />
                                <span>Text Paragraph</span>
                              </button>
                              <button
                                type="button"
                                onClick={() => addContentBlock('image', index, 'after')}
                                disabled={attachmentCount >= MAX_ATTACHMENTS}
                                className={`w-full text-left px-4 py-3 hover:bg-gray-50 flex items-center space-x-3 text-sm transition-colors ${
                                  attachmentCount >= MAX_ATTACHMENTS ? 'opacity-50 cursor-not-allowed' : ''
                                }`}
                              >
                                <Image size={16} className="text-green-500" />
                                <span>Image</span>
                              </button>
                              <button
                                type="button"
                                onClick={() => addContentBlock('video', index, 'after')}
                                disabled={attachmentCount >= MAX_ATTACHMENTS}
                                className={`w-full text-left px-4 py-3 hover:bg-gray-50 flex items-center space-x-3 text-sm transition-colors ${
                                  attachmentCount >= MAX_ATTACHMENTS ? 'opacity-50 cursor-not-allowed' : ''
                                }`}
                              >
                                <Video size={16} className="text-purple-500" />
                                <span>Video</span>
                              </button>
                              <button
                                type="button"
                                onClick={() => addContentBlock('file', index, 'after')}
                                disabled={attachmentCount >= MAX_ATTACHMENTS}
                                className={`w-full text-left px-4 py-3 hover:bg-gray-50 flex items-center space-x-3 text-sm transition-colors ${
                                  attachmentCount >= MAX_ATTACHMENTS ? 'opacity-50 cursor-not-allowed' : ''
                                }`}
                              >
                                <FileText size={16} className="text-orange-500" />
                                <span>Document</span>
                              </button>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              ))}
              
              {/* Add block at the end */}
              <div className="p-4 border-t border-gray-200 bg-gray-50/20">
                <div className="relative">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => handlePlusButtonClick(productData.contentBlocks.length - 1, 'end')}
                    className="w-full border-dashed border-[#0097B2]/30 text-[#0097B2] hover:bg-[#0097B2]/5 transition-colors"
                  >
                    <Plus size={16} className="mr-2" />
                    Add More Content
                  </Button>
                  
                  {/* End menu */}
                  {showMediaMenu && menuPosition === 'end' && (
                    <div className="media-menu-container absolute left-0 top-12 bg-white border border-gray-200 rounded-lg shadow-xl py-2 min-w-[180px] z-20">
                      <div className="px-3 py-1 text-xs text-gray-500 border-b">Add Content</div>
                      <button
                        type="button"
                        onClick={() => addContentBlock('text', productData.contentBlocks.length - 1, 'after')}
                        className="w-full text-left px-4 py-3 hover:bg-gray-50 flex items-center space-x-3 text-sm transition-colors"
                      >
                        <FileText size={16} className="text-blue-500" />
                        <span>Text Paragraph</span>
                      </button>
                      <button
                        type="button"
                        onClick={() => addContentBlock('image', productData.contentBlocks.length - 1, 'after')}
                        disabled={attachmentCount >= MAX_ATTACHMENTS}
                        className={`w-full text-left px-4 py-3 hover:bg-gray-50 flex items-center space-x-3 text-sm transition-colors ${
                          attachmentCount >= MAX_ATTACHMENTS ? 'opacity-50 cursor-not-allowed' : ''
                        }`}
                      >
                        <Image size={16} className="text-green-500" />
                        <span>Image</span>
                      </button>
                      <button
                        type="button"
                        onClick={() => addContentBlock('video', productData.contentBlocks.length - 1, 'after')}
                        disabled={attachmentCount >= MAX_ATTACHMENTS}
                        className={`w-full text-left px-4 py-3 hover:bg-gray-50 flex items-center space-x-3 text-sm transition-colors ${
                          attachmentCount >= MAX_ATTACHMENTS ? 'opacity-50 cursor-not-allowed' : ''
                        }`}
                      >
                        <Video size={16} className="text-purple-500" />
                        <span>Video</span>
                      </button>
                      <button
                        type="button"
                        onClick={() => addContentBlock('file', productData.contentBlocks.length - 1, 'after')}
                        disabled={attachmentCount >= MAX_ATTACHMENTS}
                        className={`w-full text-left px-4 py-3 hover:bg-gray-50 flex items-center space-x-3 text-sm transition-colors ${
                          attachmentCount >= MAX_ATTACHMENTS ? 'opacity-50 cursor-not-allowed' : ''
                        }`}
                      >
                        <FileText size={16} className="text-orange-500" />
                        <span>Document</span>
                      </button>
                    </div>
                  )}
                </div>
              </div>
            </div>
            {errors.content && (
              <p className="text-red-500 text-xs mt-1 flex items-center">
                <AlertCircle size={12} className="mr-1" />
                {errors.content}
              </p>
            )}
            <p className="text-xs text-gray-500 mt-2">
              💡 <strong>Pro tip:</strong> Press Enter to create new paragraphs, hover over text to add media inline, maximum {MAX_ATTACHMENTS} attachments allowed.
            </p>
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