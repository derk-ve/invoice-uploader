import sys
import os
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent))

from utils.config_manager import load_config, get_config_value
from utils.logger import setup_logger
from src.snelstart_automation import SnelstartAutomation


def main():
    # Load configuration
    config = load_config()
    if not config:
        print("Failed to load configuration. Exiting.")
        return
    
    # Setup logging
    logs_dir = get_config_value(config, 'paths.logs', './logs')
    logger = setup_logger(logs_dir)
    
    logger.info("Starting Snelstart Invoice Automation")
    
    # Get invoices directory
    invoices_dir = get_config_value(config, 'paths.invoices', './invoices')
    invoices_path = Path(invoices_dir)
    
    # Check if invoices directory exists and has files
    if not invoices_path.exists():
        logger.error(f"Invoices directory not found: {invoices_path}")
        return
    
    # Get list of invoice files
    invoice_files = list(invoices_path.glob('*'))
    invoice_files = [f for f in invoice_files if f.is_file()]
    
    if not invoice_files:
        logger.warning(f"No invoice files found in {invoices_path}")
        return
    
    # Initialize automation
    automation = SnelstartAutomation(config, logger)
    
    # Process the first invoice (MVP approach)
    first_invoice = invoice_files[0]
    logger.info(f"Processing invoice: {first_invoice.name}")
    
    success = automation.process_single_invoice(str(first_invoice))
    
    if success:
        logger.info("Automation completed successfully")
    else:
        logger.error("Automation failed")


if __name__ == "__main__":
    main()
