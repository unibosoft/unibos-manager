"""
Enable gamification for existing documents
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from modules.documents.backend.models import Document
from modules.documents.backend.gamification_models import UserProfile, PointTransaction
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Enable gamification features for existing documents and award retroactive points'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--user',
            type=str,
            help='Username to process (if not specified, processes all users)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Run without making changes'
        )
    
    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        username = options.get('user')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))
        
        # Get users to process
        if username:
            users = User.objects.filter(username=username)
            if not users.exists():
                self.stdout.write(self.style.ERROR(f'User {username} not found'))
                return
        else:
            users = User.objects.all()
        
        total_points_awarded = 0
        total_documents_processed = 0
        
        for user in users:
            self.stdout.write(f'\nProcessing user: {user.username}')
            
            # Get or create user profile
            if not dry_run:
                profile, created = UserProfile.objects.get_or_create(user=user)
                if created:
                    self.stdout.write(self.style.SUCCESS(f'  Created profile for {user.username}'))
            
            # Process existing documents
            documents = Document.objects.filter(user=user, is_deleted=False)
            doc_count = documents.count()
            
            if doc_count == 0:
                self.stdout.write('  No documents found')
                continue
            
            self.stdout.write(f'  Found {doc_count} documents')
            
            # Award points for existing documents
            points_per_document = {
                'completed': 10,  # Successfully processed documents
                'manual_review': 5,  # Documents needing review
                'failed': 2,  # Failed documents still get some points for effort
                'pending': 1,  # Pending documents
                'processing': 1,  # Currently processing
            }
            
            user_points = 0
            
            for doc in documents:
                points = points_per_document.get(doc.processing_status, 1)
                
                # Bonus points for documents with OCR text
                if doc.ocr_text and len(doc.ocr_text) > 100:
                    points += 5  # Bonus for successful OCR
                
                # Bonus for receipts with parsed data
                if hasattr(doc, 'parsed_receipt') and doc.parsed_receipt:
                    points += 10  # Extra points for successfully parsed receipts
                    
                    # Additional points based on receipt completeness
                    receipt = doc.parsed_receipt
                    if receipt.store_name:
                        points += 2
                    if receipt.total_amount:
                        points += 3
                    if receipt.transaction_date:
                        points += 2
                    if hasattr(receipt, 'receipt_items') and receipt.receipt_items.count() > 0:
                        points += 5
                
                user_points += points
                total_documents_processed += 1
                
                if not dry_run:
                    # Create transaction record
                    PointTransaction.objects.create(
                        user=user,
                        points=points,
                        transaction_type='earned',
                        reason=f'Retroactive points for document: {doc.original_filename[:50]}',
                        related_document_id=doc.id,
                        metadata={'document_type': doc.document_type, 'status': doc.processing_status}
                    )
            
            if not dry_run:
                # Update user profile
                profile.total_points += user_points
                profile.receipts_processed += doc_count
                profile.save()
                
                # Check for level up
                new_level = profile.total_points // 1000 + 1
                if new_level > profile.current_level:
                    profile.current_level = new_level
                    profile.save()
                    self.stdout.write(self.style.SUCCESS(f'  User leveled up to {new_level}!'))
            
            total_points_awarded += user_points
            
            self.stdout.write(self.style.SUCCESS(
                f'  Awarded {user_points} points for {doc_count} documents'
            ))
        
        # Summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('GAMIFICATION ACTIVATION COMPLETE'))
        self.stdout.write(f'Total users processed: {users.count()}')
        self.stdout.write(f'Total documents processed: {total_documents_processed}')
        self.stdout.write(f'Total points awarded: {total_points_awarded}')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\nThis was a DRY RUN - no changes were made'))
            self.stdout.write('Run without --dry-run to apply changes')