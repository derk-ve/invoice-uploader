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
                patterns = ["*Inloggen*", "*SnelStart*"]
                for pattern in patterns:
                    try:
                        # Use WindowControl to find by pattern
                        window = auto.WindowControl(searchDepth=1, Name=pattern)
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
                        print(f"Pattern {pattern} failed: {pattern_error}")
                        
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
        
        # Find the login window specifically
        login_window = None
        try:
            # Try to find login window first (prioritize "Inloggen")
            patterns_to_try = ["*Inloggen*", "*SnelStart*"]
            
            for pattern in patterns_to_try:
                print(f"Trying to find window with pattern: {pattern}")
                window = auto.WindowControl(searchDepth=1, Name=pattern)
                if window.Exists(maxSearchSeconds=3):
                    print(f"Found window: {window.Name}")
                    if "Inloggen" in window.Name:
                        login_window = window
                        print(f"Using login window: {window.Name}")
                        break
                    elif login_window is None:  # Use as fallback if no login window found
                        login_window = window
                        print(f"Using fallback window: {window.Name}")
            
            if not login_window:
                print("No suitable window found for element inspection")
                return elements
            
        except Exception as e:
            print(f"Error finding login window: {e}")
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
        """Generate a detailed inspection report."""
        report = []
        report.append("=== SNELSTART UI INSPECTION REPORT ===\\n")
        
        # Windows found
        report.append("WINDOWS FOUND:")
        if self.snelstart_windows:
            for i, window in enumerate(self.snelstart_windows):
                report.append(f"  {i+1}. Method: {window['method']}")
                report.append(f"     Title: {window['title']}")
                if 'automation_id' in window:
                    report.append(f"     AutomationId: {window['automation_id']}")
                    report.append(f"     ClassName: {window['class_name']}")
                    report.append(f"     ControlType: {window['control_type']}")
                report.append("")
        else:
            report.append("  No SnelStart windows found")
        
        report.append("\\nELEMENTS FOUND:")
        if self.elements_found:
            for i, element in enumerate(self.elements_found):
                indent = "  " + ("  " * element.get('depth', 0))
                report.append(f"{indent}{i+1}. Type: {element['type']}")
                if element.get('window'):
                    report.append(f"{indent}   Window: {element['window']}")
                if element.get('index') is not None:
                    report.append(f"{indent}   Index: {element['index']}")
                if element['name']:
                    report.append(f"{indent}   Name: '{element['name']}'")
                if element['automation_id']:
                    report.append(f"{indent}   AutomationId: '{element['automation_id']}'")
                if element['class_name']:
                    report.append(f"{indent}   ClassName: '{element['class_name']}'")
                if element['value']:
                    report.append(f"{indent}   Value: '{element['value']}'")
                if element.get('is_enabled') is not None:
                    report.append(f"{indent}   Enabled: {element['is_enabled']}")
                if element.get('is_visible') is not None:
                    report.append(f"{indent}   Visible: {element['is_visible']}")
                if element.get('depth') is not None:
                    report.append(f"{indent}   Depth: {element['depth']}")
                report.append(f"{indent}   Description: {element['description']}")
                report.append("")
        else:
            report.append("  No UI elements found")
        
        return "\\n".join(report)
    
    def save_report(self, filename="ui_inspection_report.txt"):
        """Save the inspection report to a file."""
        report = self.generate_report()
        
        # Save to logs directory
        logs_dir = Path(__file__).parent.parent / "logs"
        logs_dir.mkdir(exist_ok=True)
        
        report_path = logs_dir / filename
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"Report saved to: {report_path}")
        return report_path


def main():
    """Main inspection function."""
    print("SnelStart UI Inspector")
    print("====================")
    print("Please make sure SnelStart is running and the login screen is visible.")
    print("Press Enter to start inspection...")
    input()
    
    inspector = UIInspector()
    
    print("\\n1. Finding SnelStart windows...")
    windows = inspector.find_snelstart_windows()
    print(f"Found {len(windows)} SnelStart windows")
    
    print("\\n2. Inspecting login elements...")
    elements = inspector.inspect_login_elements()
    print(f"Found {len(elements)} UI elements")
    
    print("\\n3. Generating report...")
    report = inspector.generate_report()
    print(report)
    
    print("\\n4. Saving detailed report...")
    report_path = inspector.save_report()
    
    print("\\nInspection complete!")
    print(f"Check the report at: {report_path}")
    print("\\nUse this information to improve element detection in login_handler.py")


if __name__ == "__main__":
    main()