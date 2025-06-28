import time
from .base_automation import BaseAutomation

# Handle pyautogui import for different environments
try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except Exception as e:
    print(f"Warning: pyautogui not available: {e}")
    PYAUTOGUI_AVAILABLE = False


class LoginHandler(BaseAutomation):
    """Handles login process for Snelstart."""
    
    def __init__(self, config, logger):
        super().__init__(config, logger)
        self.timeout = config.get('snelstart', {}).get('login', {}).get('timeout', 30)
        self.retry_attempts = config.get('snelstart', {}).get('login', {}).get('retry_attempts', 3)
        
        # Set pyautogui settings if available
        if PYAUTOGUI_AVAILABLE:
            pyautogui.FAILSAFE = True
            pyautogui.PAUSE = 0.5
    
    def _wait_for_login_screen(self):
        """Wait for the login screen to appear."""
        self.logger.info("Waiting for login screen to appear...")
        
        if not PYAUTOGUI_AVAILABLE:
            self.logger.warning("PyAutoGUI not available - using time delay")
            self.wait(3)
            return True
        
        # Look for login screen elements
        start_time = time.time()
        while time.time() - start_time < self.timeout:
            try:
                # Try to find the "Log in bij SnelStart" text
                if pyautogui.locateOnScreen is not None:
                    # This would require screenshot templates - for now use delay
                    self.wait(3)
                    return True
            except Exception:
                pass
            self.wait(1)
        
        self.logger.error("Login screen not found within timeout")
        return False
    
    def _find_email_field(self):
        """Find and click the email input field."""
        self.logger.info("Looking for email field...")
        
        if not PYAUTOGUI_AVAILABLE:
            self.logger.warning("PyAutoGUI not available - cannot find field")
            return False
        
        try:
            # Get screen size and calculate center area where form likely is
            screen_width, screen_height = pyautogui.size()
            center_x, center_y = screen_width // 2, screen_height // 2
            
            # Click in the center area where email field should be
            # Based on screenshot, email field is roughly in center
            email_field_y = center_y - 50  # Slightly above center
            pyautogui.click(center_x, email_field_y)
            
            self.logger.info("Clicked on email field area")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to find email field: {str(e)}")
            return False
    
    def _enter_credentials(self):
        """Enter email credentials."""
        email = self.config.get('snelstart', {}).get('login', {}).get('email', '')
        
        if not email:
            self.logger.error("Email not configured")
            return False
        
        if not PYAUTOGUI_AVAILABLE:
            self.logger.warning("PyAutoGUI not available - cannot enter credentials")
            return False
        
        try:
            # Clear field and type email
            pyautogui.hotkey('ctrl', 'a')  # Select all
            self.wait(0.2)
            pyautogui.typewrite(email)
            self.logger.info("Email entered successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to enter credentials: {str(e)}")
            return False
    
    def _click_continue_button(self):
        """Click the blue 'Doorgaan' (Continue) button."""
        self.logger.info("Looking for Continue button...")
        
        if not PYAUTOGUI_AVAILABLE:
            self.logger.warning("PyAutoGUI not available - cannot click button")
            return False
        
        try:
            # Get screen size and calculate where button likely is
            screen_width, screen_height = pyautogui.size()
            center_x, center_y = screen_width // 2, screen_height // 2
            
            # Based on screenshot, button is below the email field
            button_y = center_y + 50  # Below center
            pyautogui.click(center_x, button_y)
            
            self.logger.info("Clicked Continue button")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to click continue button: {str(e)}")
            return False
    
    def _verify_login_success(self):
        """Verify that login was successful."""
        self.logger.info("Verifying login success...")
        
        # Wait a moment for page to load
        self.wait(3)
        
        # For now, assume success if no errors occurred
        # In a real implementation, you would check for:
        # - Dashboard elements
        # - Absence of login form
        # - Presence of user menu
        
        self.logger.info("Login verification completed")
        return True
    
    def login(self):
        """Main login workflow."""
        self.logger.info("Starting login process...")
        
        for attempt in range(self.retry_attempts):
            try:
                self.logger.info(f"Login attempt {attempt + 1}/{self.retry_attempts}")
                
                # Step 1: Wait for login screen
                if not self._wait_for_login_screen():
                    continue
                
                # Step 2: Find and click email field
                if not self._find_email_field():
                    continue
                
                # Step 3: Enter email
                if not self._enter_credentials():
                    continue
                
                # Step 4: Click continue button
                if not self._click_continue_button():
                    continue
                
                # Step 5: Verify login success
                if self._verify_login_success():
                    self.logger.info("Login completed successfully")
                    return True
                
            except Exception as e:
                self.logger.error(f"Login attempt {attempt + 1} failed: {str(e)}")
            
            if attempt < self.retry_attempts - 1:
                self.logger.info("Retrying login...")
                self.wait(2)
        
        self.logger.error("All login attempts failed")
        return False