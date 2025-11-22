"""
Management command to delete PDFs older than 1 hour
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from core.models import RoastResult
import os
from datetime import timedelta


class Command(BaseCommand):
    help = 'Delete PDFs and results older than 1 hour'

    def handle(self, *args, **options):
        cutoff_time = timezone.now() - timedelta(hours=1)
        
        # Find old results
        old_results = RoastResult.objects.filter(created_at__lt=cutoff_time)
        
        deleted_count = 0
        for result in old_results:
            # Delete PDF file
            if result.pdf_path:
                pdf_full_path = os.path.join(settings.MEDIA_ROOT, result.pdf_path)
                if os.path.exists(pdf_full_path):
                    try:
                        os.remove(pdf_full_path)
                        deleted_count += 1
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f'Failed to delete {pdf_full_path}: {e}'))
            
            # Delete result record
            result.delete()
        
        self.stdout.write(self.style.SUCCESS(f'Successfully deleted {deleted_count} old files and records'))

