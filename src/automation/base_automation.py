import platform
import time

# Handle UI automation imports with fallbacks
try:
    import uiautomation as auto
    UI_AUTOMATION_AVAILABLE = True
except ImportError:
    UI_AUTOMATION_AVAILABLE = False

try:
    import pygetwindow as gw
    PYGETWINDOW_AVAILABLE = True
except ImportError:
    PYGETWINDOW_AVAILABLE = False

try:
    import win32gui
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False


class EnvironmentDetector:
    """Detects the current operating environment."""
    
    @staticmethod
    def is_wsl():
        """Check if running in WSL environment."""
        return 'microsoft' in platform.uname().release.lower()


class BaseAutomation:
    """Base class for all automation components."""
    
    def __init__(self, config, logger, automation=None):
        self.config = config
        self.logger = logger
        self.automation = automation  # Reference to main SnelstartAutomation instance
        self.delay = config.get('automation', {}).get('delay', 2.0)
        self.is_wsl = EnvironmentDetector.is_wsl()
    
    def wait(self, seconds=None):
        """Wait for specified time or default delay."""
        wait_time = seconds if seconds is not None else self.delay
        time.sleep(wait_time)
    
    def _build_search_criteria(self, path_config):
        """Build search criteria dictionary from path configuration."""
        search_criteria = {}
        
        if 'automation_id' in path_config:
            search_criteria['AutomationId'] = path_config['automation_id']
        
        if 'name' in path_config:
            search_criteria['Name'] = path_config['name']
        
        if 'class_name' in path_config:
            search_criteria['ClassName'] = path_config['class_name']
        
        return search_criteria
    
    def _get_control_class(self, path_config):
        """Get the appropriate UIAutomation control class from path config."""
        if 'control_type' in path_config:
            return getattr(auto, path_config['control_type'], auto.Control)
        return auto.Control
    
    def _try_text_search_fallback(self, parent_window, path_config):
        """Try to find element by searching children for text content."""
        if 'search_text' not in path_config:
            return None
        
        try:
            children = parent_window.GetChildren()
            search_text = path_config['search_text'].lower()
            
            for child in children:
                name = getattr(child, 'Name', '').lower()
                if search_text in name:
                    self.logger.debug(f"Found element by text search: {path_config}")
                    return child
        except Exception as e:
            self.logger.debug(f"Text search failed: {e}")
        
        return None

    def find_element_by_path(self, parent_window, path_config, timeout=5):
        """
        Find a UI element using path configuration.
        
        Args:
            parent_window: The parent window/control to search in
            path_config: Dictionary with element identifiers (automation_id, name, class_name, etc.)
            timeout: Maximum time to wait for element
            
        Returns:
            UI element if found, None otherwise
        """
        if not UI_AUTOMATION_AVAILABLE:
            self.logger.warning("UI automation not available")
            return None
        
        if not parent_window:
            self.logger.error("Parent window not provided")
            return None
        
        try:
            # Build search criteria and get control class
            search_criteria = self._build_search_criteria(path_config)
            
            # Try primary search using UIAutomation API
            if search_criteria:
                control_class = self._get_control_class(path_config)
                search_criteria['searchDepth'] = 2
                
                element = control_class(**search_criteria)
                if element and element.Exists(maxSearchSeconds=timeout):
                    self.logger.debug(f"Found element using path: {path_config}")
                    return element
            
            # Try fallback text search
            element = self._try_text_search_fallback(parent_window, path_config)
            if element:
                return element
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error finding element by path {path_config}: {str(e)}")
            return None
    
    def find_element_by_paths(self, parent_window, paths_list, timeout=5):
        """
        Try to find element using multiple path configurations (fallback strategy).
        
        Args:
            parent_window: The parent window/control to search in
            paths_list: List of path configurations to try
            timeout: Maximum time to wait for each path
            
        Returns:
            First UI element found, None if none found
        """
        for i, path_config in enumerate(paths_list):
            self.logger.debug(f"Trying path {i+1}/{len(paths_list)}: {path_config}")
            element = self.find_element_by_path(parent_window, path_config, timeout)
            if element:
                self.logger.info(f"Found element using path {i+1}: {path_config}")
                return element
        
        self.logger.warning(f"Element not found using any of {len(paths_list)} paths")
        return None
    
    def wait_for_element(self, parent_window, path_config, timeout=30):
        """
        Wait for an element to appear using path configuration.
        
        Args:
            parent_window: The parent window/control to search in
            path_config: Dictionary with element identifiers
            timeout: Maximum time to wait
            
        Returns:
            UI element if found within timeout, None otherwise
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            element = self.find_element_by_path(parent_window, path_config, timeout=1)
            if element:
                return element
            time.sleep(0.5)
        
        self.logger.warning(f"Element not found within {timeout} seconds: {path_config}")
        return None
    
    def validate_element(self, element, check_enabled=True, check_visible=True):
        """
        Validate that an element is ready for interaction.
        
        Args:
            element: UI element to validate
            check_enabled: Whether to check if element is enabled
            check_visible: Whether to check if element is visible
            
        Returns:
            True if element is valid for interaction, False otherwise
        """
        if not element:
            return False
        
        try:
            if not element.Exists():
                self.logger.warning("Element no longer exists")
                return False
            
            if check_visible and not element.IsVisible:
                self.logger.warning("Element is not visible") 
                return False
            
            if check_enabled and not element.IsEnabled:
                self.logger.warning("Element is not enabled")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating element: {str(e)}")
            return False
    
    def safe_click(self, element, retry_count=3):
        """
        Safely click an element with validation and retry logic.
        
        Args:
            element: UI element to click
            retry_count: Number of retry attempts
            
        Returns:
            True if click succeeded, False otherwise
        """
        for attempt in range(retry_count):
            try:
                if not self.validate_element(element):
                    self.logger.warning(f"Element validation failed on attempt {attempt + 1}")
                    self.wait(1)
                    continue
                
                element.Click()
                self.logger.debug("Element clicked successfully")
                return True
                
            except Exception as e:
                self.logger.warning(f"Click attempt {attempt + 1} failed: {str(e)}")
                if attempt < retry_count - 1:
                    self.wait(1)
        
        self.logger.error("All click attempts failed")
        return False
    
    def safe_send_keys(self, element, text, clear_first=True, retry_count=3):
        """
        Safely send keys to an element with validation and retry logic.
        
        Args:
            element: UI element to send keys to
            text: Text to send
            clear_first: Whether to clear the field first
            retry_count: Number of retry attempts
            
        Returns:
            True if send keys succeeded, False otherwise
        """
        for attempt in range(retry_count):
            try:
                if not self.validate_element(element):
                    self.logger.warning(f"Element validation failed on attempt {attempt + 1}")
                    self.wait(1)
                    continue
                
                # Focus the element
                element.SetFocus()
                self.wait(0.2)
                
                # Clear existing content if requested
                if clear_first:
                    element.SendKeys('{Ctrl}a')
                    self.wait(0.1)
                
                # Send the text
                element.SendKeys(text)
                self.logger.debug(f"Successfully sent keys to element")
                return True
                
            except Exception as e:
                self.logger.warning(f"Send keys attempt {attempt + 1} failed: {str(e)}")
                if attempt < retry_count - 1:
                    self.wait(1)
        
        self.logger.error("All send keys attempts failed")
        return False
    
    def find_window_with_pygetwindow(self, title_pattern, timeout=10):
        """
        Find a window using pygetwindow and convert to UI automation control.
        
        Args:
            title_pattern: String to match window title (exact substring match)
            timeout: Maximum time to wait for window
            
        Returns:
            UI automation WindowControl if found, None otherwise
        """
        if not PYGETWINDOW_AVAILABLE:
            self.logger.warning("pygetwindow not available")
            return None
        
        if not UI_AUTOMATION_AVAILABLE:
            self.logger.warning("UI automation not available")
            return None
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                windows = gw.getAllWindows()
                for window in windows:
                    window_title = window.title
                    
                    # Check if window title contains the pattern string
                    if title_pattern in window_title:
                        return self._convert_pygetwindow_to_uiautomation(window)
                
                self.wait(0.5)
                
            except Exception as e:
                self.logger.debug(f"Error searching for window: {e}")
                self.wait(0.5)
        
        self.logger.warning(f"Window with pattern '{title_pattern}' not found within {timeout} seconds")
        return None
    
    def _convert_pygetwindow_to_uiautomation(self, pyget_window):
        """
        Convert a pygetwindow Window to UI automation WindowControl.
        
        Args:
            pyget_window: pygetwindow Window object
            
        Returns:
            UI automation WindowControl if successful, None otherwise
        """
        if not UI_AUTOMATION_AVAILABLE:
            return None
        
        try:
            # Method 1: Try using window handle if available
            if hasattr(pyget_window, '_hWnd') and WIN32_AVAILABLE:
                hwnd = pyget_window._hWnd
                self.logger.debug(f"Converting window using handle: {hwnd}")
                window_control = auto.WindowControl(searchDepth=1, foundIndex=1)
                
                # Find the window by iterating through top-level windows
                desktop = auto.GetRootControl()
                for child in desktop.GetChildren():
                    try:
                        if hasattr(child, 'NativeWindowHandle') and child.NativeWindowHandle == hwnd:
                            self.logger.debug(f"Found UI automation window: {child.Name}")
                            return child
                    except:
                        continue
            
            # Method 2: Try matching by exact title
            try:
                window_control = auto.WindowControl(searchDepth=1, Name=pyget_window.title)
                if window_control.Exists(maxSearchSeconds=2):
                    self.logger.debug(f"Found window by title: {pyget_window.title}")
                    return window_control
            except Exception as title_error:
                self.logger.debug(f"Title match failed: {title_error}")
            
            # Method 3: Try finding by pattern matching
            try:
                desktop = auto.GetRootControl()
                for child in desktop.GetChildren():
                    try:
                        if child.Name == pyget_window.title:
                            self.logger.debug(f"Found window by iteration: {child.Name}")
                            return child
                    except:
                        continue
            except Exception as iter_error:
                self.logger.debug(f"Iteration match failed: {iter_error}")
            
            self.logger.warning(f"Could not convert pygetwindow to UI automation: {pyget_window.title}")
            return None
            
        except Exception as e:
            self.logger.error(f"Error converting pygetwindow to UI automation: {e}")
            return None
    
    def find_snelstart_login_window(self, timeout=10):
        """
        Find the Snelstart login window using multiple strategies.
        
        Returns:
            UI automation WindowControl for login window, None if not found
        """
        self.logger.info("Searching for Snelstart login window...")
        
        # Strategy 1: Look for separate login window first
        login_patterns = [
            "Inloggen SnelStart 12",
            "Inloggen SnelStart"
        ]
        
        for pattern in login_patterns:
            self.logger.debug(f"Trying login pattern: {pattern}")
            window = self.find_window_with_pygetwindow(pattern, timeout=3)
            if window:
                self.logger.info(f"Found separate login window: {window.Name}")
                return window
        
        # Strategy 2: Look for main window as fallback
        main_patterns = [
            "SnelStart 12"
        ]
        
        for pattern in main_patterns:
            self.logger.debug(f"Trying main window pattern: {pattern}")
            window = self.find_window_with_pygetwindow(pattern, timeout=3)
            if window:
                self.logger.info(f"Found main window as fallback: {window.Name}")
                return window
        
        self.logger.warning("No Snelstart window found")
        return None