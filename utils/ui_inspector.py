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
        """Find all Snelstart windows."""
        windows = []
        
        if PYGETWINDOW_AVAILABLE:
            try:
                # Look for windows with "SnelStart" in the title
                snelstart_windows = gw.getWindowsWithTitle("SnelStart")
                for window in snelstart_windows:
                    windows.append({
                        'method': 'pygetwindow',
                        'title': window.title,
                        'left': window.left,
                        'top': window.top,
                        'width': window.width,
                        'height': window.height
                    })
            except Exception as e:
                print(f"Error with pygetwindow: {e}")
        
        if UI_AUTOMATION_AVAILABLE:
            try:
                # Use UI Automation to find windows
                windows_found = auto.FindWindows(searchDepth=1, Name="*SnelStart*")
                for window in windows_found:
                    if window.Name:
                        windows.append({
                            'method': 'uiautomation',
                            'title': window.Name,
                            'automation_id': getattr(window, 'AutomationId', 'N/A'),
                            'class_name': getattr(window, 'ClassName', 'N/A'),
                            'control_type': getattr(window, 'ControlTypeName', 'N/A')
                        })
            except Exception as e:
                print(f"Error with uiautomation: {e}")
        
        self.snelstart_windows = windows
        return windows
    
    def inspect_login_elements(self):
        """Inspect elements that might be related to login."""
        elements = []
        
        if not UI_AUTOMATION_AVAILABLE:
            print("UI Automation not available - cannot inspect elements")
            return elements
        
        try:
            # Find main SnelStart window
            window = auto.WindowControl(searchDepth=1, Name="*SnelStart*")
            if not window.Exists(maxSearchSeconds=5):
                print("SnelStart window not found")
                return elements
            
            print(f"Found SnelStart window: {window.Name}")
            
            # Look for common login elements
            login_patterns = [
                # Text input fields
                {'control_type': 'EditControl', 'description': 'Text input fields'},
                {'control_type': 'TextControl', 'description': 'Text labels'},
                {'control_type': 'ButtonControl', 'description': 'Buttons'},
                # Web-based elements if it's a browser control
                {'control_type': 'DocumentControl', 'description': 'Web document'},
                {'control_type': 'PaneControl', 'description': 'Container panes'},
            ]
            
            for pattern in login_patterns:
                try:
                    controls = window.GetChildren()
                    for control in controls:
                        if hasattr(control, 'ControlTypeName') and pattern['control_type'] in control.ControlTypeName:
                            element_info = {
                                'type': control.ControlTypeName,
                                'name': getattr(control, 'Name', ''),
                                'automation_id': getattr(control, 'AutomationId', ''),
                                'class_name': getattr(control, 'ClassName', ''),
                                'value': getattr(control, 'Value', ''),
                                'help_text': getattr(control, 'HelpText', ''),
                                'description': pattern['description']
                            }
                            elements.append(element_info)
                            
                            # If it's a pane or document, look deeper
                            if 'Pane' in control.ControlTypeName or 'Document' in control.ControlTypeName:
                                self._inspect_children(control, elements, depth=1, max_depth=3)
                                
                except Exception as e:
                    print(f"Error inspecting {pattern['control_type']}: {e}")
            
        except Exception as e:
            print(f"Error during element inspection: {e}")
        
        self.elements_found = elements
        return elements
    
    def _inspect_children(self, parent_control, elements_list, depth=0, max_depth=3):
        """Recursively inspect child elements."""
        if depth >= max_depth:
            return
        
        try:
            children = parent_control.GetChildren()
            for child in children:
                if hasattr(child, 'ControlTypeName'):
                    element_info = {
                        'type': child.ControlTypeName,
                        'name': getattr(child, 'Name', ''),
                        'automation_id': getattr(child, 'AutomationId', ''),
                        'class_name': getattr(child, 'ClassName', ''),
                        'value': getattr(child, 'Value', ''),
                        'help_text': getattr(child, 'HelpText', ''),
                        'depth': depth + 1,
                        'description': f'Child element (depth {depth + 1})'
                    }
                    elements_list.append(element_info)
                    
                    # Continue recursing if it might contain more elements
                    if any(term in child.ControlTypeName for term in ['Pane', 'Document', 'Group']):
                        self._inspect_children(child, elements_list, depth + 1, max_depth)
                        
        except Exception as e:
            print(f"Error inspecting children at depth {depth}: {e}")
    
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
                report.append(f"  {i+1}. Type: {element['type']}")
                if element['name']:
                    report.append(f"     Name: '{element['name']}'")
                if element['automation_id']:
                    report.append(f"     AutomationId: '{element['automation_id']}'")
                if element['class_name']:
                    report.append(f"     ClassName: '{element['class_name']}'")
                if element['value']:
                    report.append(f"     Value: '{element['value']}'")
                if element.get('depth'):
                    report.append(f"     Depth: {element['depth']}")
                report.append(f"     Description: {element['description']}")
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