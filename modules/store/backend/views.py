from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, TemplateView
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum, Count, Q, F
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

from .models import Marketplace, Order, OrderItem, Product, SyncLog
from .sentos_api import SentosAPI
import json


@method_decorator(login_required, name='dispatch')
class StoreDashboardView(TemplateView):
    """Store dashboard with overview"""
    template_name = 'store/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get user's marketplaces
        marketplaces = Marketplace.objects.filter(user=user)
        
        # Get recent orders
        recent_orders = Order.objects.filter(user=user).select_related('marketplace')[:10]
        
        # Calculate statistics
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        # Today's stats
        today_orders = Order.objects.filter(
            user=user,
            order_date__date=today
        )
        today_revenue = today_orders.aggregate(
            total=Sum('total_amount')
        )['total'] or Decimal('0')
        
        # This week's stats
        week_orders = Order.objects.filter(
            user=user,
            order_date__date__gte=week_ago
        )
        week_revenue = week_orders.aggregate(
            total=Sum('total_amount')
        )['total'] or Decimal('0')
        
        # This month's stats
        month_orders = Order.objects.filter(
            user=user,
            order_date__date__gte=month_ago
        )
        month_revenue = month_orders.aggregate(
            total=Sum('total_amount')
        )['total'] or Decimal('0')
        
        # Order status breakdown
        status_breakdown = Order.objects.filter(user=user).values('status').annotate(
            count=Count('id')
        ).order_by('status')
        
        # Low stock products
        low_stock_products = Product.objects.filter(
            user=user,
            stock_quantity__lte=F('low_stock_threshold')
        ).select_related('marketplace')[:10]
        
        # Best selling products
        best_sellers = Product.objects.filter(user=user).order_by('-total_sales')[:5]
        
        context.update({
            'marketplaces': marketplaces,
            'recent_orders': recent_orders,
            'today_orders_count': today_orders.count(),
            'today_revenue': today_revenue,
            'week_orders_count': week_orders.count(),
            'week_revenue': week_revenue,
            'month_orders_count': month_orders.count(),
            'month_revenue': month_revenue,
            'status_breakdown': status_breakdown,
            'low_stock_products': low_stock_products,
            'best_sellers': best_sellers,
            'pending_orders_count': Order.objects.filter(
                user=user, status='pending'
            ).count(),
            'processing_orders_count': Order.objects.filter(
                user=user, status='processing'
            ).count(),
        })
        
        return context


@method_decorator(login_required, name='dispatch')
class OrderListView(ListView):
    """List all orders"""
    model = Order
    template_name = 'store/orders/list.html'
    context_object_name = 'orders'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Order.objects.filter(user=self.request.user).select_related('marketplace')
        
        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Filter by marketplace
        marketplace_id = self.request.GET.get('marketplace')
        if marketplace_id:
            queryset = queryset.filter(marketplace_id=marketplace_id)
        
        # Search
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(order_number__icontains=search) |
                Q(customer_name__icontains=search) |
                Q(customer_email__icontains=search) |
                Q(platform_order_id__icontains=search)
            )
        
        # Date range
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        
        if date_from:
            queryset = queryset.filter(order_date__gte=date_from)
        
        if date_to:
            queryset = queryset.filter(order_date__lte=date_to)
        
        return queryset.order_by('-order_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['marketplaces'] = Marketplace.objects.filter(user=self.request.user)
        context['status_choices'] = Order.STATUS_CHOICES
        return context


@method_decorator(login_required, name='dispatch')
class OrderDetailView(DetailView):
    """Order detail view"""
    model = Order
    template_name = 'store/orders/detail.html'
    context_object_name = 'order'
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).select_related('marketplace')


