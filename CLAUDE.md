# CLAUDE Development Guidelines for UNIBOS

## 🎯 Purpose
This document defines the rules and guidelines Claude should follow when working on the UNIBOS project. These guidelines ensure consistency, quality, and proper documentation across all development sessions.

---

## 📝 Development Logging

### Every Session Must:
1. **Log all significant changes** to `DEVELOPMENT_LOG.md`
2. **Use the format**: `[YYYY-MM-DD HH:MM] Category: Title`
3. **Include details**: What was done, why, and the result
4. **Update immediately** after completing each feature/fix

### Log Categories:
- **Version Manager**: Version control and release management
- **UI/UX**: User interface improvements  
- **Modules**: Individual module development
- **Navigation**: Menu and navigation improvements
- **Backend**: Django backend changes
- **Bug Fix**: Error corrections
- **Performance**: Optimization improvements
- **Archive System**: Backup and archiving
- **Development Tools**: Scripts and automation

### Using the Log Script:
```bash
./add_dev_log.sh "Category" "Title" "Details" "Result"
```

---

## 🔤 UI Text Standards

### All UI Text Must Be:
- **lowercase** - No uppercase text in web UI or CLI interfaces
- **consistent** - Same style across all interfaces (web and CLI)
- **minimal** - Short, clear labels
- **no title case** - "version manager" not "Version Manager"

### Examples:
✅ Correct:
- version manager
- archive analyzer  
- git status
- total archives
- klondike solitaire
- screen locked - enter password
- congratulations! you won!

❌ Incorrect:
- Version Manager
- Archive Analyzer
- Git Status
- Total Archives
- KLONDIKE SOLITAIRE
- Screen Locked - Enter Password
- CONGRATULATIONS! YOU WON!

---

## 🔧 Version Management

### Before Creating New Version:
1. **Check current version** from VERSION.json
2. **Verify no gaps** in version sequence
3. **Update DEVELOPMENT_LOG.md** with changes
4. **Use auto-commit messages** from recent logs

### Version Release Process:
1. Update VERSION.json
2. Update Django files if needed
3. Create archive (no ZIP, only folders)
4. Perform git operations
5. Log the release in DEVELOPMENT_LOG.md

---

## 💾 Code Standards

### Python Code:
- Follow PEP 8
- Add docstrings to all functions
- Handle exceptions properly
- Use type hints where appropriate

### JavaScript:
- Use modern ES6+ syntax
- Add JSDoc comments
- Handle async operations properly
- Consistent error handling

### Django Templates:
- Use lowercase for all text
- Semantic HTML5 elements
- Accessible markup (ARIA labels)
- Mobile-responsive design

### CLI Interface:
- All text must be lowercase (game titles, messages, prompts)
- Consistent prompt formatting: "enter password:" not "Enter Password:"
- Error messages in lowercase: "incorrect password!" not "Incorrect password!"
- Game text in lowercase: "klondike solitaire" not "KLONDIKE SOLITAIRE"

### Documentation (README.md, etc):
- **ALL text must be lowercase**
- No title case anywhere
- Remove motivational quotes
- Keep professional but minimal

---

## 🧪 Testing Requirements

### Before Committing:
1. **Test all changes** manually
2. **Check for console errors** in browser
3. **Verify CLI still works** after changes
4. **Test on different screen sizes** for web UI

### Critical Areas:
- Version manager operations
- Archive creation
- Git operations
- Navigation (arrow keys, enter, q)
- Web UI responsiveness

---

## 📁 File Organization

### Directory Structure:
```
/backend/           # Django backend
/src/              # CLI source code
/archive/          # Version archives
/DEVELOPMENT_LOG.md # Development history
/CLAUDE.md         # This file
/add_dev_log.sh    # Log helper script
```

### Naming Conventions:
- Python files: `snake_case.py`
- JavaScript: `camelCase.js`
- Templates: `snake_case.html`
- CSS: `kebab-case.css`

---

## 🚫 Never Do

1. **Never skip logging** development activities
2. **Never use uppercase** in web UI or CLI text
3. **Never create ZIP archives** (only folders)
4. **Never commit without testing**
5. **Never delete DEVELOPMENT_LOG.md**
6. **Never change version numbers manually** (use scripts)

---

## ✅ Always Do

1. **Always update DEVELOPMENT_LOG.md** after changes
2. **Always use lowercase** in web UI and CLI
3. **Always test before committing**
4. **Always handle errors gracefully**
5. **Always document complex logic**
6. **Always preserve user data**

---

## 🔄 Session Handover

### At End of Each Session:
1. **Summary of changes** in DEVELOPMENT_LOG.md
2. **List any pending tasks** clearly
3. **Note any known issues** or bugs
4. **Update this file** if new patterns emerge

### Starting New Session:
1. **Read DEVELOPMENT_LOG.md** for recent changes
2. **Check VERSION.json** for current version
3. **Review pending tasks** from previous session
4. **Test critical features** still work

---

## 📊 Performance Guidelines

### Optimization Priorities:
1. **CLI responsiveness** < 100ms for navigation
2. **Web page loads** < 2 seconds
3. **Archive creation** < 30 seconds
4. **Database queries** optimized with indexes

---

## 🌍 Localization

### Language Support:
- Primary: English (en)
- Secondary: Turkish (tr)
- All text should be localizable
- Use translation keys, not hardcoded text

---

## 📈 Z-Score Reference

### For Archive Size Anomaly Detection:
- **Normal**: Z-Score between -1 and 1
- **Warning**: Z-Score between 1 and 2
- **Anomaly**: Z-Score > 2 or < -2

---

## 🔗 Related Documentation

- [DEVELOPMENT_LOG.md](DEVELOPMENT_LOG.md) - Track all changes here
- [VERSION_MANAGEMENT.md](VERSION_MANAGEMENT.md) - Version system details
- [CLAUDE_INSTRUCTIONS.md](CLAUDE_INSTRUCTIONS.md) - Detailed Claude instructions
- [ARCHIVE_GUIDE.md](ARCHIVE_GUIDE.md) - Archive protection protocols

---

Last Updated: 2025-08-12
Author: Claude & Berk Hatırlı
Version: 2.0