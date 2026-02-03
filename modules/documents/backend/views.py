"""
Documents Module Views
Handles document upload, OCR processing, and cross-module integration
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, FileResponse
from django.core.files.storage import default_storage
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from datetime import datetime, timedelta
from decimal import Decimal
import json
import os
import logging

from core.system.web_ui.backend.views import BaseUIView
from .models import (
    Document, ParsedReceipt, ReceiptItem, DocumentBatch,
    CreditCard, Subscription, ExpenseCategory, ExpenseGroup, ProcessingStatus
)
from modules.documents.backend.ocr_service import OCRProcessor, BatchProcessor, CrossModuleIntegrator
from modules.documents.backend.utils import ThumbnailGenerator, DocumentHelper, PaginationHelper

logger = logging.getLogger('documents.views')


class DocumentsDashboardView(LoginRequiredMixin, BaseUIView):
    """Main documents dashboard with enhanced features"""
    template_name = 'documents/dashboard.html'
    
    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        user = request.user
        
        # Get filter parameters
        doc_type = request.GET.get('type', '')
        status = request.GET.get('status', '')
        search = request.GET.get('search', '')
        
        # Get dynamic page size
        page_size = PaginationHelper.get_page_size(request, default=20)
        
        # Build document query with select_related for performance (exclude soft deleted)
        documents = Document.objects.filter(user=user, is_deleted=False).select_related('parsed_receipt')
        
        if doc_type:
            documents = documents.filter(document_type=doc_type)
        if status:
            documents = documents.filter(processing_status=status)
        if search:
            documents = documents.filter(
                Q(original_filename__icontains=search) |
                Q(ocr_text__icontains=search) |
                Q(parsed_receipt__store_name__icontains=search)
            )
        
        # Order by upload date
        documents = documents.order_by('-uploaded_at')
        
        # Enhanced pagination with dynamic page size
        paginator = Paginator(documents, page_size)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        # Add pagination context
        pagination_context = PaginationHelper.get_pagination_context(page_obj, request)
        context.update(pagination_context)
        
        # Document statistics
        stats = Document.objects.filter(user=user, is_deleted=False).aggregate(
            total=Count('id'),
            pending=Count('id', filter=Q(processing_status='pending')),
            processing=Count('id', filter=Q(processing_status='processing')),
            completed=Count('id', filter=Q(processing_status='completed')),
            failed=Count('id', filter=Q(processing_status='failed')),
            manual_review=Count('id', filter=Q(processing_status='manual_review'))
        )
        
        # Count deleted documents
        context['deleted_count'] = Document.objects.filter(
            user=user,
            is_deleted=True
        ).count()
        
        context['total_documents'] = stats['total']
        context['pending_documents'] = stats['pending']
        context['processing_documents'] = stats['processing']
        context['processed_documents'] = stats['completed']
        context['failed_documents'] = stats['failed']
        context['manual_review_documents'] = stats['manual_review']

        # Get currently processing document (oldest first - being processed now)
        context['current_processing_doc'] = Document.objects.filter(
            user=user,
            is_deleted=False,
            processing_status='processing'
        ).order_by('uploaded_at').first()
        
        # Use original documents with file_path
        context['documents'] = page_obj
        context['page_obj'] = page_obj
        
        # Filter values for form
        context['current_type'] = doc_type
        context['current_status'] = status
        context['current_search'] = search
        context['document_types'] = Document._meta.get_field('document_type').choices
        context['status_choices'] = Document._meta.get_field('processing_status').choices
        
        # Recent batches
        context['recent_batches'] = DocumentBatch.objects.filter(user=user)[:5]
        
        # Credit cards
        context['credit_cards'] = CreditCard.objects.filter(user=user)[:3]  # Show top 3
        
        # Subscriptions
        context['subscriptions'] = Subscription.objects.filter(user=user, is_active=True)[:5]
        context['monthly_subscriptions_total'] = sum(
            sub.amount if sub.billing_cycle == 'monthly' else sub.yearly_cost / 12
            for sub in context['subscriptions']
        )
        
        # Expense categories
        context['expense_categories'] = ExpenseCategory.objects.filter(
            user=user,
            parent__isnull=True
        )
        
        # Gamification data
        try:
            from .gamification_models import UserProfile, Achievement, Challenge, UserChallenge
            
            # Get or create user profile
            user_profile, created = UserProfile.objects.get_or_create(user=user)
            
            # User gamification stats
            context['user_points'] = user_profile.total_points
            context['user_rank'] = UserProfile.objects.filter(total_points__gt=user_profile.total_points).count() + 1
            context['user_achievements'] = user_profile.achievements.count()
            
            # Active challenges
            context['active_challenges'] = UserChallenge.objects.filter(
                user=user,
                completed=False,
                challenge__end_date__gte=timezone.now()
            ).count()
            
        except Exception as e:
            logger.warning(f"Could not load gamification data: {e}")
            context['user_points'] = 0
            context['user_rank'] = '∞'
            context['user_achievements'] = 0
            context['active_challenges'] = 0
        
        return render(request, self.template_name, context)


class DocumentListView(LoginRequiredMixin, BaseUIView):
    """List all documents with enhanced pagination and filtering"""
    template_name = 'documents/document_list.html'
    
    def get(self, request):
        context = self.get_context_data()
        
        # Get filter parameters
        doc_type = request.GET.get('type', '')
        status = request.GET.get('status', '')
        search = request.GET.get('search', '')
        
        # Build query
        documents = Document.objects.filter(user=request.user)
        
        if doc_type:
            documents = documents.filter(document_type=doc_type)
        if status:
            documents = documents.filter(processing_status=status)
        if search:
            documents = documents.filter(
                Q(original_filename__icontains=search) |
                Q(ocr_text__icontains=search)
            )
        
        # Dynamic pagination
        page_size = PaginationHelper.get_page_size(request)
        paginator = Paginator(documents, page_size)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        # Add pagination context
        pagination_context = PaginationHelper.get_pagination_context(page_obj, request)
        
        context.update(pagination_context)
        context.update({
            'page_obj': page_obj,
            'documents': page_obj.object_list,
            'total_count': paginator.count,
            'doc_type': doc_type,
            'status': status,
            'search': search,
            'document_types': Document._meta.get_field('document_type').choices,
            'status_choices': Document._meta.get_field('processing_status').choices,
        })
        
        return render(request, self.template_name, context)


class DocumentUploadView(LoginRequiredMixin, BaseUIView):
    """Handle document upload and OCR processing"""
    template_name = 'documents/upload.html'
    
    def post(self, request, *args, **kwargs):
        """Handle file upload with enhanced OCR and thumbnail generation"""
        # Check if this is an AJAX request (from dashboard quick upload)
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'multipart/form-data'

        if 'files' not in request.FILES:
            if is_ajax:
                return JsonResponse({'success': False, 'error': 'No files selected'}, status=400)
            messages.error(request, 'No files selected')
            return redirect('documents:upload')

        files = request.FILES.getlist('files')
        batch_name = request.POST.get('batch_name', f'Batch {timezone.now().strftime("%Y%m%d_%H%M")}')
        auto_ocr = request.POST.get('auto_ocr', 'true') == 'true'
        upload_only = request.POST.get('upload_only', 'false') == 'true'  # Quick upload mode - always process with OCR in background

        # Create batch - always start with processing status for background OCR
        batch = DocumentBatch.objects.create(
            user=request.user,
            batch_name=batch_name,
            total_documents=len(files),
            status='processing'
        )

        # Initialize processors
        thumbnail_generator = ThumbnailGenerator()
        uploaded = 0
        processed = 0
        failed = 0
        ocr_errors = []

        for file in files:
            try:
                # Get unique filename to avoid overwriting
                unique_filename = DocumentHelper.get_unique_filename(request.user, file.name)

                # Save document with 'processing' status - will be processed by background task
                document = Document.objects.create(
                    user=request.user,
                    document_type=request.POST.get('document_type', 'receipt'),
                    original_filename=unique_filename,
                    file_path=file,
                    processing_status='processing'  # Always processing for background OCR
                )

                # Generate thumbnail (quick operation)
                try:
                    thumb_file = thumbnail_generator.generate_thumbnail_from_django_file(
                        document.file_path,
                        str(document.id)
                    )
                    if thumb_file:
                        document.thumbnail_path.save(f"thumb_{document.id}.jpg", thumb_file, save=False)
                        logger.info(f"Thumbnail generated for document {document.id}")
                except Exception as e:
                    logger.error(f"Thumbnail generation failed for {document.id}: {e}")

                uploaded += 1
                document.save()

                # OCR will be processed in background automatically
                    
            except Exception as e:
                failed += 1
                logger.error(f'Error processing {file.name}: {str(e)}')
                messages.error(request, f'Error processing {file.name}: {str(e)}')
        
        # Update batch - leave as processing for background OCR
        batch.status = 'processing'
        batch.save()

        logger.info(f"uploaded {uploaded} documents for user {request.user.id}, ocr will process in background")

        # Prepare response data
        response_data = {
            'success': uploaded > 0,
            'total': len(files),
            'uploaded': uploaded,
            'processing': uploaded,  # All uploaded files are now processing
            'failed': failed,
            'batch_id': str(batch.id),
            'batch_name': batch_name,
        }

        # Return JSON for AJAX requests
        if is_ajax:
            return JsonResponse(response_data)

        # Provide detailed feedback for regular form submissions
        if uploaded > 0:
            messages.success(request, f'successfully uploaded {uploaded} document(s) - ocr processing started in background')

        if failed > 0:
            messages.warning(request, f'{failed} document(s) failed to upload')

        return redirect('documents:dashboard')
    
    def save_parsed_receipt(self, document, parsed_data):
        """Save parsed receipt data with advanced parser support"""
        # Parse dates if they're strings
        transaction_date = parsed_data.get('transaction_date')
        if isinstance(transaction_date, str):
            # Try to parse common Turkish date formats
            import re
            from datetime import datetime
            date_patterns = [
                (r'(\d{2})[/.-](\d{2})[/.-](\d{4})', '%d/%m/%Y'),
                (r'(\d{2})[/.-](\d{2})[/.-](\d{2})', '%d/%m/%y'),
                (r'(\d{4})[/.-](\d{2})[/.-](\d{2})', '%Y/%m/%d')
            ]
            for pattern, format_str in date_patterns:
                match = re.match(pattern, transaction_date.replace('-', '/').replace('.', '/'))
                if match:
                    try:
                        transaction_date = datetime.strptime(transaction_date.replace('-', '/').replace('.', '/'), format_str)
                        # Add time if available
                        if parsed_data.get('transaction_time'):
                            time_str = parsed_data['transaction_time']
                            time_match = re.match(r'(\d{1,2}):(\d{2})', time_str)
                            if time_match:
                                transaction_date = transaction_date.replace(
                                    hour=int(time_match.group(1)),
                                    minute=int(time_match.group(2))
                                )
                        break
                    except:
                        pass
        
        receipt = ParsedReceipt.objects.create(
            document=document,
            store_name=parsed_data.get('store_name', ''),
            store_address=parsed_data.get('store_address', ''),
            store_phone=parsed_data.get('store_phone', ''),
            store_tax_id=parsed_data.get('store_tax_id', ''),
            transaction_date=transaction_date,
            receipt_number=parsed_data.get('receipt_number', ''),
            cashier_id=parsed_data.get('cashier', ''),
            subtotal=parsed_data.get('subtotal'),
            tax_amount=parsed_data.get('tax_amount'),
            discount_amount=parsed_data.get('discount_amount'),
            total_amount=parsed_data.get('total_amount'),
            payment_method=parsed_data.get('payment_method', ''),
            card_last_digits=parsed_data.get('card_last_digits', ''),
            raw_ocr_data=parsed_data
        )
        
        # Save items with enhanced data
        for item_data in parsed_data.get('items', []):
            ReceiptItem.objects.create(
                receipt=receipt,
                name=item_data.get('name', ''),
                barcode=item_data.get('barcode', ''),
                quantity=item_data.get('quantity', 1),
                unit_price=item_data.get('unit_price', 0),
                total_price=item_data.get('total', item_data.get('total_price', 0)),
                tax_rate=item_data.get('kdv_rate', 18),
                category=item_data.get('category', '')
            )
        
        return receipt
    
    def integrate_with_modules(self, batch):
        """Enhanced cross-module integration for processed documents"""
        integrator = CrossModuleIntegrator()
        integration_results = []
        
        for document in Document.objects.filter(
            user=batch.user,
            processing_status='completed',
            uploaded_at__gte=batch.started_at  # Only process current batch documents
        ):
            if hasattr(document, 'parsed_receipt'):
                receipt = document.parsed_receipt
                result = {'document_id': document.id, 'integrations': {}}
                
                # Distribute data to other modules
                distributions = integrator.distribute_receipt_data(
                    receipt.raw_ocr_data,
                    batch.user.id
                )
                
                # Create WIMM transaction
                if distributions['wimm']:
                    try:
                        transaction = self.create_wimm_transaction(batch.user, distributions['wimm'][0], document)
                        result['integrations']['wimm'] = {'success': True, 'transaction_id': transaction.id if transaction else None}
                    except Exception as e:
                        result['integrations']['wimm'] = {'success': False, 'error': str(e)}
                
                # Update Kişisel Enflasyon prices
                if receipt.items.exists():
                    try:
                        inflation_records = self.create_inflation_records(batch.user, receipt)
                        result['integrations']['personal_inflation'] = {'success': True, 'records': inflation_records}
                    except Exception as e:
                        result['integrations']['personal_inflation'] = {'success': False, 'error': str(e)}
                
                # Update WIMS inventory
                if distributions['wims']:
                    try:
                        inventory_updates = self.update_inventory(batch.user, distributions['wims'], receipt)
                        result['integrations']['wims'] = {'success': True, 'updates': inventory_updates}
                    except Exception as e:
                        result['integrations']['wims'] = {'success': False, 'error': str(e)}
                
                # Handle foreign currency if detected
                if receipt.currency and receipt.currency != 'TRY':
                    try:
                        currency_record = self.create_currency_record(batch.user, receipt)
                        result['integrations']['currencies'] = {'success': True, 'record': currency_record}
                    except Exception as e:
                        result['integrations']['currencies'] = {'success': False, 'error': str(e)}
                
                integration_results.append(result)
        
        return integration_results
    
    def create_wimm_transaction(self, user, transaction_data, document=None):
        """Create WIMM transaction from receipt with enhanced data"""
        from modules.wimm.backend.models import Transaction, TransactionCategory
        from core.base.models.base import Account
        
        # Get appropriate account based on payment method
        payment_method = transaction_data.get('payment_method', 'cash')
        
        if payment_method in ['credit_card', 'debit_card']:
            # Try to match credit card by last 4 digits
            card_digits = transaction_data.get('card_digits', '')
            if card_digits:
                card = CreditCard.objects.filter(
                    user=user,
                    last_four_digits=card_digits
                ).first()
                if card:
                    # Get or create credit card account
                    account = Account.objects.filter(
                        user=user,
                        account_type='credit_card',
                        name__icontains=card.bank_name
                    ).first()
        
        if not 'account' in locals():
            # Get default account
            account = Account.objects.filter(user=user, is_default=True).first()
            if not account:
                account = Account.objects.filter(user=user).first()
        
        if account and transaction_data.get('amount'):
            # Get or create category
            category = None
            vendor = transaction_data.get('vendor', 'Unknown')
            if 'market' in vendor.lower() or 'migros' in vendor.lower() or 'a101' in vendor.lower():
                category = TransactionCategory.objects.filter(name='Groceries').first()
            
            transaction = Transaction.objects.create(
                user=user,
                transaction_type='expense',
                from_account=account,
                amount=transaction_data['amount'],
                description=f"Purchase at {vendor}",
                transaction_date=transaction_data.get('date', timezone.now()),
                payment_method=payment_method,
                category=category,
                document=document if document else None,
                metadata={
                    'source': 'ocr_import',
                    'receipt_number': transaction_data.get('receipt_number', ''),
                    'items_count': transaction_data.get('items_count', 0)
                }
            )
            return transaction
        return None
    
    def create_inflation_records(self, user, receipt):
        """Create enhanced personal inflation records with better categorization"""
        from modules.personal_inflation.backend.models import (
            Product, Store, PriceRecord,
            ProductCategory, PersonalBasket, BasketItem
        )
        from decimal import Decimal
        
        records_created = []
        
        # Get or create store with enhanced data
        store_name = receipt.store_name or 'Unknown Store'
        store_type = 'supermarket'
        
        # Determine store type based on name
        if any(x in store_name.lower() for x in ['migros', 'a101', 'bim', 'şok', 'carrefour']):
            store_type = 'supermarket'
        elif any(x in store_name.lower() for x in ['pharmacy', 'eczane']):
            store_type = 'pharmacy'
        elif any(x in store_name.lower() for x in ['restaurant', 'cafe', 'kebap']):
            store_type = 'restaurant'
        
        store, _ = Store.objects.get_or_create(
            name=store_name,
            defaults={
                'store_type': store_type,
                'address': receipt.store_address,
                'phone': receipt.store_phone
            }
        )
        
        # Smart category detection
        categories_map = {
            'gıda': ['süt', 'yoğurt', 'peynir', 'et', 'tavuk', 'balık', 'ekmek', 'meyve', 'sebze'],
            'temizlik': ['deterjan', 'sabun', 'şampuan', 'temizlik', 'çamaşır'],
            'kişisel bakım': ['diş', 'şampuan', 'krem', 'parfüm', 'deodorant'],
            'içecek': ['su', 'kola', 'çay', 'kahve', 'meyve suyu', 'ayran'],
            'atıştırmalık': ['çikolata', 'bisküvi', 'cips', 'kraker']
        }
        
        # Get or create categories
        categories = {}
        for cat_name in categories_map.keys():
            category, _ = ProductCategory.objects.get_or_create(
                name=cat_name.title(),
                defaults={'icon': '🛒', 'order': 100}
            )
            categories[cat_name] = category
        
        # Default category
        default_category, _ = ProductCategory.objects.get_or_create(
            name='Diğer',
            defaults={'icon': '📦', 'order': 999}
        )
        
        # Get user's default basket or create one
        basket = PersonalBasket.objects.filter(
            user=user, 
            is_default=True
        ).first()
        
        if not basket:
            basket = PersonalBasket.objects.create(
                user=user,
                name='Ana Sepet',
                is_default=True,
                is_active=True
            )
        
        # Process each receipt item
        for item in receipt.items.all():
            if not item.name or item.total_price <= 0:
                continue
            
            # Detect category
            item_category = default_category
            item_name_lower = item.name.lower()
            
            for cat_name, keywords in categories_map.items():
                if any(keyword in item_name_lower for keyword in keywords):
                    item_category = categories[cat_name]
                    break
            
            # Extract brand if possible
            brand = ''
            known_brands = ['ülker', 'eti', 'nestle', 'pınar', 'sütaş', 'danone']
            for b in known_brands:
                if b in item_name_lower:
                    brand = b.title()
                    break
            
            # Create or get product
            product, created = Product.objects.get_or_create(
                name=item.name,
                defaults={
                    'category': item_category,
                    'unit': item.unit or 'adet',
                    'brand': brand,
                    'barcode': item.barcode,
                    'is_active': True
                }
            )
            
            # Update receipt item with linked product
            item.linked_product_id = product.id
            item.category = item_category.name
            item.save()
            
            # Create price record
            price_record = PriceRecord.objects.create(
                product=product,
                store=store,
                user=user,
                price=item.unit_price if item.unit_price > 0 else item.total_price,
                currency=receipt.currency,
                source='ocr_import',
                recorded_at=receipt.transaction_date or timezone.now(),
                notes=f'Receipt #{receipt.receipt_number}' if receipt.receipt_number else 'OCR Import',
                metadata={
                    'document_id': str(receipt.document.id),
                    'confidence': receipt.document.ocr_confidence
                }
            )
            
            records_created.append(price_record.id)
            
            # Add to user's basket if not already there
            basket_item, created = BasketItem.objects.get_or_create(
                basket=basket,
                product=product,
                defaults={
                    'quantity': Decimal(str(item.quantity or 1)),
                    'frequency': 'monthly',
                    'is_active': True
                }
            )
            
            # Update basket item quantity if it exists and quantity increased
            if not created and item.quantity > basket_item.quantity:
                basket_item.quantity = Decimal(str(item.quantity))
                basket_item.save()
        
        return records_created
    
    def update_inventory(self, user, inventory_data, receipt):
        """Update WIMS inventory from receipt items with smart matching"""
        from modules.wims.backend.models import Item, ItemTransaction, Location, Category
        
        updates_made = []
        
        # Get default location
        default_location = Location.objects.filter(
            user=user,
            is_default=True
        ).first()
        
        if not default_location:
            default_location = Location.objects.filter(user=user).first()
            if not default_location:
                # Create default location
                default_location = Location.objects.create(
                    user=user,
                    name='Home',
                    location_type='home',
                    is_default=True
                )
        
        # Process inventory items
        for item_data in inventory_data:
            item_name = item_data['item_name']
            
            # Try to match existing inventory item
            existing_item = Item.objects.filter(
                user=user,
                name__icontains=item_name.split()[0]  # Match by first word
            ).first()
            
            if existing_item:
                # Update existing item quantity
                old_quantity = existing_item.quantity
                existing_item.quantity += Decimal(str(item_data['quantity_added']))
                existing_item.last_purchase_price = Decimal(str(item_data['purchase_price']))
                existing_item.last_purchase_date = item_data['purchase_date']
                existing_item.save()
                
                # Create transaction record
                transaction = ItemTransaction.objects.create(
                    item=existing_item,
                    transaction_type='purchase',
                    quantity=Decimal(str(item_data['quantity_added'])),
                    unit_price=Decimal(str(item_data['purchase_price'])),
                    location=default_location,
                    date=item_data['purchase_date'] or timezone.now(),
                    notes=f'Auto-imported from receipt #{receipt.receipt_number}'
                )
                
                # Link to receipt item
                receipt_item = receipt.items.filter(name=item_name).first()
                if receipt_item:
                    receipt_item.linked_stock_item_id = existing_item.id
                    receipt_item.save()
                
                updates_made.append({
                    'item_id': existing_item.id,
                    'item_name': existing_item.name,
                    'old_quantity': float(old_quantity),
                    'new_quantity': float(existing_item.quantity),
                    'transaction_id': transaction.id
                })
            else:
                # Check if this is a consumable item worth tracking
                consumables = ['deterjan', 'sabun', 'kağıt', 'peçete', 'tuvalet', 'çöp poşeti']
                should_track = any(c in item_name.lower() for c in consumables)
                
                if should_track:
                    # Create new inventory item
                    category = Category.objects.filter(
                        user=user,
                        name='Consumables'
                    ).first()
                    
                    if not category:
                        category = Category.objects.create(
                            user=user,
                            name='Consumables',
                            icon='🧻'
                        )
                    
                    new_item = Item.objects.create(
                        user=user,
                        name=item_name,
                        category=category,
                        quantity=Decimal(str(item_data['quantity_added'])),
                        unit='adet',
                        location=default_location,
                        last_purchase_price=Decimal(str(item_data['purchase_price'])),
                        last_purchase_date=item_data['purchase_date'],
                        notes='Auto-created from receipt import'
                    )
                    
                    # Link to receipt item
                    receipt_item = receipt.items.filter(name=item_name).first()
                    if receipt_item:
                        receipt_item.linked_stock_item_id = new_item.id
                        receipt_item.save()
                    
                    updates_made.append({
                        'item_id': new_item.id,
                        'item_name': new_item.name,
                        'new_item': True,
                        'quantity': float(new_item.quantity)
                    })
        
        return updates_made
    
    def create_currency_record(self, user, receipt):
        """Create currency record for foreign currency transactions"""
        from modules.currencies.backend.models import CurrencyTransaction
        
        if receipt.currency and receipt.currency != 'TRY':
            # Create currency transaction record
            transaction = CurrencyTransaction.objects.create(
                user=user,
                currency_code=receipt.currency,
                amount=receipt.total_amount,
                transaction_type='expense',
                transaction_date=receipt.transaction_date or timezone.now(),
                description=f'Purchase at {receipt.store_name}',
                source='ocr_import',
                metadata={
                    'document_id': str(receipt.document.id),
                    'receipt_number': receipt.receipt_number,
                    'store': receipt.store_name
                }
            )
            return transaction.id
        return None


class CreditCardManagementView(LoginRequiredMixin, BaseUIView):
    """Manage credit cards"""
    template_name = 'documents/credit_cards.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get all credit cards
        cards = CreditCard.objects.filter(user=user)
        
        # Calculate statistics
        total_limit = sum(card.credit_limit for card in cards)
        total_balance = sum(card.current_balance for card in cards)
        total_available = sum(card.available_credit for card in cards)
        
        context.update({
            'credit_cards': cards,
            'total_limit': total_limit,
            'total_balance': total_balance,
            'total_available': total_available,
            'overall_utilization': (total_balance / total_limit * 100) if total_limit > 0 else 0
        })
        
        return context
    
    def post(self, request, *args, **kwargs):
        """Add new credit card"""
        card = CreditCard.objects.create(
            user=request.user,
            bank_name=request.POST['bank_name'],
            card_name=request.POST['card_name'],
            last_four_digits=request.POST['last_four_digits'],
            card_type=request.POST['card_type'],
            credit_limit=request.POST['credit_limit'],
            current_balance=request.POST.get('current_balance', 0),
            available_credit=request.POST.get('available_credit', request.POST['credit_limit']),
            statement_day=request.POST['statement_day'],
            payment_due_day=request.POST['payment_due_day'],
            expiry_date=request.POST['expiry_date']
        )
        
        messages.success(request, f'Credit card {card.bank_name} ***{card.last_four_digits} added')
        return redirect('documents:credit_cards')


def prepare_structured_data(document):
    """Convert OCR parsed_data to structured_data format for template display"""
    structured_data = {
        'store_info': None,
        'transaction': None,
        'financial': None,
        'payment': None,
        'items_summary': None
    }
    
    try:
        # If ParsedReceipt exists, use it
        if hasattr(document, 'parsed_receipt') and document.parsed_receipt:
            receipt = document.parsed_receipt
            
            structured_data['store_info'] = {
                'name': receipt.store_name or 'Unknown Store',
                'address': receipt.store_address or '',
                'phone': receipt.store_phone or '',
                'tax_id': receipt.store_tax_id or ''
            }
            
            structured_data['transaction'] = {
                'date': receipt.transaction_date,
                'receipt_no': receipt.receipt_number or '',
                'cashier': receipt.cashier_id or ''
            }
            
            structured_data['financial'] = {
                'subtotal': receipt.subtotal or Decimal('0.00'),
                'tax': receipt.tax_amount or Decimal('0.00'),
                'discount': receipt.discount_amount or Decimal('0.00'),
                'total': receipt.total_amount or Decimal('0.00'),
                'currency': receipt.currency or 'TRY'
            }
            
            structured_data['payment'] = {
                'method': receipt.payment_method or 'unknown',
                'card_digits': receipt.card_last_digits or ''
            }
            
            structured_data['items_summary'] = {
                'count': receipt.items.count(),
                'categories': receipt.items.values('category').distinct().count(),
                'total_discount': sum(item.discount_amount or 0 for item in receipt.items.all())
            }
            
        # If no ParsedReceipt but OCR text exists, parse it
        elif document.ocr_text and document.document_type == 'receipt':
            from modules.documents.backend.ocr_service import OCRProcessor
            processor = OCRProcessor()
            
            # Try to parse the OCR text
            parsed_data = processor.parse_receipt(document.ocr_text)
            
            if parsed_data:
                # Convert parsed_data to structured_data format
                structured_data['store_info'] = {
                    'name': parsed_data.get('store_name', 'Unknown Store'),
                    'address': parsed_data.get('store_address', ''),
                    'phone': parsed_data.get('store_phone', ''),
                    'tax_id': parsed_data.get('store_tax_id', '')
                }
                
                # Handle transaction date
                transaction_date = parsed_data.get('transaction_date')
                if isinstance(transaction_date, str):
                    try:
                        # Try parsing common date formats
                        for fmt in ['%d/%m/%Y', '%d.%m.%Y', '%d-%m-%Y', '%Y-%m-%d']:
                            try:
                                transaction_date = datetime.strptime(transaction_date, fmt)
                                break
                            except ValueError:
                                continue
                    except:
                        transaction_date = None
                
                structured_data['transaction'] = {
                    'date': transaction_date,
                    'receipt_no': parsed_data.get('receipt_number', ''),
                    'cashier': parsed_data.get('cashier', '')
                }
                
                # Convert financial amounts to Decimal
                def to_decimal(value):
                    if value is None:
                        return Decimal('0.00')
                    if isinstance(value, (int, float)):
                        return Decimal(str(value))
                    if isinstance(value, str):
                        # Remove currency symbols and spaces
                        value = value.replace('₺', '').replace('TL', '').replace(',', '.').strip()
                        try:
                            return Decimal(value)
                        except:
                            return Decimal('0.00')
                    return Decimal('0.00')
                
                structured_data['financial'] = {
                    'subtotal': to_decimal(parsed_data.get('subtotal', 0)),
                    'tax': to_decimal(parsed_data.get('tax_amount', 0)),
                    'discount': to_decimal(parsed_data.get('discount_amount', 0)),
                    'total': to_decimal(parsed_data.get('total_amount', 0)),
                    'currency': parsed_data.get('currency', 'TRY')
                }
                
                structured_data['payment'] = {
                    'method': parsed_data.get('payment_method', 'unknown'),
                    'card_digits': parsed_data.get('card_last_digits', '')
                }
                
                # Items summary
                items = parsed_data.get('items', [])
                if items:
                    categories = set()
                    total_discount = Decimal('0.00')
                    
                    for item in items:
                        if item.get('category'):
                            categories.add(item['category'])
                        if item.get('discount_amount'):
                            total_discount += to_decimal(item['discount_amount'])
                    
                    structured_data['items_summary'] = {
                        'count': len(items),
                        'categories': len(categories),
                        'total_discount': total_discount
                    }
                else:
                    structured_data['items_summary'] = {
                        'count': 0,
                        'categories': 0,
                        'total_discount': Decimal('0.00')
                    }
                
    except Exception as e:
        logger.error(f"Error preparing structured data for document {document.id}: {e}")
    
    return structured_data


def get_receipt_items(document):
    """Get receipt items and categorize them"""
    items = []
    
    try:
        if hasattr(document, 'parsed_receipt') and document.parsed_receipt:
            # Get items from ParsedReceipt
            items = list(document.parsed_receipt.items.all().order_by('id'))
            
        elif document.ocr_text and document.document_type == 'receipt':
            # Parse OCR text to get items
            from .ocr_service import OCRProcessor
            processor = OCRProcessor()
            parsed_data = processor.parse_receipt(document.ocr_text)
            
            if parsed_data and parsed_data.get('items'):
                # Convert parsed items to ReceiptItem-like objects
                class MockReceiptItem:
                    def __init__(self, data):
                        self.name = data.get('name', '')
                        self.barcode = data.get('barcode', '')
                        self.quantity = data.get('quantity', 1)
                        self.unit_price = data.get('unit_price', 0)
                        self.total_price = data.get('total', data.get('total_price', 0))
                        self.tax_rate = data.get('kdv_rate', data.get('tax_rate', 18))
                        self.category = data.get('category', '')
                        self.discount_amount = data.get('discount_amount', 0)
                
                items = [MockReceiptItem(item) for item in parsed_data['items']]
                
    except Exception as e:
        logger.error(f"Error getting receipt items for document {document.id}: {e}")
    
    return items


def get_category_breakdown(items):
    """Get category breakdown from receipt items"""
    category_breakdown = {}
    
    try:
        for item in items:
            cat = item.category or 'Uncategorized'
            if cat not in category_breakdown:
                category_breakdown[cat] = {'count': 0, 'total': Decimal('0.00')}
            
            category_breakdown[cat]['count'] += 1
            
            # Handle both ReceiptItem objects and mock objects
            if hasattr(item, 'total_price'):
                total = item.total_price
                if isinstance(total, (int, float)):
                    total = Decimal(str(total))
                elif not isinstance(total, Decimal):
                    total = Decimal('0.00')
                category_breakdown[cat]['total'] += total
                
    except Exception as e:
        logger.error(f"Error calculating category breakdown: {e}")
    
    return category_breakdown


def check_integration_status(document):
    """Check which modules have integrated with this document"""
    status = {
        'wimm': False,
        'personal_inflation': False,
        'wims': False,
        'currencies': False
    }
    
    try:
        # Check WIMM integration
        try:
            from modules.wimm.backend.models import Transaction
            if Transaction.objects.filter(metadata__document_id=str(document.id)).exists():
                status['wimm'] = True
        except Exception as e:
            logger.debug(f"WIMM check failed: {e}")
        
        # Check Personal Inflation integration
        if hasattr(document, 'parsed_receipt') and document.parsed_receipt:
            receipt = document.parsed_receipt
            if receipt.items.filter(linked_product_id__isnull=False).exists():
                status['personal_inflation'] = True
        
        # Check WIMS integration
        if hasattr(document, 'parsed_receipt') and document.parsed_receipt:
            receipt = document.parsed_receipt
            if receipt.items.filter(linked_stock_item_id__isnull=False).exists():
                status['wims'] = True
        
        # Check for foreign currency
        if hasattr(document, 'parsed_receipt') and document.parsed_receipt:
            if document.parsed_receipt.currency and document.parsed_receipt.currency != 'TRY':
                status['currencies'] = True
                
    except Exception as e:
        logger.error(f"Error checking integration status for document {document.id}: {e}")
    
    return status


class DocumentDetailView(LoginRequiredMixin, BaseUIView):
    """View individual document details with enhanced data display"""
    template_name = 'documents/document_detail.html'
    
    def get(self, request, document_id):
        document = get_object_or_404(Document, id=document_id, user=request.user)
        
        context = self.get_context_data()
        context['document'] = document
        
        # Use the new helper function to prepare structured data
        structured_data = prepare_structured_data(document)
        context['structured_data'] = structured_data
        
        # Get receipt items using helper
        receipt_items = get_receipt_items(document)
        context['receipt_items'] = receipt_items
        
        # Get category breakdown using helper
        category_breakdown = get_category_breakdown(receipt_items)
        context['category_breakdown'] = category_breakdown
        
        # Check integration status using helper
        integration_status = check_integration_status(document)
        context['integration_status'] = integration_status
        
        # Add parsed_receipt to context if exists
        if hasattr(document, 'parsed_receipt') and document.parsed_receipt:
            context['parsed_receipt'] = document.parsed_receipt
        
        # If no parsed receipt but OCR text exists, try to create one
        if not hasattr(document, 'parsed_receipt') and document.ocr_text and document.document_type == 'receipt':
            from modules.documents.backend.ocr_service import OCRProcessor
            processor = OCRProcessor()
            
            try:
                # Parse the OCR text
                parsed_data = processor.parse_receipt(document.ocr_text)
                
                # Create ParsedReceipt if parsing successful and has minimum required data
                if parsed_data and (parsed_data.get('store_name') or parsed_data.get('total_amount')):
                    # Save the parsed receipt
                    upload_view = DocumentUploadView()
                    receipt = upload_view.save_parsed_receipt(document, parsed_data)
                    
                    if receipt:
                        # Refresh document to get the new ParsedReceipt
                        document.refresh_from_db()
                        context['parsed_receipt'] = receipt
                        
                        # Re-prepare structured data with the new ParsedReceipt
                        structured_data = prepare_structured_data(document)
                        context['structured_data'] = structured_data
                        
                        # Re-get receipt items
                        receipt_items = get_receipt_items(document)
                        context['receipt_items'] = receipt_items
                        
                        # Re-calculate category breakdown
                        category_breakdown = get_category_breakdown(receipt_items)
                        context['category_breakdown'] = category_breakdown
                        
                        # Re-check integration status
                        integration_status = check_integration_status(document)
                        context['integration_status'] = integration_status
                        
                        logger.info(f"Created ParsedReceipt for document {document.id} on detail view")
                
            except Exception as e:
                logger.error(f"Error creating ParsedReceipt on detail view for document {document.id}: {e}")
        
        # Get raw OCR data if available
        if document.ocr_text:
            # Format OCR text for better display
            context['formatted_ocr'] = self.format_ocr_text(document.ocr_text)
        
        # Add debug info if no structured data
        if not structured_data or not any(structured_data.values()):
            logger.warning(f"No structured data available for document {document.id}")
            if document.ocr_text:
                logger.debug(f"OCR text exists for document {document.id}, length: {len(document.ocr_text)}")
            else:
                logger.debug(f"No OCR text for document {document.id}")
        
        return render(request, self.template_name, context)
    
    
    def format_ocr_text(self, text):
        """Format OCR text for better readability"""
        # Split into lines and remove empty lines
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        return '\n'.join(lines)


class DocumentViewerView(LoginRequiredMixin, BaseUIView):
    """Serve document file for viewing"""
    
    def get(self, request, document_id):
        document = get_object_or_404(Document, id=document_id, user=request.user)
        
        # Check if file exists
        if not document.file_path:
            return HttpResponse("File not found", status=404)
        
        # Determine content type
        file_ext = document.original_filename.lower().split('.')[-1] if '.' in document.original_filename else 'jpg'
        content_types = {
            'pdf': 'application/pdf',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'bmp': 'image/bmp',
            'webp': 'image/webp',
        }
        content_type = content_types.get(file_ext, 'application/octet-stream')
        
        try:
            # Check if the file exists on disk
            if hasattr(document.file_path, 'path'):
                file_path = document.file_path.path
                if not os.path.exists(file_path):
                    logger.error(f"File not found on disk: {file_path}")
                    return HttpResponse("File not found on disk", status=404)
            
            # Return file response with proper headers
            response = FileResponse(
                document.file_path.open('rb'),
                content_type=content_type,
                as_attachment=False
            )
            
            # Set cache headers for better performance
            response['Cache-Control'] = 'public, max-age=3600'
            
            # Set content disposition for inline viewing
            response['Content-Disposition'] = f'inline; filename="{document.original_filename}"'
            
            return response
            
        except FileNotFoundError:
            logger.error(f"File not found for document {document_id}: {document.file_path}")
            return HttpResponse("File not found", status=404)
        except Exception as e:
            logger.error(f"Error serving document {document_id}: {str(e)}")
            return HttpResponse(f"Error loading file: {str(e)}", status=500)


class SubscriptionManagementView(LoginRequiredMixin, BaseUIView):
    """Manage subscriptions"""
    template_name = 'documents/subscriptions.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get all subscriptions
        subscriptions = Subscription.objects.filter(user=user)
        active_subscriptions = subscriptions.filter(is_active=True)
        
        # Calculate costs
        monthly_total = sum(
            sub.amount if sub.billing_cycle == 'monthly' else sub.yearly_cost / 12
            for sub in active_subscriptions
        )
        yearly_total = sum(sub.yearly_cost for sub in active_subscriptions)
        
        # Upcoming renewals
        upcoming_renewals = active_subscriptions.filter(
            next_billing_date__lte=timezone.now().date() + timedelta(days=7)
        ).order_by('next_billing_date')
        
        context.update({
            'subscriptions': subscriptions,
            'active_subscriptions': active_subscriptions,
            'monthly_total': monthly_total,
            'yearly_total': yearly_total,
            'upcoming_renewals': upcoming_renewals
        })
        
        return context
    
    def post(self, request, *args, **kwargs):
        """Add new subscription"""
        subscription = Subscription.objects.create(
            user=request.user,
            service_name=request.POST['service_name'],
            category=request.POST['category'],
            amount=request.POST['amount'],
            billing_cycle=request.POST['billing_cycle'],
            billing_day=request.POST['billing_day'],
            start_date=request.POST['start_date'],
            next_billing_date=request.POST['next_billing_date'],
            auto_renew=request.POST.get('auto_renew', 'on') == 'on'
        )
        
        messages.success(request, f'Subscription {subscription.service_name} added')
        return redirect('documents:subscriptions')

class RecycleBinView(LoginRequiredMixin, BaseUIView):
    """View deleted documents (soft delete)"""
    template_name = 'documents/recycle_bin.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()

        # Get deleted documents
        deleted_docs = Document.objects.filter(
            user=request.user,
            is_deleted=True
        ).order_by('-deleted_at')

        context.update({
            'deleted_documents': deleted_docs,
            'total_deleted': deleted_docs.count()
        })

        return render(request, self.template_name, context)


@require_POST
def select_ocr_method(request, document_id):
    """Select preferred OCR method for a document"""
    try:
        document = get_object_or_404(Document, id=document_id, user=request.user)

        # Get method from request body
        import json
        data = json.loads(request.body)
        method = data.get('method', '').lower()

        if method not in ['tesseract', 'ollama']:
            return JsonResponse({
                'success': False,
                'error': 'Invalid OCR method. Must be "tesseract" or "ollama"'
            }, status=400)

        # Update preferred method
        document.preferred_ocr_method = method

        # Update main OCR fields based on selected method
        if method == 'tesseract':
            document.ocr_text = document.tesseract_text or ''
            document.ocr_confidence = document.tesseract_confidence or 0
            # Update parsed data from tesseract
            if document.tesseract_parsed_data:
                # Create or update ParsedReceipt based on tesseract data
                if document.document_type == 'receipt':
                    from modules.documents.backend.ocr_service import OCRProcessor
                    processor = OCRProcessor()
                    processor.create_parsed_receipt(document, document.tesseract_parsed_data)
        elif method == 'ollama':
            document.ocr_text = document.ollama_text or ''
            document.ocr_confidence = document.ollama_confidence or 0
            # Update parsed data from ollama
            if document.ollama_parsed_data:
                # Create or update ParsedReceipt based on ollama data
                if document.document_type == 'receipt':
                    from modules.documents.backend.ocr_service import OCRProcessor
                    processor = OCRProcessor()
                    processor.create_parsed_receipt(document, document.ollama_parsed_data)

        document.save()

        logger.info(f"User {request.user.username} selected {method} as preferred OCR method for document {document_id}")

        return JsonResponse({
            'success': True,
            'method': method,
            'message': f'{method.capitalize()} selected as preferred OCR method'
        })

    except Exception as e:
        logger.error(f"Error selecting OCR method for document {document_id}: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


class DocumentAnalysisView(LoginRequiredMixin, BaseUIView):
    """
    Comprehensive OCR Analysis Comparison View
    Runs 4 different OCR methods and shows side-by-side comparison
    """
    template_name = 'documents/document_analysis.html'

    # OCR Method Configuration - Single source of truth
    OCR_METHODS = [
        {
            'id': 'paddleocr',
            'name': 'paddleocr',
            'title': 'paddleocr - çok dilli ocr, 80+ dil',
            'icon': '🚀',
            'description': 'çok dilli ocr, 80+ dil',
            'speed': '⚡ ~2-5s',
            'order': 1
        },
        {
            'id': 'tesseract',
            'name': 'tesseract',
            'title': 'tesseract - temel ocr motoru',
            'icon': '🔤',
            'description': 'temel ocr motoru',
            'speed': '⚡ ~1-3s',
            'order': 2
        },
        {
            'id': 'trocr',
            'name': 'trocr',
            'title': 'trocr - microsoft transformer, el yazısı',
            'icon': '✍️',
            'description': 'microsoft transformer, el yazısı',
            'speed': '🐢 ~15-30s',
            'order': 3
        },
        {
            'id': 'llama_vision',
            'name': 'llama 3.2-vision',
            'title': 'llama 3.2-vision - meta\'nın görsel ai\'ı',
            'icon': '🦙',
            'description': 'meta\'nın görsel ai\'ı',
            'speed': '🐢 ~180-200s',
            'order': 4
        },
        {
            'id': 'hybrid',
            'name': 'hybrid',
            'title': 'hybrid - paddleocr + llama vision',
            'icon': '🔄',
            'description': 'paddleocr + llama vision',
            'speed': '🐢 ~180-200s',
            'order': 5
        },
        {
            'id': 'donut',
            'name': 'donut',
            'title': 'donut - ocr-free transformer, naver clova',
            'icon': '🍩',
            'description': 'ocr-free transformer, naver clova',
            'speed': '🐌 ~30-60s',
            'order': 6
        },
        {
            'id': 'layoutlmv3',
            'name': 'layoutlmv3',
            'title': 'layoutlmv3 - layout-aware extraction, microsoft',
            'icon': '📐',
            'description': 'layout-aware extraction, microsoft',
            'speed': '🐌 ~40-80s',
            'order': 7
        },
        {
            'id': 'surya',
            'name': 'surya',
            'title': 'surya - all-in-one ocr, 90+ languages',
            'icon': '☀️',
            'description': 'all-in-one ocr, 90+ languages',
            'speed': '⚡ ~15-30s',
            'order': 8
        },
        {
            'id': 'doctr',
            'name': 'doctr',
            'title': 'doctr - modern pytorch ocr',
            'icon': '📚',
            'description': 'modern pytorch ocr',
            'speed': '⚡ ~10-20s',
            'order': 9
        },
        {
            'id': 'easyocr',
            'name': 'easyocr',
            'title': 'easyocr - multilingual fallback, 80+ languages',
            'icon': '✨',
            'description': 'multilingual fallback, 80+ languages',
            'speed': '⚡ ~5-15s',
            'order': 10
        },
        {
            'id': 'ocrmypdf',
            'name': 'ocrmypdf',
            'title': 'ocrmypdf - pdf-optimized tesseract',
            'icon': '📄',
            'description': 'pdf-optimized tesseract',
            'speed': '⚡ ~8-15s',
            'order': 11
        },
    ]

    def get(self, request, document_id, *args, **kwargs):
        document = get_object_or_404(Document, id=document_id, user=request.user, is_deleted=False)

        # Import analysis service
        from modules.documents.backend.analysis_service import OCRAnalysisService

        # Don't run any OCR methods on page load (user will select methods manually)
        analyzer = OCRAnalysisService()
        analysis_results = analyzer.analyze_document(document, methods_to_run=[])

        context = self.get_context_data()
        context['document'] = document
        context['analysis'] = analysis_results
        context['ocr_methods'] = self.OCR_METHODS  # Pass method config to template

        logger.info(f"User {request.user.username} viewed analysis comparison for document {document_id}")

        return render(request, self.template_name, context)
