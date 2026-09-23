# Payment Troubleshooting and Billing Guide

## 1. Failed Payment Handling
- **Symptoms**: Customer reports money deducted from bank account, but checkout status shows "Failed", "Pending", or "Error".
- **Root Cause**: Inter-bank payment gateway timeouts, 3D Secure authentication delays, or temporary ledger locks.
- **Resolution Procedure**:
  1. Verify the Transaction ID or payment reference number in the gateway logs.
  2. If the bank deducted money without issuing an authorization token, the payment gateway auto-reverses funds within **24 hours**.
  3. If funds are not auto-reversed within 24 hours, escalate ticket to **Payments Team** with customer bank transaction receipt.
  4. Instruct the customer to provide proof of deduction (last 4 digits of card, transaction timestamp).

## 2. Supported Payment Methods
- Visa, MasterCard, American Express, Discover credit/debit cards.
- PayPal, Apple Pay, Google Pay.
- ACH Direct Debit (US accounts only).

## 3. Recurring Subscription Charges
- Subscriptions auto-renew on the billing cycle date.
- Failed renewal attempts retry on Day 1, Day 3, and Day 7 before account grace period expires.
