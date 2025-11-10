# 🚀 UNIBOS Deployment Commands

**Last Updated**: 2025-11-10 (v532+ Modular Structure)

## Quick One-Liner Deploy to Rocksteady

### 🎯 The Simplest Command (Recommended):
```bash
rsync -avz --exclude-from=.rsync-exclude . rocksteady:~/unibos/ && ssh rocksteady "cd ~/unibos && ./unibos.sh"
```

Or without exclude file:
```bash
rsync -avz --exclude={.git,venv,archive,quarantine,*.sql,*.log,db.sqlite3} . rocksteady:~/unibos/ && ssh rocksteady "cd ~/unibos && ./unibos.sh"
```

This single command:
1. Syncs your local UNIBOS to rocksteady server
2. Runs unibos.sh which handles everything else

### 📦 With Backup (Safe):
```bash
ssh rocksteady "[ -d ~/unibos ] && mv ~/unibos ~/unibos_$(date +%s)" ; rsync -avz --exclude=".git" --exclude="venv" . rocksteady:~/unibos/ && ssh rocksteady "cd ~/unibos && ./unibos.sh"
```

### 🤫 Silent Mode (Minimal Output):
```bash
rsync -qaz --exclude={.git,__pycache__,venv} . rocksteady:~/unibos/ && ssh rocksteady "cd ~/unibos && ./unibos.sh" 2>/dev/null
```

### 🏃 Run in Background:
```bash
rsync -qaz --exclude={.git,venv} . rocksteady:~/unibos/ && ssh rocksteady "cd ~/unibos && nohup ./unibos.sh > /tmp/unibos.log 2>&1 &"
```

Then check logs with:
```bash
ssh rocksteady "tail -f /tmp/unibos.log"
```

## 🔧 Management Commands

### Check Status:
```bash
ssh rocksteady "ps aux | grep unibos"
```

### Restart:
```bash
ssh rocksteady "cd ~/unibos && pkill -f unibos; ./unibos.sh"
```

### View Logs:
```bash
ssh rocksteady "tail -f /tmp/unibos.log"
```

### Stop All:
```bash
ssh rocksteady "pkill -f 'python.*(main|manage)'"
```

## 🎯 Super Quick Copy-Paste

Just copy and run this:
```bash
rsync -avz --exclude={.git,venv,__pycache__,archive,quarantine,*.sql,*.log,data_db/backups,db.sqlite3,.DS_Store} . rocksteady:~/unibos/ && ssh rocksteady "cd ~/unibos && ./unibos.sh"
```

That's it! UNIBOS will be running on rocksteady. 🎉

Access at: `http://rocksteady.local:8000`

---

## 📦 v532+ Modular Structure Notes

Starting with v532, UNIBOS uses a modular architecture with 21 modules in `modules/*/backend/`:

### Structure:
```
modules/
├── core/backend/           # Core shared functionality
├── web_ui/backend/         # Web interface
├── documents/backend/      # OCR and document processing
├── birlikteyiz/backend/    # Emergency response
├── wimm/backend/           # Financial management
└── ... (16 more modules)
```

### Deployment Impact:
- **Same commands work** - rsync handles modules/ directory automatically
- **Module configs** - Each module has its own `module.json`
- **Migrations** - Django handles all module migrations together
- **Static files** - Collected from all modules to `apps/web/backend/staticfiles/`

### What Gets Deployed:
✅ `modules/*/backend/` - All module backend code
✅ `apps/web/backend/` - Django project settings
✅ `apps/cli/` - CLI interface
❌ `modules/*/mobile/build/` - Excluded (Flutter builds)
❌ `archive/` - Excluded (protected)