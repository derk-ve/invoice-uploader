"""
UI Element Inspector Utility

This utility helps inspect Snelstart's UI elements to find reliable automation paths.
Run this script while Snelstart is open to discover element identifiers.
"""

import time
from pathlib import Path

# Handle imports with fallbacks for different environments
try:
    import uiautomation as auto
    UI_AUTOMATION_AVAILABLE = True
except ImportError:
    print("Warning: uiautomation not available")
    UI_AUTOMATION_AVAILABLE = False

try:
    import pygetwindow as gw
    PYGETWINDOW_AVAILABLE = True
except ImportError:
    print("Warning: pygetwindow not available")
    PYGETWINDOW_AVAILABLE = False

try:
    import win32gui
    import win32con
    WIN32_AVAILABLE = True
except ImportError:
    print("Warning: pywin32 not available")
    WIN32_AVAILABLE = False


class UIInspector:
    """Utility class to inspect and analyze UI elements."""
    
    def __init__(self):
        self.snelstart_windows = []
        self.elements_found = []
    
    def find_snelstart_windows(self):
        """Find all Snelstart windows, prioritizing login window."""
        windows = []
        
        if PYGETWINDOW_AVAILABLE:
            try:
                # Look for both login and main windows
                all_windows = gw.getAllWindows()
                for window in all_windows:
                    if "SnelStart" in window.title or "Inloggen" in window.title:
                        window_info = {
                            'method': 'pygetwindow',
                            'title': window.title,
                            'left': window.left,
                            'top': window.top,
                            'width': window.width,
                            'height': window.height,
                            'is_login_window': 'Inloggen' in window.title
                        }
                        windows.append(window_info)
                        print(f"Found window: {window.title}")
            except Exception as e:
                print(f"Error with pygetwindow: {e}")
        
        if UI_AUTOMATION_AVAILABLE:
            try:
                # Find windows using UI Automation - try different patterns
                patterns = [
                    lambda name: 'Inloggen' in name,
                    lambda name: 'SnelStart' in name
                ]
                for i, pattern_func in enumerate(patterns):
                    try:
                        # Use WindowControl to find by pattern
                        window = auto.WindowControl(searchDepth=1, Name=pattern_func)
                        if window.Exists(maxSearchSeconds=2):
                            windows.append({
                                'method': 'uiautomation',
                                'title': window.Name,
                                'automation_id': getattr(window, 'AutomationId', 'N/A'),
                                'class_name': getattr(window, 'ClassName', 'N/A'),
                                'control_type': getattr(window, 'ControlTypeName', 'N/A'),
                                'is_login_window': 'Inloggen' in window.Name
                            })
                            print(f"Found UI Automation window: {window.Name}")
                    except Exception as pattern_error:
                        print(f"Pattern {i+1} failed: {pattern_error}")
                        
            except Exception as e:
                print(f"Error with uiautomation: {e}")
        
        # Sort windows to prioritize login window
        windows.sort(key=lambda x: x.get('is_login_window', False), reverse=True)
        
        self.snelstart_windows = windows
        return windows
    
    def inspect_login_elements(self):
        """Inspect elements in the login window specifically."""
        elements = []
        
        if not UI_AUTOMATION_AVAILABLE:
            print("UI Automation not available - cannot inspect elements")
            return elements
        
        # Find the login window specifically using information from pygetwindow
        login_window = None
        
        # First, get window titles found by pygetwindow to use as exact matches
        found_titles = []
        for window_info in self.snelstart_windows:
            if window_info.get('method') == 'pygetwindow':
                found_titles.append(window_info['title'])
        
        print(f"Titles found by pygetwindow: {found_titles}")
        
        # Debug: Show what UI automation can see
        print("\nDEBUG: Checking what UI automation can find...")
        try:
            # Try to enumerate all top-level windows that UI automation can see
            desktop = auto.GetRootControl()
            all_windows = desktop.GetChildren()
            print(f"UI automation sees {len(all_windows)} top-level windows:")
            
            for i, win in enumerate(all_windows[:10]):  # Show first 10 to avoid spam
                try:
                    win_name = getattr(win, 'Name', 'No name')
                    win_class = getattr(win, 'ClassName', 'No class')
                    if "SnelStart" in win_name or "Inloggen" in win_name or win_name:
                        print(f"  {i+1}. Name: '{win_name}', Class: '{win_class}'")
                except:
                    pass
        except Exception as debug_error:
            print(f"Debug enumeration failed: {debug_error}")
        
        try:
            # Try exact window titles first
            titles_to_try = []
            
            # Prioritize login window title
            for title in found_titles:
                if "Inloggen" in title:
                    titles_to_try.insert(0, title)  # Insert at beginning for priority
                else:
                    titles_to_try.append(title)
            
            # Also try pattern matching as fallback
            patterns_to_try = [
                lambda name: 'Inloggen' in name,
                lambda name: 'SnelStart' in name,
                "Inloggen SnelStart 12", 
                "SnelStart 12"
            ]
            
            # Combine exact titles and patterns
            all_attempts = titles_to_try + patterns_to_try
            
            print(f"Will try {len(all_attempts)} window identifiers")
            
            for i, attempt in enumerate(all_attempts):
                attempt_desc = f"Lambda function {i+1}" if callable(attempt) else f"'{attempt}'"
                print(f"Trying to find window: {attempt_desc}")
                try:
                    window = auto.WindowControl(searchDepth=1, Name=attempt)
                    if window.Exists(maxSearchSeconds=2):
                        print(f"SUCCESS: Found window with {attempt_desc}: {window.Name}")
                        # Prioritize login window
                        if "Inloggen" in window.Name:
                            login_window = window
                            print(f"Using login window: {window.Name}")
                            break
                        elif login_window is None:  # Use as fallback
                            login_window = window
                            print(f"Using fallback window: {window.Name}")
                    else:
                        print(f"Window with {attempt_desc} does not exist")
                except Exception as attempt_error:
                    print(f"Error trying {attempt_desc}: {attempt_error}")
            
            # If still no window found, try alternative approaches
            if not login_window:
                print("\nTrying alternative approaches...")
                
                # Try using different search criteria
                alternative_attempts = [
                    {"ClassName": "Window", "Name": lambda name: 'Inloggen' in name},
                    {"Name": "Inloggen SnelStart 12"},
                    {"Name": lambda name: name.startswith('Inloggen')},
                ]
                
                for criteria in alternative_attempts:
                    try:
                        print(f"Trying criteria: {criteria}")
                        window = auto.WindowControl(searchDepth=1, **criteria)
                        if window.Exists(maxSearchSeconds=1):
                            login_window = window
                            print(f"SUCCESS with alternative approach: {window.Name}")
                            break
                    except Exception as alt_error:
                        print(f"Alternative approach failed: {alt_error}")
            
            if not login_window:
                print("FAILED: No suitable window found for element inspection")
                print("This may be due to UI automation permissions or window access restrictions")
                return elements
            
        except Exception as e:
            print(f"Error during window finding process: {e}")
            return elements
        
        # Inspect elements in the login window
        try:
            print(f"Inspecting elements in window: {login_window.Name}")
            
            # Get all children and inspect them
            print("Getting window children...")
            children = login_window.GetChildren()
            print(f"Found {len(children)} direct children")
            
            for i, control in enumerate(children):
                try:
                    element_info = {
                        'window': login_window.Name,
                        'index': i,
                        'type': getattr(control, 'ControlTypeName', 'Unknown'),
                        'name': getattr(control, 'Name', ''),
                        'automation_id': getattr(control, 'AutomationId', ''),
                        'class_name': getattr(control, 'ClassName', ''),
                        'value': getattr(control, 'Value', ''),
                        'help_text': getattr(control, 'HelpText', ''),
                        'is_enabled': getattr(control, 'IsEnabled', False),
                        'is_visible': getattr(control, 'IsVisible', False),
                        'depth': 0,
                        'description': f'Direct child {i+1}'
                    }
                    elements.append(element_info)
                    print(f"Found element {i+1}: {element_info['type']} - {element_info['name']}")
                    
                    # If it's a container, look deeper
                    if element_info['type'] in ['PaneControl', 'GroupControl', 'DocumentControl', 'CustomControl']:
                        self._inspect_children_recursive(control, elements, depth=1, max_depth=4, parent_index=i)
                        
                except Exception as control_error:
                    print(f"Error inspecting control {i}: {control_error}")
                    elements.append({
                        'window': login_window.Name,
                        'index': i,
                        'type': 'ERROR',
                        'name': f'Error accessing control: {str(control_error)}',
                        'depth': 0,
                        'description': f'Failed to access child {i+1}'
                    })
            
        except Exception as e:
            print(f"Error during element inspection: {e}")
            elements.append({
                'window': getattr(login_window, 'Name', 'Unknown'),
                'type': 'ERROR',
                'name': f'Inspection failed: {str(e)}',
                'depth': 0,
                'description': 'Window inspection error'
            })
        
        self.elements_found = elements
        return elements
    
    def _inspect_children_recursive(self, parent_control, elements_list, depth=0, max_depth=3, parent_index=0):
        """Recursively inspect child elements with improved error handling."""
        if depth >= max_depth:
            return
        
        try:
            children = parent_control.GetChildren()
            print(f"  {'  ' * depth}Found {len(children)} children at depth {depth}")
            
            for i, child in enumerate(children):
                try:
                    element_info = {
                        'window': 'Child Element',
                        'index': f"{parent_index}.{i}",
                        'type': getattr(child, 'ControlTypeName', 'Unknown'),
                        'name': getattr(child, 'Name', ''),
                        'automation_id': getattr(child, 'AutomationId', ''),
                        'class_name': getattr(child, 'ClassName', ''),
                        'value': getattr(child, 'Value', ''),
                        'help_text': getattr(child, 'HelpText', ''),
                        'is_enabled': getattr(child, 'IsEnabled', False),
                        'is_visible': getattr(child, 'IsVisible', False),
                        'depth': depth,
                        'description': f'Child element (depth {depth})'
                    }
                    elements_list.append(element_info)
                    print(f"  {'  ' * depth}Child {i+1}: {element_info['type']} - {element_info['name']}")
                    
                    # Continue recursing for containers
                    if element_info['type'] in ['PaneControl', 'GroupControl', 'DocumentControl', 'CustomControl'] and depth < max_depth - 1:
                        self._inspect_children_recursive(child, elements_list, depth + 1, max_depth, f"{parent_index}.{i}")
                        
                except Exception as child_error:
                    print(f"  {'  ' * depth}Error accessing child {i}: {child_error}")
                    elements_list.append({
                        'window': 'Child Element',
                        'index': f"{parent_index}.{i}",
                        'type': 'ERROR',
                        'name': f'Error: {str(child_error)}',
                        'depth': depth,
                        'description': f'Failed child at depth {depth}'
                    })
                    
        except Exception as e:
            print(f"  {'  ' * depth}Error getting children at depth {depth}: {e}")
    
    def generate_report(self):
        """Generate a comprehensive inspection report."""
        report = []
        
        report.append("=== SNELSTART UI INSPECTION REPORT ===")
        report.append("")
        
        # Window information
        report.append("WINDOWS FOUND:")
        if self.snelstart_windows:
            for i, window in enumerate(self.snelstart_windows, 1):
                report.append(f"  {i}. Method: {window['method']}")
                report.append(f"     Title: {window['title']}")
                if window.get('automation_id'):
                    report.append(f"     AutomationId: {window['automation_id']}")
                if window.get('class_name'):
                    report.append(f"     ClassName: {window['class_name']}")
                if window.get('control_type'):
                    report.append(f"     ControlType: {window['control_type']}")
                report.append("")
        else:
            report.append("  No SnelStart windows found")
        
        report.append("=== UI STRUCTURE FOR PATH DEFINITIONS ===")
        report.append("")
        
        # Create a hierarchical structure view
        if self.elements_found:
            # Group elements by depth for clearer structure
            depth_groups = {}
            for element in self.elements_found:
                depth = element.get('depth', 0)
                if depth not in depth_groups:
                    depth_groups[depth] = []
                depth_groups[depth].append(element)
            
            # Generate hierarchical structure
            for depth in sorted(depth_groups.keys()):
                if depth == 0:
                    report.append("MAIN WINDOW STRUCTURE:")
                else:
                    report.append(f"DEPTH {depth} ELEMENTS:")
                
                for element in depth_groups[depth]:
                    indent = "  " + ("  " * depth)
                    
                    # Create a clear identifier line
                    identifier_parts = []
                    if element.get('name'):
                        identifier_parts.append(f"Name: '{element['name']}'")
                    if element.get('automation_id'):
                        identifier_parts.append(f"AutomationId: '{element['automation_id']}'")
                    if element.get('class_name'):
                        identifier_parts.append(f"Class: '{element['class_name']}'")
                    
                    identifier = " | ".join(identifier_parts) if identifier_parts else "No identifiers"
                    
                    report.append(f"{indent}[{element['type']}] {identifier}")
                    
                    # Add status info
                    status_info = []
                    if element.get('is_enabled') is not None:
                        status_info.append(f"Enabled: {element['is_enabled']}")
                    if element.get('is_visible') is not None:
                        status_info.append(f"Visible: {element['is_visible']}")
                    if element.get('value'):
                        status_info.append(f"Value: '{element['value']}'")
                    
                    if status_info:
                        report.append(f"{indent}  ({' | '.join(status_info)})")
                    
                    report.append("")
        else:
            report.append("  No UI elements found")
        
        # Add UI path suggestions
        report.append("=== SUGGESTED UI PATHS FOR AUTOMATION ===")
        report.append("")
        
        # Look for login-relevant elements
        login_elements = []
        button_elements = []
        input_elements = []
        
        for element in self.elements_found:
            element_type = element.get('type', '').lower()
            element_name = element.get('name', '').lower()
            automation_id = element.get('automation_id', '').lower()
            
            # Categorize elements that might be useful for login
            if 'edit' in element_type or 'text' in element_type:
                if any(keyword in element_name or keyword in automation_id 
                       for keyword in ['email', 'user', 'login', 'gebruiker']):
                    input_elements.append(element)
            elif 'button' in element_type:
                if any(keyword in element_name or keyword in automation_id 
                       for keyword in ['login', 'continue', 'doorgaan', 'inloggen']):
                    button_elements.append(element)
            elif element.get('automation_id') == 'WebAuthentication':
                login_elements.append(element)
        
        if login_elements:
            report.append("LOGIN CONTAINER ELEMENTS:")
            for element in login_elements:
                report.append(f"  - {element['type']} with AutomationId: '{element['automation_id']}'")
            report.append("")
        
        if input_elements:
            report.append("POTENTIAL INPUT FIELDS:")
            for element in input_elements:
                identifiers = []
                if element.get('name'):
                    identifiers.append(f"Name: '{element['name']}'")
                if element.get('automation_id'):
                    identifiers.append(f"AutomationId: '{element['automation_id']}'")
                if element.get('class_name'):
                    identifiers.append(f"Class: '{element['class_name']}'")
                report.append(f"  - {element['type']} | {' | '.join(identifiers)}")
            report.append("")
        
        if button_elements:
            report.append("POTENTIAL ACTION BUTTONS:")
            for element in button_elements:
                identifiers = []
                if element.get('name'):
                    identifiers.append(f"Name: '{element['name']}'")
                if element.get('automation_id'):
                    identifiers.append(f"AutomationId: '{element['automation_id']}'")
                if element.get('class_name'):
                    identifiers.append(f"Class: '{element['class_name']}'")
                report.append(f"  - {element['type']} | {' | '.join(identifiers)}")
            report.append("")
        
        # Add configuration template
        report.append("=== CONFIGURATION TEMPLATE ===")
        report.append("")
        report.append("Add this to your config.yaml under snelstart.ui_paths.login:")
        report.append("")
        report.append("login_container:")
        if login_elements:
            element = login_elements[0]
            if element.get('automation_id'):
                report.append(f"  - automation_id: '{element['automation_id']}'")
                report.append(f"    control_type: '{element['type']}'")
        
        report.append("")
        report.append("email_field:")
        if input_elements:
            for element in input_elements[:2]:  # Show top 2 candidates
                report.append(f"  - # Option: {element['type']}")
                if element.get('name'):
                    report.append(f"    name: '{element['name']}'")
                if element.get('automation_id'):
                    report.append(f"    automation_id: '{element['automation_id']}'")
                if element.get('class_name'):
                    report.append(f"    class_name: '{element['class_name']}'")
                report.append(f"    control_type: '{element['type']}'")
        
        report.append("")
        report.append("continue_button:")
        if button_elements:
            for element in button_elements[:2]:  # Show top 2 candidates
                report.append(f"  - # Option: {element['type']}")
                if element.get('name'):
                    report.append(f"    name: '{element['name']}'")
                if element.get('automation_id'):
                    report.append(f"    automation_id: '{element['automation_id']}'")
                if element.get('class_name'):
                    report.append(f"    class_name: '{element['class_name']}'")
                report.append(f"    control_type: '{element['type']}'")
        
        return "\n".join(report)
    
    def save_report(self, filename="ui_inspection_report.txt"):
        """Save the inspection report to a file."""
        report = self.generate_report()
        
        # Save to logs directory
        logs_dir = Path(__file__).parent.parent / "logs"
        logs_dir.mkdir(exist_ok=True)
        
        report_path = logs_dir / filename
        with open(report_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(report)
        
        print(f"Report saved to: {report_path}")
        return report_path
    
    def print_report(self):
        """Print the report to console with proper formatting."""
        report = self.generate_report()
        print(report)


def main():
    """Main inspection function."""
    print("SnelStart UI Inspector")
    print("====================")
    print("Please make sure SnelStart is running and the login screen is visible.")
    print("Press Enter to start inspection...")
    input()
    
    inspector = UIInspector()
    
    print("\n1. Finding SnelStart windows...")
    windows = inspector.find_snelstart_windows()
    print(f"Found {len(windows)} SnelStart windows")
    
    print("\n2. Inspecting login elements...")
    elements = inspector.inspect_login_elements()
    print(f"Found {len(elements)} UI elements")
    
    print("\n3. Generating and displaying report...")
    inspector.print_report()
    
    print("\n4. Saving detailed report...")
    report_path = inspector.save_report()
    
    print("\nInspection complete!")
    print(f"Check the report at: {report_path}")
    print("\nUse this information to improve element detection in login_handler.py")


if __name__ == "__main__":
    main()