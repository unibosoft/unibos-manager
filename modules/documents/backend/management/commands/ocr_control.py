"""
OCR Processing Control - Pause/Resume mechanism
"""
import os
from django.core.management.base import BaseCommand
from django.core.cache import cache


class Command(BaseCommand):
    help = 'Control OCR background processing (pause/resume/status)'

    def add_arguments(self, parser):
        parser.add_argument(
            'action',
            type=str,
            choices=['pause', 'resume', 'status'],
            help='Action to perform: pause, resume, or status'
        )

    def handle(self, *args, **options):
        action = options['action']
        
        if action == 'pause':
            cache.set('ocr_processing_paused', True, timeout=None)
            self.stdout.write(self.style.WARNING('⏸️  OCR processing PAUSED'))
            self.stdout.write('Background OCR will stop after current document.')
            
        elif action == 'resume':
            cache.delete('ocr_processing_paused')
            self.stdout.write(self.style.SUCCESS('▶️  OCR processing RESUMED'))
            self.stdout.write('Background OCR will continue processing.')
            
        elif action == 'status':
            is_paused = cache.get('ocr_processing_paused', False)
            if is_paused:
                self.stdout.write(self.style.WARNING('Status: ⏸️  PAUSED'))
            else:
                self.stdout.write(self.style.SUCCESS('Status: ▶️  RUNNING'))