@method_decorator(login_required, name='dispatch')
class ProductListView(ListView):
    """List all products"""
    model = Product
    template_name = 'store/products/list.html'
    context_object_name = 'products'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Product.objects.filter(user=self.request.user).select_related('marketplace')
        
        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Filter by marketplace
        marketplace_id = self.request.GET.get('marketplace')
        if marketplace_id:
            queryset = queryset.filter(marketplace_id=marketplace_id)
        
        # Search
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(sku__icontains=search) |
                Q(barcode__icontains=search) |
                Q(brand__icontains=search)
            )
        
        # Low stock filter
        if self.request.GET.get('low_stock'):
            queryset = queryset.filter(stock_quantity__lte=F('low_stock_threshold'))
        
        return queryset.order_by('title')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['marketplaces'] = Marketplace.objects.filter(user=self.request.user)
        context['status_choices'] = Product.STATUS_CHOICES
        return context


@method_decorator(login_required, name='dispatch')
class MarketplaceListView(ListView):
    """List user's marketplaces"""
    model = Marketplace
    template_name = 'store/marketplaces/list.html'
    context_object_name = 'marketplaces'
    
    def get_queryset(self):
        return Marketplace.objects.filter(user=self.request.user)


@login_required
def marketplace_add(request):
    """Add new marketplace"""
    if request.method == 'POST':
        platform = request.POST.get('platform')
        shop_name = request.POST.get('shop_name')
        
        # For Sentos integration
        if platform == 'sentos':
            sentos_api_key = request.POST.get('sentos_api_key')
            sentos_shop_url = request.POST.get('sentos_shop_url')
            
            # Test connection
            api = SentosAPI(sentos_api_key, sentos_shop_url)
            if api.test_connection():
                marketplace = Marketplace.objects.create(
                    user=request.user,
                    platform=platform,
                    shop_name=shop_name,
                    sentos_api_key=sentos_api_key,
                    sentos_shop_url=sentos_shop_url,
                    status='active'
                )
                
                # Get connected marketplaces from Sentos
                try:
                    connected = api.get_marketplaces()
                    messages.success(
                        request,
                        f"Successfully connected to Sentos! Found {len(connected)} marketplace(s)."
                    )
                except:
                    pass
                
                return redirect('store:marketplace_detail', pk=marketplace.pk)
            else:
                messages.error(request, "Failed to connect to Sentos API. Please check your credentials.")
        else:
            # Other marketplace types
            marketplace = Marketplace.objects.create(
                user=request.user,
                platform=platform,
                shop_name=shop_name,
                api_key=request.POST.get('api_key', ''),
                api_secret=request.POST.get('api_secret', ''),
                status='pending'
            )
            messages.success(request, f"Marketplace {shop_name} added successfully!")
            return redirect('store:marketplace_detail', pk=marketplace.pk)
    
    return render(request, 'store/marketplaces/add.html', {
        'platform_choices': Marketplace.PLATFORM_CHOICES
    })


