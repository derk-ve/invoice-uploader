# Invoice Uploader - Snelstart Automation

## Project Overview

This is a Python automation tool that automates the process of uploading invoices to Snelstart accounting software. The project uses UI automation to launch Snelstart, handle login, upload invoices, match them to transactions, and save results.

## Key Information for Claude

### Project Status
- **Current Phase**: Login handler implementation in progress
- **Working Components**: App launcher, configuration system, logging
- **Next Steps**: Complete login automation, then invoice upload functionality

### Architecture

The project follows a modular architecture with separation of concerns:

```
src/
├── snelstart_automation.py      # Main orchestrator class
└── automation/
    ├── base_automation.py       # Base class with environment detection
    ├── app_launcher.py         # ✅ COMPLETE - Launches Snelstart app
    ├── login_handler.py        # 🔄 IN PROGRESS - UI automation login
    ├── invoice_uploader.py     # ❌ PLACEHOLDER - Invoice upload logic
    ├── transaction_selector.py # ❌ PLACEHOLDER - Transaction selection
    ├── invoice_matcher.py      # ❌ PLACEHOLDER - Invoice matching
    └── result_saver.py         # ❌ PLACEHOLDER - Save automation results
```

### Key Classes and Files

#### Entry Point
- **`main.py`**: Application entry point, loads config, sets up logging, processes invoices

#### Core Orchestration
- **`SnelstartAutomation`** (src/snelstart_automation.py:9): Main workflow orchestrator
  - Manages the complete automation workflow
  - Uses composition pattern with specialized automation classes
  - Process workflow: Launch → Login → Upload → Select → Match → Save

#### Automation Components
- **`BaseAutomation`** (src/automation/base_automation.py:14): Base class for all automation
  - Provides WSL/Windows environment detection
  - Common delay/wait functionality
  - Shared config and logger access

- **`AppLauncher`** (src/automation/app_launcher.py:6): ✅ **COMPLETE** 
  - Cross-platform app launching (WSL + Windows)
  - Path validation and error handling
  - Platform-specific launch methods

- **`LoginHandler`** (src/automation/login_handler.py:20): 🔄 **IN PROGRESS**
  - UI automation using `uiautomation` library
  - Window detection and element finding
  - Email credential entry and form submission
  - Retry logic with configurable attempts

#### Configuration & Utilities
- **`config_manager.py`** (utils/config_manager.py): Configuration management
  - YAML config loading with environment variable override
  - Supports .env files for sensitive data
  - Dot notation config access: `get_config_value(config, 'snelstart.login.email')`

- **`logger.py`** (utils/logger.py): Centralized logging
  - File and console logging
  - Timestamped log files in logs/ directory

### Configuration

#### Main Config (`config/config.yaml`)
```yaml
snelstart:
  app_path: "C:\\Users\\...\\SnelStart.exe"  # Path to Snelstart executable
  login:
    timeout: 30
    retry_attempts: 3

paths:
  invoices: "./invoices"  # Invoice files directory
  logs: "./logs"         # Log files directory

automation:
  delay: 2.0  # Default delay between actions
```

#### Environment Variables (via .env file)
- `SNELSTART_EMAIL`: Login email address
- `SNELSTART_PASSWORD`: Login password (not yet used)
- `SNELSTART_TIMEOUT`: Login timeout override
- `SNELSTART_RETRY_ATTEMPTS`: Retry attempts override

### Dependencies

#### Core Dependencies (pyproject.toml)
- `pillow>=11.2.1`: Image processing
- `pyautogui>=0.9.54`: Screen automation
- `pyyaml>=6.0.2`: Configuration file parsing
- `python-dotenv>=1.0.0`: Environment variable loading

#### Additional Dependencies (requirements.txt)
- `pywin32`: Windows-specific automation
- `uiautomation`: Windows UI element automation
- `pygetwindow`: Window management

### Environment Detection

The project detects WSL vs Windows environments:
- **WSL Detection**: `'microsoft' in platform.uname().release.lower()` (base_automation.py:11)
- **Launch Method**: WSL uses `cmd.exe /c start` while Windows uses direct execution
- **Cross-Platform**: All automation components inherit WSL/Windows awareness

### Current Implementation Status

#### ✅ Completed
1. **Project Structure**: Modular architecture with clear separation
2. **Configuration System**: YAML + environment variable support
3. **Logging**: File and console logging with timestamps  
4. **App Launcher**: Full cross-platform Snelstart launching
5. **Base Infrastructure**: Environment detection, common utilities

#### 🔄 In Progress  
1. **Login Handler**: UI automation partially implemented
   - Window detection ✅
   - Email field finding ✅
   - Credential entry ✅
   - Button clicking ✅
   - Success verification ❓ (basic implementation)

#### ❌ To Do
1. **Password Entry**: Currently only handles email, needs password field support
2. **Invoice Upload**: File upload automation
3. **Transaction Selection**: Navigate and select transactions
4. **Invoice Matching**: Match uploaded invoices to selected transactions
5. **Result Saving**: Save automation results and verify completion

### Development Guidelines

#### Code Patterns
- All automation classes inherit from `BaseAutomation`
- Use dependency injection (config, logger passed to constructors)
- Implement retry logic with configurable attempts
- Log all significant actions and errors
- Handle both WSL and Windows environments

#### Error Handling
- Graceful degradation when UI automation libraries unavailable
- Comprehensive exception handling with logging
- Retry mechanisms for unreliable operations
- Clear error messages for debugging

#### Testing Commands
Run from project root:
```bash
python main.py  # Process first invoice in invoices/ directory
```

### Next Development Steps

1. **Complete Login Handler**: 
   - Add password field detection and entry
   - Improve login success verification
   - Handle multi-step login flows

2. **Implement Invoice Upload**:
   - File dialog automation
   - File selection and upload
   - Upload progress monitoring

3. **Add Transaction Selection**:
   - Navigate transaction lists
   - Transaction filtering/search
   - Selection automation

4. **Build Invoice Matching**:
   - Compare invoice data to transactions
   - Automated matching logic
   - Manual matching fallback

5. **Result Saving**:
   - Verify successful processing
   - Save transaction results
   - Generate completion reports

### File Locations for Common Tasks

- **Configuration changes**: `config/config.yaml`
- **Environment setup**: `.env` file (create in project root)
- **Main workflow**: `src/snelstart_automation.py:24` (`process_single_invoice`)
- **App launching**: `src/automation/app_launcher.py:48` (`launch_snelstart`)
- **Login logic**: `src/automation/login_handler.py:173` (`login`)
- **Logging setup**: `utils/logger.py:7` (`setup_logger`)
- **Config loading**: `utils/config_manager.py:13` (`load_config`)

### Debugging Tips

- **Logs**: Check `logs/` directory for detailed execution logs
- **UI Automation**: LoginHandler logs window/element detection details
- **Environment**: BaseAutomation logs WSL vs Windows detection
- **Configuration**: config_manager logs environment variable loading

This project is designed for defensive automation purposes to help with legitimate business accounting workflows.