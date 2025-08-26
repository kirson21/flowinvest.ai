-- Add fields to track actual NowPayments payment IDs for better webhook synchronization
ALTER TABLE public.subscription_email_validation 
ADD COLUMN nowpayments_payment_id TEXT;

ALTER TABLE public.subscription_email_validation 
ADD COLUMN actual_amount_paid DECIMAL(10, 2) DEFAULT 0;

-- Add index for better performance
CREATE INDEX IF NOT EXISTS idx_subscription_email_validation_payment_id 
ON public.subscription_email_validation(nowpayments_payment_id);

-- Add comments
COMMENT ON COLUMN public.subscription_email_validation.nowpayments_payment_id 
IS 'Actual payment ID from NowPayments webhook for tracking';

COMMENT ON COLUMN public.subscription_email_validation.actual_amount_paid 
IS 'Actual amount paid as reported by NowPayments webhook';