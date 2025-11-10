# public server deployment status

**Last Updated**: 2025-11-10 (v532+ Modular Structure)

## ✅ deployment system updated

### quick deploy (⚡)
- **preserves remote settings** - production.py and .env backed up/restored
- **safe rsync** - uses .rsyncignore to protect archives and sensitive files
- **auto restart** - gunicorn and nginx restarted after deployment
- **instant** - takes ~10 seconds for code updates

### full deployment (📦)
- **complete setup** - handles dependencies, migrations, static files
- **uses rocksteady_deploy.sh** - leverages existing deployment script
- **settings preservation** - remote production settings maintained
- **comprehensive** - full stack deployment with all services

### backend only (🔧)
- **django specific** - syncs only backend directory
- **migrations included** - runs django migrations automatically
- **gunicorn restart** - backend service restarted
- **settings safe** - production.py preserved

### cli only (💻)
- **src directory sync** - updates cli interface code
- **permissions** - makes scripts executable
- **unibos.sh included** - launcher script updated
- **quick update** - for cli-only changes

## deployment workflow

```bash
# from local (mac):
cd ~/Desktop/unibos
python3 src/main.py

# navigate to:
dev tools → public server → deploy to rocksteady

# choose:
- quick deploy: for code updates (recommended)
- full deployment: for major changes
- backend only: for django updates
- cli only: for cli updates
```

## protected files

the following are **never overwritten** on remote:
- `apps/web/backend/unibos_backend/settings/production.py`
- `apps/web/backend/.env`
- `apps/web/backend/staticfiles/`
- `apps/web/backend/media/`
- `apps/web/backend/venv/`
- `modules/*/backend/media/` - Module-specific media files
- `modules/*/mobile/build/` - Flutter build outputs (excluded)
- `archive/` directory
- all `.sql` files
- all logs

## current status

- **ssh connection**: ✅ working
- **rsyncignore**: ✅ configured
- **remote structure**: ✅ valid
- **services**: ✅ all running
  - gunicorn: active
  - nginx: active
  - postgresql: active
- **web access**: ✅ accessible
  - https://recaria.org
  - https://recaria.org/admin

## usage tips

1. **always use quick deploy** for regular updates
2. **full deployment** only when:
   - new dependencies added
   - database schema changes
   - first time setup

3. **backend only** when:
   - django model changes
   - new apps added
   - api updates

4. **cli only** when:
   - updating cli menus
   - fixing cli bugs
   - no backend changes

## troubleshooting

if deployment fails:
```bash
# check ssh connection
ssh rocksteady

# check services
ssh rocksteady "sudo systemctl status gunicorn nginx postgresql"

# check logs
ssh rocksteady "sudo tail -50 /home/ubuntu/unibos/logs/gunicorn-error.log"

# manual restart
ssh rocksteady "sudo systemctl restart gunicorn nginx"
```

## key features

- **zero downtime** - services stay up during deployment
- **atomic updates** - all or nothing deployment
- **rollback capable** - settings backed up before changes
- **secure** - sensitive files never transferred
- **fast** - incremental rsync, only changed files
- **reliable** - tested deployment pipeline

## v532+ modular structure notes

### what changed:
- **21 modules** in `modules/*/backend/` directory
- **Django apps** remain in `apps/web/backend/`
- **CLI tools** remain in `apps/cli/`
- **Module isolation** - each module has own backend/, mobile/, module.json

### deployment considerations:
- **no changes needed** - rsync handles modules/ automatically
- **migrations work** - Django discovers all module migrations
- **static files** - collected from all modules to central staticfiles/
- **module configs** - module.json files define module metadata

### file sizes (v532+):
- `modules/`: ~25-35MB (21 modules)
- `apps/web/backend/`: ~8-10MB (Django settings)
- `apps/cli/`: ~3-4MB (CLI interface)

last updated: 2025-11-10