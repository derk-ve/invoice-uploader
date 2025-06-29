from .automation.app_launcher import AppLauncher
from .automation.login_handler import LoginHandler
from .automation.invoice_uploader import InvoiceUploader
from .automation.transaction_selector import TransactionSelector
from .automation.invoice_matcher import InvoiceMatcher
from .automation.result_saver import ResultSaver

# Handle UI automation imports
try:
    import uiautomation as auto
    UI_AUTOMATION_AVAILABLE = True
except ImportError:
    UI_AUTOMATION_AVAILABLE = False


class SnelstartAutomation:
    """Main orchestrator class for Snelstart automation workflow."""
    
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        
        # Window management
        self.current_window = None
        self.window_cache = {}
        self.window_patterns = [
            lambda name: 'SnelStart' in name,
            lambda name: 'snelstart' in name,
            lambda name: 'SNELSTART' in name
        ]
        
        # Initialize all automation components
        self.app_launcher = AppLauncher(config, logger)
        self.login_handler = LoginHandler(config, logger, automation=self)  # Only LoginHandler needs automation reference
        self.invoice_uploader = InvoiceUploader(config, logger)
        self.transaction_selector = TransactionSelector(config, logger)
        self.invoice_matcher = InvoiceMatcher(config, logger)
        self.result_saver = ResultSaver(config, logger)
    
    def get_current_window(self, refresh=False):
        """
        Get the current Snelstart window, with option to refresh.
        
        Args:
            refresh: Force refresh of window reference
            
        Returns:
            Current Snelstart window or None if not found
        """
        if not UI_AUTOMATION_AVAILABLE:
            self.logger.warning("UI automation not available")
            return None
        
        # Return cached window if valid and not refreshing
        if not refresh and self.current_window:
            try:
                if self.current_window.Exists():
                    return self.current_window
            except Exception:
                # Window is no longer valid, clear it
                self.current_window = None
        
        # Find new window
        self.logger.info("Finding Snelstart window...")
        
        try:
            for pattern_func in self.window_patterns:
                window = auto.WindowControl(searchDepth=1, Name=pattern_func)
                if window.Exists(maxSearchSeconds=5):
                    self.current_window = window
                    self.logger.info(f"Found Snelstart window: {window.Name}")
                    return window
            
            self.logger.warning("Snelstart window not found")
            return None
            
        except Exception as e:
            self.logger.error(f"Error finding Snelstart window: {str(e)}")
            return None
    
    def wait_for_window(self, timeout=30):
        """
        Wait for Snelstart window to appear.
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Returns:
            Snelstart window if found within timeout, None otherwise
        """
        self.logger.info(f"Waiting for Snelstart window (timeout: {timeout}s)...")
        
        import time
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            window = self.get_current_window(refresh=True)
            if window:
                return window
            time.sleep(1)
        
        self.logger.error(f"Snelstart window not found within {timeout} seconds")
        return None
    
    def focus_window(self):
        """
        Bring the Snelstart window to the foreground.
        
        Returns:
            True if successful, False otherwise
        """
        window = self.get_current_window()
        if not window:
            self.logger.error("Cannot focus window - window not found")
            return False
        
        try:
            window.SetFocus()
            self.logger.debug("Window focused successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to focus window: {str(e)}")
            return False
    
    def is_window_ready(self):
        """
        Check if the Snelstart window is ready for automation.
        
        Returns:
            True if window is ready, False otherwise
        """
        window = self.get_current_window()
        if not window:
            return False
        
        try:
            return window.Exists() and window.IsVisible
        except Exception:
            return False
    
    def cache_window(self, key, window):
        """
        Cache a window reference for later use.
        
        Args:
            key: Cache key for the window
            window: Window to cache
        """
        self.window_cache[key] = window
        self.logger.debug(f"Cached window: {key}")
    
    def get_cached_window(self, key):
        """
        Get a cached window reference.
        
        Args:
            key: Cache key for the window
            
        Returns:
            Cached window or None if not found/invalid
        """
        if key not in self.window_cache:
            return None
        
        window = self.window_cache[key]
        try:
            if window.Exists():
                return window
            else:
                # Window no longer valid, remove from cache
                del self.window_cache[key]
                return None
        except Exception:
            # Window reference is invalid, remove from cache
            del self.window_cache[key]
            return None
    
    def process_single_invoice(self, invoice_path):
        """Process a single invoice through the complete workflow."""
        self.logger.info(f"Starting invoice processing workflow for: {invoice_path}")
        
        steps = [
            ("Launch Snelstart", self.app_launcher.launch_snelstart),
            ("Wait for Window", lambda: self.wait_for_window()),
            ("Focus Window", self.focus_window),
            ("Login", self.login_handler.login),
            ("Upload Invoice", lambda: self.invoice_uploader.upload_invoice(invoice_path)),
            ("Select Transaction", self.transaction_selector.select_transaction),
            ("Match Invoice to Transaction", self.invoice_matcher.match_invoice_to_transaction),
            ("Save Result", self.result_saver.save_result)
        ]
        
        for step_name, step_func in steps:
            self.logger.info(f"Executing step: {step_name}")
            
            # Special handling for window setup steps
            if step_name == "Wait for Window":
                result = step_func()
                if not result:
                    self.logger.error(f"Step failed: {step_name}")
                    return False
            else:
                if not step_func():
                    self.logger.error(f"Step failed: {step_name}")
                    return False
        
        self.logger.info("Invoice processing completed successfully")
        return True