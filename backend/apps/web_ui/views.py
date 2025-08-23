"""
UNIBOS Web UI Views
Terminal-style web interface matching the CLI design
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.conf import settings
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from apps.administration.models import ScreenLock
import json
import os
from pathlib import Path
from datetime import datetime

# Import VERSION info - First try backend/VERSION.json, then src/VERSION.json
VERSION_DATA = None
try:
    # First try backend VERSION.json
    backend_path = Path(__file__).parent.parent.parent
    backend_version_file = backend_path / 'VERSION.json'
    
    if backend_version_file.exists():
        with open(backend_version_file, 'r') as f:
            VERSION_DATA = json.load(f)
    
    # If not found, try src/VERSION.json
    if not VERSION_DATA:
        src_path = backend_path.parent / 'src'
        src_version_file = src_path / 'VERSION.json'
        
        if src_version_file.exists():
            with open(src_version_file, 'r') as f:
                VERSION_DATA = json.load(f)
    
    # If still not found, use fallback
    if not VERSION_DATA:
        VERSION_DATA = {
            "version": "v510",
            "build_number": "20250823_1022",
            "release_date": "2025-08-23"
        }
except:
    # Fallback to current version
    VERSION_DATA = {
        "version": "v510",
        "build_number": "20250823_1022",
        "release_date": "2025-08-23"
    }


@method_decorator(never_cache, name='dispatch')
class BaseUIView(TemplateView):
    """Base view with common context for all pages"""
    
    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        # Add cache control headers
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Context processors now provide common data (modules, tools, version, etc.)
        return context
    # Methods removed - now handled by context processors in apps.web_ui.context_processors


@method_decorator(login_required(login_url='/login/'), name='dispatch')
class MainView(BaseUIView):
    """Main dashboard view"""
    template_name = 'web_ui/main.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_module'] = None
        context['page_title'] = 'UNIBOS Main Menu'
        return context


@method_decorator(login_required(login_url='/login/'), name='dispatch')
class ModuleView(BaseUIView):
    """Generic module view"""
    
    def dispatch(self, request, *args, **kwargs):
        """Handle special module routing"""
        module_id = self.kwargs.get('module_id')
        from django.shortcuts import redirect, render
        
        # Map module IDs to their proper names
        if module_id == 'kisisel_enflasyon':
            return redirect('personal_inflation:dashboard')
        
        # Redirect CCTV to its own app
        if module_id == 'cctv':
            return redirect('cctv:dashboard')
        
        # Redirect Documents to its own app
        if module_id == 'documents':
            return redirect('documents:dashboard')
        
        # Redirect Movies to its own app
        if module_id == 'movies':
            return redirect('movies:dashboard')
        
        # Redirect Music to its own app
        if module_id == 'music':
            return redirect('music:dashboard')
        
        # Redirect RestoPOS to its own app
        if module_id == 'restopos':
            return redirect('restopos:dashboard')
        
        # Redirect Birlikteyiz to its own app
        if module_id == 'birlikteyiz':
            return redirect('birlikteyiz:dashboard')
        
        # Redirect Recaria to its own view
        if module_id == 'recaria':
            return redirect('recaria:dashboard')
        
        # Handle store module (placeholder for now)
        if module_id == 'store':
            return render(request, 'web_ui/module_placeholder.html', {
                'module_name': 'store',
                'module_icon': '🛍️',
                'message': 'store module is under development'
            })
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_template_names(self):
        """Return appropriate template based on module"""
        module_id = self.kwargs.get('module_id')
        
        # Check if module has a specific template
        module_templates = {
            'currencies': 'web_ui/modules/currencies.html',
            'wimm': 'web_ui/modules/wimm.html',
            'wims': 'web_ui/modules/wims.html',
            'cctv': 'redirect',  # CCTV has its own app with views
        }
        
        if module_id in module_templates:
            return [module_templates[module_id]]
        
        # Default to generic module template
        return ['web_ui/module.html']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        module_id = self.kwargs.get('module_id')
        
        # Get module details
        module_data = self.get_module_data(module_id)
        context.update({
            'current_module': module_id,
            'module_data': module_data,
            'page_title': f'UNIBOS - {module_data.get("name", module_id)}'
        })
        
        # Add currencies-specific context if needed
        if module_id == 'currencies':
            context.update(self.get_currencies_context())
        elif module_id == 'wimm':
            context.update(self.get_wimm_context())
        elif module_id == 'wims':
            context.update(self.get_wims_context())
        
        return context
    
    def get_currencies_context(self):
        """Get currencies-specific context data"""
        from apps.currencies.models import BankExchangeRate, Currency, ExchangeRate
        from django.db.models import Count, Max
        
        try:
            # Get statistics
            total_banks = BankExchangeRate.objects.values('bank').distinct().count()
            total_pairs = BankExchangeRate.objects.values('currency_pair').distinct().count()
            latest_update = BankExchangeRate.objects.aggregate(Max('timestamp'))['timestamp__max']
            
            return {
                'currencies_stats': {
                    'total_banks': total_banks,
                    'total_pairs': total_pairs,
                    'latest_update': latest_update,
                    'active_currencies': Currency.objects.filter(is_active=True).count()
                }
            }
        except:
            return {
                'currencies_stats': {
                    'total_banks': 0,
                    'total_pairs': 0,
                    'latest_update': None,
                    'active_currencies': 0
                }
            }
    
    def get_wimm_context(self):
        """Get WIMM-specific context data"""
        from apps.wimm.views import wimm_dashboard
        
        # Call the WIMM dashboard view logic
        if self.request.user.is_authenticated:
            from apps.core.models import Account
            from apps.wimm.models import Transaction, Invoice, Budget
            from django.db.models import Sum
            from django.utils import timezone
            from decimal import Decimal
            
            accounts = Account.objects.filter(user=self.request.user)
            total_balance = accounts.aggregate(total=Sum('balance'))['total'] or Decimal('0')
            
            recent_transactions = Transaction.objects.filter(
                user=self.request.user
            ).order_by('-transaction_date')[:10]
            
            today = timezone.now()
            month_start = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            month_income = Transaction.objects.filter(
                user=self.request.user,
                transaction_type='income',
                transaction_date__gte=month_start
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
            
            month_expense = Transaction.objects.filter(
                user=self.request.user,
                transaction_type='expense',
                transaction_date__gte=month_start
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
            
            pending_invoices = Invoice.objects.filter(
                user=self.request.user,
                payment_status__in=['pending', 'partial']
            ).count()
            
            active_budgets = Budget.objects.filter(
                user=self.request.user,
                start_date__lte=today,
                end_date__gte=today
            )
            
            return {
                'accounts': accounts,
                'total_balance': total_balance,
                'recent_transactions': recent_transactions,
                'month_income': month_income,
                'month_expense': month_expense,
                'month_net': month_income - month_expense,
                'pending_invoices': pending_invoices,
                'active_budgets': active_budgets,
            }
        
        return {}
    
    def get_wims_context(self):
        """Get WIMS-specific context data"""
        if self.request.user.is_authenticated:
            from apps.wims.models import Warehouse, StockItem, StockMovement
            from apps.core.models import Item
            from django.db.models import Sum, Count, F
            
            warehouses = Warehouse.objects.filter(user=self.request.user)
            total_items = Item.objects.filter(stock_items__warehouse__user=self.request.user).distinct().count()
            
            total_stock_value = StockItem.objects.filter(
                warehouse__user=self.request.user
            ).aggregate(
                total=Sum('quantity')
            )['total'] or 0
            
            recent_movements = StockMovement.objects.filter(
                user=self.request.user
            ).order_by('-movement_date')[:10]
            
            # Check for expiring items
            from datetime import timedelta
            from django.utils import timezone
            
            expiry_threshold = timezone.now().date() + timedelta(days=30)
            expiring_items = StockItem.objects.filter(
                warehouse__user=self.request.user,
                expiry_date__lte=expiry_threshold,
                expiry_date__gte=timezone.now().date()
            ).count()
            
            # Low stock items
            low_stock_items = StockItem.objects.filter(
                warehouse__user=self.request.user,
                quantity__lte=F('reorder_point')
            ).count()
            
            return {
                'warehouses': warehouses,
                'total_items': total_items,
                'total_stock_value': total_stock_value,
                'recent_movements': recent_movements,
                'expiring_items': expiring_items,
                'low_stock_items': low_stock_items,
            }
        
        return {}
    
    def get_module_data(self, module_id):
        """Get specific module data"""
        # Get icon from sidebar context dynamically
        from .context_processors import sidebar_context
        sidebar_data = sidebar_context(self.request)
        
        # Find the correct icon from sidebar modules
        module_icon = '📦'  # Default icon
        for module in sidebar_data['modules']:
            if module['id'] == module_id:
                module_icon = module['icon']
                break
        
        modules = {
            'recaria': {
                'name': 'recaria',
                'icon': module_icon if module_id == 'recaria' else '🪐',
                'description': 'ultima online inspired system',
                'features': [
                    'character management',
                    'guild system',
                    'trading post',
                    'quest tracking'
                ],
                'stats': {
                    'users': 0,
                    'guilds': 0,
                    'active_quests': 0
                }
            },
            'birlikteyiz': {
                'name': 'birlikteyiz',
                'icon': module_icon if module_id == 'birlikteyiz' else '📡',
                'description': 'community emergency response system',
                'features': [
                    'real-time earthquake tracking',
                    'multiple data sources (kandilli, afad, usgs)',
                    'emergency alerts & mesh network',
                    'disaster zone monitoring',
                    'resource point mapping',
                    'community help coordination'
                ],
                'stats': {
                    'active_alerts': 0,
                    'helpers': 0,
                    'resolved': 0
                }
            },
            'kisisel_enflasyon': {
                'name': 'kişisel enflasyon',
                'icon': module_icon if module_id == 'kisisel_enflasyon' else '📈',
                'description': 'personal inflation tracking',
                'features': [
                    'price tracking',
                    'inflation calculation',
                    'category analysis',
                    'historical data'
                ],
                'stats': {
                    'tracked_items': 0,
                    'categories': 0,
                    'inflation_rate': '0%'
                }
            },
            'currencies': {
                'name': 'currencies',
                'icon': module_icon if module_id == 'currencies' else '💰',
                'description': 'real-time currency exchange',
                'features': [
                    'live exchange rates',
                    'currency converter',
                    'historical charts',
                    'alerts'
                ],
                'stats': {
                    'tracked_pairs': 0,
                    'last_update': 'never',
                    'alerts': 0
                }
            },
            'wimm': {
                'name': 'wimm - where is my money',
                'icon': module_icon if module_id == 'wimm' else '💸',
                'description': 'financial management system',
                'features': [
                    'transaction tracking',
                    'invoice management',
                    'budget planning',
                    'cash flow analysis',
                    'multi-currency accounts'
                ],
                'stats': {
                    'accounts': 0,
                    'transactions': 0,
                    'invoices': 0
                }
            },
            'wims': {
                'name': 'wims - where is my stuff',
                'icon': module_icon if module_id == 'wims' else '📦',
                'description': 'inventory management system',
                'features': [
                    'stock tracking',
                    'multi-warehouse',
                    'batch/serial tracking',
                    'expiry alerts',
                    'stock movements'
                ],
                'stats': {
                    'warehouses': 0,
                    'items': 0,
                    'total_stock': 0
                }
            },
            'cctv': {
                'name': 'cctv',
                'icon': module_icon if module_id == 'cctv' else '📹',
                'description': 'professional security camera management',
                'features': [
                    'tp-link tapo camera support',
                    'live streaming & recording',
                    'motion detection alerts',
                    'ptz camera control',
                    'multi-camera grid view',
                    'kerberos.io integration'
                ],
                'stats': {
                    'cameras': 0,
                    'recording': 0,
                    'alerts': 0,
                    'storage_used': '0gb'
                }
            },
            'documents': {
                'name': 'documents',
                'icon': module_icon if module_id == 'documents' else '📄',
                'description': 'document management system',
                'features': [
                    'invoice processing',
                    'receipt scanning',
                    'ocr extraction',
                    'document search',
                    'cloud storage'
                ],
                'stats': {
                    'documents': 0,
                    'processed': 0,
                    'storage': '0gb'
                }
            },
            'movies': {
                'name': 'movies',
                'icon': module_icon if module_id == 'movies' else '🎬',
                'description': 'movie collection manager',
                'features': [
                    'movie database',
                    'watchlist tracking',
                    'ratings & reviews',
                    'recommendation engine'
                ],
                'stats': {
                    'movies': 0,
                    'watched': 0,
                    'watchlist': 0
                }
            },
            'music': {
                'name': 'music',
                'icon': module_icon if module_id == 'music' else '🎵',
                'description': 'music library manager',
                'features': [
                    'playlist management',
                    'album organization',
                    'artist tracking',
                    'streaming integration'
                ],
                'stats': {
                    'songs': 0,
                    'playlists': 0,
                    'artists': 0
                }
            },
            'restopos': {
                'name': 'restopos',
                'icon': module_icon if module_id == 'restopos' else '🍽️',
                'description': 'restaurant pos system',
                'features': [
                    'order management',
                    'table tracking',
                    'inventory control',
                    'payment processing'
                ],
                'stats': {
                    'orders': 0,
                    'tables': 0,
                    'revenue': '₺0'
                }
            }
        }
        
        return modules.get(module_id, {
            'name': module_id.replace('_', ' '),
            'icon': module_icon,  # Use dynamic icon even for fallback
            'description': 'module description',
            'features': [],
            'stats': {}
        })


class ToolView(BaseUIView):
    """Tool view"""
    
    def get_template_names(self):
        """Return appropriate template based on tool"""
        tool_id = self.kwargs.get('tool_id')
        
        # Special handling for administration
        if tool_id == 'administration':
            # Redirect to administration app
            from django.shortcuts import redirect
            return None  # Will be handled in dispatch
        
        return ['web_ui/tool.html']
    
    def dispatch(self, request, *args, **kwargs):
        tool_id = self.kwargs.get('tool_id')
        
        # Redirect administration to the admin module
        if tool_id == 'administration':
            from django.shortcuts import redirect
            return redirect('administration:dashboard')
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tool_id = self.kwargs.get('tool_id')
        
        context.update({
            'current_tool': tool_id,
            'tool_data': self.get_tool_data(tool_id),
            'page_title': f'unibos - {tool_id.replace("_", " ")}'
        })
        
        return context
    
    def get_tool_data(self, tool_id):
        """Get tool specific data"""
        # Get icon from sidebar context dynamically
        from .context_processors import sidebar_context
        sidebar_data = sidebar_context(self.request)
        
        # Find the correct icon from sidebar tools and dev_tools
        tool_icon = '🔧'  # Default icon
        for tool in sidebar_data['tools'] + sidebar_data['dev_tools']:
            if tool['id'] == tool_id:
                tool_icon = tool['icon']
                break
        
        tools = {
            'web_forge': {
                'name': 'web forge',
                'icon': tool_icon if tool_id == 'web_forge' else '🌐',
                'description': 'web interface management',
                'status': 'running',
                'port': 8000,
                'features': [
                    'start/stop web server',
                    'view logs',
                    'configuration',
                    'database status'
                ]
            },
            'database_setup': {
                'name': 'database setup',
                'icon': tool_icon if tool_id == 'database_setup' else '🗄️',
                'description': 'database configuration wizard',
                'status': 'connected',
                'database': 'postgresql',
                'features': [
                    'connection test',
                    'migration status',
                    'backup/restore',
                    'query console'
                ]
            }
        }
        
        return tools.get(tool_id, {
            'name': tool_id.replace('_', ' '),
            'icon': tool_icon,  # Use dynamic icon even for fallback
            'description': 'tool description',
            'features': []
        })


class APIStatusView(View):
    """API endpoint for system status"""
    
    def get(self, request):
        """Get current system status"""
        status = {
            'version': VERSION_DATA['version'],
            'build': VERSION_DATA['build_number'],
            'time': datetime.now().isoformat(),
            'online': self.check_online_status(),
            'modules': {
                'recaria': {'status': 'active', 'health': 'good'},
                'birlikteyiz': {'status': 'active', 'health': 'good'},
                'kisisel_enflasyon': {'status': 'active', 'health': 'good'},
                'currencies': {'status': 'active', 'health': 'good'},
            }
        }
        
        return JsonResponse(status)
    
    def check_online_status(self):
        """Check if system is online"""
        try:
            import socket
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            return True
        except:
            return False

class LoginView(TemplateView):
    """Login page view"""
    template_name = 'web_ui/login.html'
    
    def dispatch(self, request, *args, **kwargs):
        # Redirect if already authenticated
        if request.user.is_authenticated:
            return redirect('web_ui:main')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Version info is now provided by context processor
        return context
    
    def post(self, request, *args, **kwargs):
        """Handle login POST request"""
        import json
        
        # Get credentials from request
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Try JSON body if form data not found
        if not username and request.content_type == 'application/json':
            try:
                data = json.loads(request.body)
                username = data.get('username')
                password = data.get('password')
            except:
                pass
        
        # Authenticate user
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Login successful
            login(request, user)
            
            # Return JSON response for AJAX
            if request.content_type == 'application/json':
                return JsonResponse({
                    'success': True,
                    'user': {
                        'username': user.username,
                        'email': user.email,
                        'is_superuser': user.is_superuser
                    }
                })
            else:
                return redirect('web_ui:main')
        else:
            # Login failed
            if request.content_type == 'application/json':
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid credentials'
                }, status=400)
            else:
                context = self.get_context_data()
                context['error'] = 'Invalid credentials'
                return self.render_to_response(context)


def logout_view(request):
    """Logout view"""
    logout(request)
    return redirect('web_ui:login')


@method_decorator(login_required, name='dispatch')
class ProfileView(BaseUIView):
    """User profile view"""
    template_name = 'web_ui/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get user profile if it exists
        profile = None
        try:
            from apps.core.models import UserProfile
            profile = UserProfile.objects.filter(user=self.request.user).first()
            if not profile:
                # Create profile if it doesn't exist
                profile = UserProfile.objects.create(user=self.request.user)
        except:
            # UserProfile model might not exist or have issues
            pass
        
        # Get user's public information
        user = self.request.user
        
        # Calculate some statistics
        from django.utils import timezone
        days_member = (timezone.now().date() - user.date_joined.date()).days
        
        context.update({
            'profile': profile,
            'user': user,
            'days_member': days_member,
            'page_title': f'@{self.request.user.username}'
        })
        
        return context


@method_decorator(login_required, name='dispatch')
class SettingsView(BaseUIView):
    """User settings view"""
    template_name = 'web_ui/settings.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get user profile if it exists
        profile = None
        try:
            from apps.core.models import UserProfile
            profile = UserProfile.objects.filter(user=self.request.user).first()
        except:
            # UserProfile model might not exist
            pass
        
        context.update({
            'user': self.request.user,
            'profile': profile,
            'page_title': 'settings'
        })
        
        return context
    
    def post(self, request, *args, **kwargs):
        """Handle settings updates"""
        from django.http import JsonResponse
        
        setting_type = request.POST.get('type')
        setting_value = request.POST.get('value')
        
        if setting_type == 'theme':
            request.session['theme'] = setting_value
        elif setting_type == 'language':
            request.session['language'] = setting_value
        elif setting_type == 'sidebar_auto_hide':
            request.session['sidebar_auto_hide'] = setting_value == 'true'
        
        return JsonResponse({'status': 'success'})


@login_required(login_url='/login/')
@never_cache
def solitaire_view(request):
    """Solitaire game view (screen lock minimized mode)"""
    # Import the solitaire models and game logic
    from apps.solitaire.models import SolitaireSession
    from apps.solitaire.game import SolitaireGame
    import uuid
    import json
    
    # Set session flag
    request.session['in_solitaire'] = True
    
    # Get or create screen lock for user
    screen_lock, created = ScreenLock.objects.get_or_create(user=request.user)
    
    # Get or create active session (same logic as solitaire app)
    session = SolitaireSession.objects.filter(
        user=request.user,
        is_active=True
    ).first()
    
    if not session:
        # Create new game session
        game = SolitaireGame()
        game.new_game()
        game_state = game.to_dict()
        
        # Create session
        session = SolitaireSession.objects.create(
            user=request.user,
            session_id=str(uuid.uuid4()),
            is_active=True
        )
        session.save_game_state(game_state)
        session.save()
    
    # Get game state
    game_state = session.get_game_state()
    
    context = {
        'has_screen_lock': screen_lock.is_enabled,
        'version': VERSION_DATA['version'],
        'build_number': VERSION_DATA['build_number'],
        'cache_buster': int(timezone.now().timestamp() * 1000),  # Current timestamp in ms
        'spacing_version': '2px-18px-fixed',
        'solitaire_version': 'v3.1',
        # ADD THE MISSING GAME STATE!
        'session_id': session.session_id,
        'game_state': json.dumps(game_state),
        'is_authenticated': True
    }
    
    # Use the actual solitaire template, not a separate one
    response = render(request, 'web_ui/solitaire.html', context)
    
    # Add aggressive cache-busting headers specifically for Safari
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0, private'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    response['Last-Modified'] = timezone.now().strftime('%a, %d %b %Y %H:%M:%S GMT')
    response['ETag'] = f'"solitaire-v2.1-{int(timezone.now().timestamp())}"'
    response['Vary'] = 'User-Agent'
    
    # Safari-specific headers
    response['Apple-Cache-Control'] = 'no-cache'
    response['X-UA-Compatible'] = 'IE=edge,chrome=1'
    
    return response


@login_required(login_url='/login/')
def exit_solitaire(request):
    """Exit solitaire (requires screen lock code)"""
    if request.method == 'POST':
        code = request.POST.get('code')
        
        # Get screen lock
        try:
            screen_lock = request.user.screen_lock
            
            if not screen_lock.is_enabled:
                # No screen lock, allow exit
                request.session['in_solitaire'] = False
                return JsonResponse({'success': True})
            
            # Check if locked out
            if screen_lock.is_locked_out():
                return JsonResponse({
                    'success': False,
                    'error': 'too many failed attempts. please wait.'
                })
            
            # Verify code
            if screen_lock.check_password(code):
                screen_lock.reset_failed_attempts()
                screen_lock.last_unlocked = timezone.now()
                screen_lock.save()
                
                # Clear session flag
                request.session['in_solitaire'] = False
                
                return JsonResponse({'success': True})
            else:
                screen_lock.record_failed_attempt()
                remaining = screen_lock.max_failed_attempts - screen_lock.failed_attempts
                
                return JsonResponse({
                    'success': False,
                    'error': f'incorrect password. {remaining} attempts remaining.'
                })
        
        except ScreenLock.DoesNotExist:
            # No screen lock configured, allow exit
            request.session['in_solitaire'] = False
            return JsonResponse({'success': True})
    
    return JsonResponse({'success': False, 'error': 'invalid request'})