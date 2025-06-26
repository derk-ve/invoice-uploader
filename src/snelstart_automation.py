from .automation.app_launcher import AppLauncher
from .automation.login_handler import LoginHandler
from .automation.invoice_uploader import InvoiceUploader
from .automation.transaction_selector import TransactionSelector
from .automation.invoice_matcher import InvoiceMatcher
from .automation.result_saver import ResultSaver


class SnelstartAutomation:
    """Main orchestrator class for Snelstart automation workflow."""
    
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        
        # Initialize all automation components
        self.app_launcher = AppLauncher(config, logger)
        self.login_handler = LoginHandler(config, logger)
        self.invoice_uploader = InvoiceUploader(config, logger)
        self.transaction_selector = TransactionSelector(config, logger)
        self.invoice_matcher = InvoiceMatcher(config, logger)
        self.result_saver = ResultSaver(config, logger)
    
    def process_single_invoice(self, invoice_path):
        """Process a single invoice through the complete workflow."""
        self.logger.info(f"Starting invoice processing workflow for: {invoice_path}")
        
        steps = [
            ("Launch Snelstart", self.app_launcher.launch_snelstart),
            ("Login", self.login_handler.login),
            ("Upload Invoice", lambda: self.invoice_uploader.upload_invoice(invoice_path)),
            ("Select Transaction", self.transaction_selector.select_transaction),
            ("Match Invoice to Transaction", self.invoice_matcher.match_invoice_to_transaction),
            ("Save Result", self.result_saver.save_result)
        ]
        
        for step_name, step_func in steps:
            self.logger.info(f"Executing step: {step_name}")
            if not step_func():
                self.logger.error(f"Step failed: {step_name}")
                return False
        
        self.logger.info("Invoice processing completed successfully")
        return True