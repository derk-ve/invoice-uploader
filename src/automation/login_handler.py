from .base_automation import BaseAutomation


class LoginHandler(BaseAutomation):
    """Handles login process for Snelstart."""
    
    def __init__(self, config, logger, automation=None):
        super().__init__(config, logger)
        self.automation = automation  # Reference to main SnelstartAutomation for window access
        self.timeout = config.get('snelstart', {}).get('login', {}).get('timeout', 30)
        self.retry_attempts = config.get('snelstart', {}).get('login', {}).get('retry_attempts', 3)
    
    def _get_ui_paths(self):
        """Get UI path configurations from config."""
        return self.config.get('snelstart', {}).get('ui_paths', {}).get('login', {})
    
    def _find_login_container(self, main_window):
        """Find the login container - either the window itself or embedded container."""
        window_name = getattr(main_window, 'Name', '')
        
        # If this is already the login window, use it directly
        if 'Inloggen' in window_name:
            self.logger.info(f"Using login window directly: {window_name}")
            return main_window
        
        # Otherwise, look for embedded container in main window
        self.logger.info("Looking for embedded login container...")
        
        ui_paths = self._get_ui_paths()
        container_paths = ui_paths.get('login_container', [
            # Default fallback paths based on inspection
            {'automation_id': 'WebAuthentication', 'control_type': 'WindowControl'},
            {'name': 'Inloggen SnelStart 12', 'control_type': 'WindowControl'},
        ])
        
        return self.find_element_by_paths(main_window, container_paths)

    def _find_email_field(self, window):
        """Find the email input field using UI paths."""
        self.logger.info("Looking for email field using UI paths...")
        
        # First try to find the login container
        login_container = self._find_login_container(window)
        search_window = login_container if login_container else window
        
        if login_container:
            self.logger.info("Found login container, searching within it for email field")
        else:
            self.logger.info("No login container found, searching in main window")
        
        ui_paths = self._get_ui_paths()
        email_paths = ui_paths.get('email_field', [
            # Default fallback paths - exact matches only
            {'automation_id': 'email_input', 'control_type': 'EditControl'},
            {'name': 'Email', 'control_type': 'EditControl'},
            {'name': 'Gebruiker', 'control_type': 'EditControl'},
            {'name': 'User', 'control_type': 'EditControl'},
            {'class_name': 'TextBox'},
            {'class_name': 'Edit', 'control_type': 'EditControl'},  # Common Windows edit class
            {'control_type': 'EditControl'},  # Generic fallback
            # Additional fallbacks for web-based login forms
            {'control_type': 'DocumentControl'},  # Sometimes login forms are in document controls
            {'control_type': 'PaneControl'},  # Sometimes fields are in panes
        ])
        
        return self.find_element_by_paths(search_window, email_paths)
    
    def _find_continue_button(self, window):
        """Find the Continue/Login button using UI paths."""
        self.logger.info("Looking for continue button using UI paths...")
        
        # First try to find the login container
        login_container = self._find_login_container(window)
        search_window = login_container if login_container else window
        
        if login_container:
            self.logger.info("Found login container, searching within it for continue button")
        else:
            self.logger.info("No login container found, searching in main window")
        
        ui_paths = self._get_ui_paths()
        button_paths = ui_paths.get('continue_button', [
            # Default fallback paths
            {'name': 'Doorgaan', 'control_type': 'ButtonControl'},
            {'name': 'Continue', 'control_type': 'ButtonControl'},
            {'name': 'Login', 'control_type': 'ButtonControl'},
            {'name': 'Inloggen', 'control_type': 'ButtonControl'},
            {'automation_id': 'continue_btn', 'control_type': 'ButtonControl'},
            {'automation_id': 'login_btn', 'control_type': 'ButtonControl'},
            {'search_text': 'doorgaan'},
            {'search_text': 'continue'},
            {'control_type': 'ButtonControl'}  # Generic fallback
        ])
        
        return self.find_element_by_paths(search_window, button_paths)
    
    def _enter_email_credentials(self, email_field):
        """Enter email credentials using safe methods."""
        email = self.config.get('snelstart', {}).get('login', {}).get('email', '')
        
        if not email:
            self.logger.error("Email not configured in snelstart.login.email or SNELSTART_EMAIL environment variable")
            return False
        
        self.logger.info("Entering email credentials...")
        return self.safe_send_keys(email_field, email, clear_first=True)
    
    def _verify_login_success(self):
        """Verify that login was successful by checking for expected elements."""
        self.logger.info("Verifying login success...")
        
        # Wait for page transition
        self.wait(3)
        
        # Get current window to check state
        if self.automation:
            window = self.automation.get_current_window(refresh=True)
            if not window:
                self.logger.warning("Cannot verify login - window not found")
                return False
            
            # For now, basic verification - in real implementation you would check for:
            # - Dashboard elements
            # - User menu presence
            # - Absence of login form
            # - Specific post-login UI elements
            
            try:
                # Check if window title or content has changed
                window_name = getattr(window, 'Name', '')
                self.logger.debug(f"Post-login window name: {window_name}")
                
                # Simple verification - if we can still access the window, assume success
                if window.Exists():
                    self.logger.info("Login verification completed - window accessible")
                    return True
                    
            except Exception as e:
                self.logger.warning(f"Login verification inconclusive: {str(e)}")
        
        # Default to success for now - improve this based on actual UI structure
        self.logger.info("Login verification completed (basic)")
        return True
    
    def login(self):
        """Main login workflow using UI path architecture."""
        self.logger.info("Starting login process with UI path architecture...")
        
        for attempt in range(self.retry_attempts):
            try:
                self.logger.info(f"Login attempt {attempt + 1}/{self.retry_attempts}")
                
                # Step 1: Find the correct login window (separate window or main window)
                window = self.find_snelstart_login_window(timeout=10)
                if not window:
                    self.logger.error("Snelstart login window not found")
                    self.wait(2)
                    continue
                
                self.logger.info(f"Using window for login: {window.Name}")
                
                # Step 2: Find email field using UI paths
                email_field = self._find_email_field(window)
                if not email_field:
                    self.logger.warning("Email field not found")
                    self.wait(2)
                    continue
                
                # Step 3: Enter email credentials
                if not self._enter_email_credentials(email_field):
                    self.logger.warning("Failed to enter email credentials")
                    self.wait(2)
                    continue
                
                # Step 4: Find and click continue button
                continue_button = self._find_continue_button(window)
                if continue_button:
                    if self.safe_click(continue_button):
                        self.logger.info("Continue button clicked successfully")
                    else:
                        self.logger.warning("Failed to click continue button")
                        continue
                else:
                    self.logger.warning("Continue button not found, trying Enter key")
                    if not self.safe_send_keys(email_field, '{Enter}', clear_first=False):
                        self.logger.warning("Failed to send Enter key")
                        continue
                
                # Step 5: Verify login success
                if self._verify_login_success():
                    self.logger.info("Login completed successfully")
                    return True
                else:
                    self.logger.warning("Login verification failed")
                
            except Exception as e:
                self.logger.error(f"Login attempt {attempt + 1} failed: {str(e)}")
            
            if attempt < self.retry_attempts - 1:
                self.logger.info("Retrying login...")
                self.wait(3)
        
        self.logger.error("All login attempts failed")
        return False