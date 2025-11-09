"""
WIMS (Where Is My Stuff) Views
"""
from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Sum, Count
from .models import Warehouse, StockItem, StockMovement


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_module_data(request):
    """Get inventory data for current user via API"""
    user = request.user
    
    # Get warehouses
    warehouses = Warehouse.objects.filter(user=user, is_active=True)
    
    # Get stock items
    stock_items = StockItem.objects.filter(
        warehouse__user=user
    ).select_related('item', 'warehouse')
    
    # Get recent movements
    recent_movements = StockMovement.objects.filter(
        user=user
    ).order_by('-movement_date')[:10]
    
    # Calculate totals
    total_items = stock_items.aggregate(
        total_quantity=Sum('quantity'),
        total_value=Sum('quantity') 
    )
    
    # Low stock items
    low_stock_items = [
        item for item in stock_items 
        if item.quantity <= item.reorder_point and item.reorder_point > 0
    ]
    
    # Expiring items
    from datetime import datetime, timedelta
    expiry_threshold = datetime.now().date() + timedelta(days=30)
    expiring_items = stock_items.filter(
        expiry_date__lte=expiry_threshold,
        expiry_date__isnull=False
    ).count()
    
    return Response({
        'summary': {
            'total_warehouses': warehouses.count(),
            'total_stock_items': stock_items.count(),
            'total_quantity': total_items['total_quantity'] or 0,
            'low_stock_count': len(low_stock_items),
            'expiring_soon': expiring_items,
        },
        'warehouses': [{
            'id': w.id,
            'name': w.name,
            'code': w.code,
            'type': w.warehouse_type,
            'location': f"{w.city}, {w.country}" if w.city else w.country,
        } for w in warehouses],
        'recent_movements': [{
            'id': m.id,
            'type': m.movement_type,
            'item': m.item.name,
            'quantity': float(m.quantity),
            'date': m.movement_date.isoformat(),
            'warehouse': m.to_warehouse.name if m.to_warehouse else None,
        } for m in recent_movements],
        'message': 'WIMS module loaded successfully'
    })
