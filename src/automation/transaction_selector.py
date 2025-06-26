from .base_automation import BaseAutomation


class TransactionSelector(BaseAutomation):
    """Handles selecting transactions in Snelstart."""
    
    def select_transaction(self):
        """Select the first available transaction."""
        self.logger.info("Selecting first transaction...")
        
        # Placeholder for transaction selection logic
        # In a real implementation, you would:
        # 1. Find the transaction list
        # 2. Click on the first transaction
        
        self.wait()
        self.logger.info("Transaction selected")
        return True