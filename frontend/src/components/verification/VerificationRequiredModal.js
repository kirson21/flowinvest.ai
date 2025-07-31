import React, { useState } from 'react';
import { X, Shield, FileCheck, TrendingUp, Verified } from 'lucide-react';
import { Button } from '../ui/button';
import { Card, CardContent } from '../ui/card';
import VerificationApplicationModal from './VerificationApplicationModal';

const VerificationRequiredModal = ({ isOpen, onClose }) => {
  const [showApplicationModal, setShowApplicationModal] = useState(false);

  const handleApplyForVerification = () => {
    setShowApplicationModal(true);
  };

  const handleApplicationSuccess = () => {
    setShowApplicationModal(false);
    onClose();
  };

  if (!isOpen && !showApplicationModal) return null;

  if (showApplicationModal) {
    return (
      <VerificationApplicationModal
        isOpen={showApplicationModal}
        onClose={() => setShowApplicationModal(false)}
        onSuccess={handleApplicationSuccess}
      />
    );
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-2xl w-full max-w-md">
        <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center">
            <Shield className="text-yellow-500 mr-2" size={24} />
            <h2 className="text-xl font-bold text-gray-900 dark:text-white">
              Seller Verification Required!
            </h2>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={onClose}
          >
            <X size={20} />
          </Button>
        </div>

        <div className="p-6 space-y-4">
          <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
            This functionality is only available to verified sellers.
          </p>

          <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
            To become a seller, please submit an application and upload the necessary verification documents, including:
          </p>

          <div className="space-y-3">
            <div className="flex items-start space-x-3">
              <FileCheck className="text-[#0097B2] mt-0.5 flex-shrink-0" size={18} />
              <span className="text-sm text-gray-700 dark:text-gray-300">
                A valid ID or passport
              </span>
            </div>
            
            <div className="flex items-start space-x-3">
              <Verified className="text-[#0097B2] mt-0.5 flex-shrink-0" size={18} />
              <span className="text-sm text-gray-700 dark:text-gray-300">
                Professional certificates/diplomas (e.g., trader, investor, financial advisor, etc.)
              </span>
            </div>
            
            <div className="flex items-start space-x-3">
              <TrendingUp className="text-[#0097B2] mt-0.5 flex-shrink-0" size={18} />
              <span className="text-sm text-gray-700 dark:text-gray-300">
                Links or evidence of your trading performance or investment portfolio from other platforms over the past 6 months
              </span>
            </div>
            
            <div className="flex items-start space-x-3">
              <Shield className="text-[#0097B2] mt-0.5 flex-shrink-0" size={18} />
              <span className="text-sm text-gray-700 dark:text-gray-300">
                Proof that the provided account belongs to you
              </span>
            </div>
          </div>

          <Card className="bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800">
            <CardContent className="p-4">
              <p className="text-sm text-blue-800 dark:text-blue-200">
                <strong>Note:</strong> Once verified, you will be granted full access to seller features including product creation, seller mode, and marketplace management tools.
              </p>
            </CardContent>
          </Card>
        </div>

        <div className="flex gap-3 p-6 pt-0">
          <Button
            variant="outline"
            onClick={onClose}
            className="flex-1"
          >
            Cancel
          </Button>
          <Button
            onClick={handleApplyForVerification}
            className="flex-1 bg-[#0097B2] hover:bg-[#0097B2]/90"
          >
            Apply for Verification
          </Button>
        </div>
      </div>
    </div>
  );
};

export default VerificationRequiredModal;