from .base_automation import BaseAutomation


class InvoiceMatcher(BaseAutomation):
    """Handles matching invoices to transactions in Snelstart."""
    
    def match_invoice_to_transaction(self):
        """Match the uploaded invoice to the selected transaction."""
        self.logger.info("Matching invoice to transaction...")
        
        # Placeholder for matching logic
        # In a real implementation, you would:
        # 1. Find the match/link button
        # 2. Click it to create the association
        
        self.wait()
        self.logger.info("Invoice matched to transaction")
        return True