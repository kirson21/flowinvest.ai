import React, { useState } from 'react';
import { Share, Copy, Check, X } from 'lucide-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../ui/dialog';
import { Button } from '../ui/button';

const ShareButton = ({ 
  url, 
  title, 
  description, 
  type = 'profile', // 'profile', 'product', 'bot'
  size = 'default', // 'small', 'default'
  className = '' 
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [copied, setCopied] = useState(false);

  // Construct full URL
  const fullUrl = `${window.location.origin}${url}`;
  
  // Social media share URLs
  const shareUrls = {
    twitter: `https://twitter.com/intent/tweet?url=${encodeURIComponent(fullUrl)}&text=${encodeURIComponent(title)}`,
    linkedin: `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(fullUrl)}`,
    telegram: `https://t.me/share/url?url=${encodeURIComponent(fullUrl)}&text=${encodeURIComponent(title)}`,
    instagram: `https://www.instagram.com/`, // Instagram doesn't support direct URL sharing, but we can copy link
    tiktok: `https://www.tiktok.com/` // TikTok doesn't support direct URL sharing, but we can copy link
  };

  const handleCopyLink = async () => {
    try {
      await navigator.clipboard.writeText(fullUrl);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy: ', err);
    }
  };

  const handleSocialShare = (platform) => {
    if (platform === 'instagram' || platform === 'tiktok') {
      // For Instagram and TikTok, copy the link and show instruction
      handleCopyLink();
      return;
    }
    
    window.open(shareUrls[platform], '_blank', 'width=600,height=400');
  };

  const getTypeConfig = () => {
    switch (type) {
      case 'profile':
        return {
          icon: '👤',
          typeLabel: 'Profile',
          defaultTitle: title || 'Check out my f01i.ai profile',
          defaultDescription: description || 'Discover AI-powered investment tools and strategies'
        };
      case 'product':
        return {
          icon: '💼',
          typeLabel: 'Product',
          defaultTitle: title || 'Check out this investment portfolio',
          defaultDescription: description || 'Professional investment strategy on f01i.ai'
        };
      case 'bot':
        return {
          icon: '🤖',
          typeLabel: 'Trading Bot',
          defaultTitle: title || 'Check out this AI trading bot',
          defaultDescription: description || 'Advanced AI trading strategy on f01i.ai'
        };
      case 'post':
        return {
          icon: '📰',
          typeLabel: 'Feed Post',
          defaultTitle: title || 'Check out this market analysis',
          defaultDescription: description || 'AI-powered market insights from f01i.ai'
        };
      default:
        return {
          icon: '🔗',
          typeLabel: 'Link',
          defaultTitle: title || 'Check this out',
          defaultDescription: description || 'Shared from f01i.ai'
        };
    }
  };

  const config = getTypeConfig();
  const shareTitle = config.defaultTitle;
  const shareDescription = config.defaultDescription;

  // Button styles based on size
  const buttonStyles = size === 'small' 
    ? 'p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors'
    : 'flex items-center space-x-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors';

  const iconSize = size === 'small' ? 16 : 18;

  return (
    <>
      <button
        onClick={() => setIsOpen(true)}
        className={`${buttonStyles} ${className}`}
        title={`Share ${config.typeLabel.toLowerCase()}`}
      >
        <Share size={iconSize} className="text-gray-600 dark:text-gray-400" />
        {size !== 'small' && (
          <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
            Share {config.typeLabel}
          </span>
        )}
      </button>

      <Dialog open={isOpen} onOpenChange={setIsOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center space-x-2">
              <span className="text-xl">{config.icon}</span>
              <span>Share {config.typeLabel}</span>
            </DialogTitle>
          </DialogHeader>
          
          <div className="space-y-4">
            {/* Preview */}
            <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
              <h3 className="font-semibold text-sm mb-1">{shareTitle}</h3>
              <p className="text-xs text-gray-600 dark:text-gray-400 mb-2">{shareDescription}</p>
              <p className="text-xs text-blue-600 break-all">{fullUrl}</p>
            </div>

            {/* Social Media Buttons */}
            <div className="space-y-2">
              <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                Share on social media
              </p>
              
              <div className="grid grid-cols-2 gap-2">
                {/* Twitter/X */}
                <Button
                  onClick={() => handleSocialShare('twitter')}
                  variant="outline"
                  className="flex items-center space-x-2 justify-start"
                >
                  <div className="w-5 h-5 bg-black rounded flex items-center justify-center">
                    <span className="text-white text-xs font-bold">𝕏</span>
                  </div>
                  <span>Twitter/X</span>
                </Button>

                {/* LinkedIn */}
                <Button
                  onClick={() => handleSocialShare('linkedin')}
                  variant="outline"
                  className="flex items-center space-x-2 justify-start"
                >
                  <div className="w-5 h-5 bg-[#0077b5] rounded flex items-center justify-center">
                    <span className="text-white text-xs font-bold">in</span>
                  </div>
                  <span>LinkedIn</span>
                </Button>

                {/* Telegram */}
                <Button
                  onClick={() => handleSocialShare('telegram')}
                  variant="outline"
                  className="flex items-center space-x-2 justify-start"
                >
                  <div className="w-5 h-5 bg-[#0088cc] rounded-full flex items-center justify-center">
                    <span className="text-white text-xs">✈</span>
                  </div>
                  <span>Telegram</span>
                </Button>

                {/* TikTok */}
                <Button
                  onClick={() => handleSocialShare('tiktok')}
                  variant="outline"
                  className="flex items-center space-x-2 justify-start"
                >
                  <div className="w-5 h-5 bg-black rounded flex items-center justify-center">
                    <span className="text-white text-xs">🎵</span>
                  </div>
                  <span>TikTok</span>
                </Button>

                {/* Instagram */}
                <Button
                  onClick={() => handleSocialShare('instagram')}
                  variant="outline"
                  className="flex items-center space-x-2 justify-start col-span-2"
                >
                  <div className="w-5 h-5 bg-gradient-to-br from-purple-500 via-pink-500 to-orange-400 rounded flex items-center justify-center">
                    <span className="text-white text-xs">📷</span>
                  </div>
                  <span>Instagram (Copy link to share)</span>
                </Button>
              </div>
            </div>

            {/* Copy Link */}
            <div className="border-t pt-4">
              <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Or copy link
              </p>
              <div className="flex items-center space-x-2">
                <input
                  type="text"
                  value={fullUrl}
                  readOnly
                  className="flex-1 px-3 py-2 text-sm border rounded-md bg-gray-50 dark:bg-gray-800"
                />
                <Button
                  onClick={handleCopyLink}
                  size="sm"
                  className={`px-3 ${copied ? 'bg-green-600 hover:bg-green-700' : ''}`}
                >
                  {copied ? (
                    <>
                      <Check size={14} className="mr-1" />
                      Copied!
                    </>
                  ) : (
                    <>
                      <Copy size={14} className="mr-1" />
                      Copy
                    </>
                  )}
                </Button>
              </div>
            </div>

            {/* Instructions */}
            <div className="text-xs text-gray-500 dark:text-gray-400 bg-blue-50 dark:bg-blue-900/20 rounded p-3">
              <p><strong>Note:</strong> This link will show a public preview of your {config.typeLabel.toLowerCase()}. 
              Visitors will need to register to access full f01i.ai features.</p>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
};

export default ShareButton;