@login_required
def marketplace_sync(request, pk):
    """Sync marketplace data"""
    marketplace = get_object_or_404(Marketplace, pk=pk, user=request.user)
    
    if marketplace.platform != 'sentos':
        messages.error(request, "Only Sentos marketplaces can be synced currently.")
        return redirect('store:marketplace_detail', pk=pk)
    
    # Create sync log
    sync_log = SyncLog.objects.create(
        marketplace=marketplace,
        sync_type='full',
        status='running'
    )
    
    try:
        api = SentosAPI(marketplace.sentos_api_key, marketplace.sentos_shop_url)
        
        # Sync orders
        order_results = api.sync_orders()
        
        # Sync products
        product_results = api.sync_products()
        
        # Update marketplace statistics
        marketplace.last_sync = timezone.now()
        marketplace.total_orders = Order.objects.filter(marketplace=marketplace).count()
        marketplace.total_products = Product.objects.filter(marketplace=marketplace).count()
        marketplace.total_revenue = Order.objects.filter(
            marketplace=marketplace
        ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        marketplace.save()
        
        # Update sync log
        sync_log.status = 'success'
        sync_log.completed_at = timezone.now()
        sync_log.items_processed = order_results['total'] + product_results['total']
        sync_log.items_created = order_results['created'] + product_results['created']
        sync_log.items_updated = order_results['updated'] + product_results['updated']
        sync_log.items_failed = order_results['failed'] + product_results['failed']
        
        if sync_log.completed_at and sync_log.started_at:
            sync_log.duration_seconds = (sync_log.completed_at - sync_log.started_at).total_seconds()
        
        sync_log.save()
        
        messages.success(
            request,
            f"Sync completed! Processed {sync_log.items_processed} items."
        )
        
    except Exception as e:
        sync_log.status = 'failed'
        sync_log.error_message = str(e)
        sync_log.completed_at = timezone.now()
        sync_log.save()
        
        messages.error(request, f"Sync failed: {str(e)}")
    
    return redirect('store:marketplace_detail', pk=pk)


@login_required
def order_update_status(request, pk):
    """Update order status"""
    order = get_object_or_404(Order, pk=pk, user=request.user)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        
        if new_status in dict(Order.STATUS_CHOICES):
            old_status = order.status
            order.status = new_status
            
            # Update timestamps
            if new_status == 'shipped':
                order.shipped_date = timezone.now()
                
                # Update tracking if provided
                tracking_number = request.POST.get('tracking_number')
                tracking_company = request.POST.get('tracking_company')
                
                if tracking_number:
                    order.tracking_number = tracking_number
                if tracking_company:
                    order.tracking_company = tracking_company
                    
            elif new_status == 'delivered':
                order.delivered_date = timezone.now()
            
            order.save()
            
            # Sync with marketplace if Sentos
            if order.marketplace.platform == 'sentos':
                try:
                    api = SentosAPI(
                        order.marketplace.sentos_api_key,
                        order.marketplace.sentos_shop_url
                    )
                    
                    tracking_info = None
                    if new_status == 'shipped' and order.tracking_number:
                        tracking_info = {
                            'tracking_number': order.tracking_number,
                            'tracking_company': order.tracking_company
                        }
                    
                    api.update_order_status(order.platform_order_id, new_status, tracking_info)
                    
                except Exception as e:
                    messages.warning(
                        request,
                        f"Order status updated locally but failed to sync: {str(e)}"
                    )
            
            messages.success(
                request,
                f"Order status updated from {old_status} to {new_status}"
            )
        else:
            messages.error(request, "Invalid status")
    
    return redirect('store:order_detail', pk=pk)


# API Views for AJAX
@login_required
def api_order_stats(request):
    """API endpoint for order statistics"""
    user = request.user
    period = request.GET.get('period', 'week')
    
    if period == 'day':
        date_from = timezone.now() - timedelta(days=1)
    elif period == 'week':
        date_from = timezone.now() - timedelta(days=7)
    elif period == 'month':
        date_from = timezone.now() - timedelta(days=30)
    else:
        date_from = timezone.now() - timedelta(days=7)
    
    orders = Order.objects.filter(
        user=user,
        order_date__gte=date_from
    )
    
    # Group by date
    daily_stats = {}
    for order in orders:
        date_key = order.order_date.date().isoformat()
        if date_key not in daily_stats:
            daily_stats[date_key] = {
                'count': 0,
                'revenue': Decimal('0')
            }
        daily_stats[date_key]['count'] += 1
        daily_stats[date_key]['revenue'] += order.total_amount
    
    return JsonResponse({
        'dates': list(daily_stats.keys()),
        'counts': [s['count'] for s in daily_stats.values()],
        'revenues': [float(s['revenue']) for s in daily_stats.values()]
    })


@login_required
def api_inventory_status(request):
    """API endpoint for inventory status"""
    user = request.user
    
    products = Product.objects.filter(user=user)
    
    status_data = {
        'in_stock': products.filter(stock_quantity__gt=F('low_stock_threshold')).count(),
        'low_stock': products.filter(
            stock_quantity__lte=F('low_stock_threshold'),
            stock_quantity__gt=0
        ).count(),
        'out_of_stock': products.filter(stock_quantity=0).count()
    }
    
    return JsonResponse(status_data)