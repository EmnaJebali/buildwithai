"""
Views for BrutalResumeRoast
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .models import RoastResult
from .tasks import roast_resume_task
from .utils import pdf_to_text
import uuid
import os
import random
import json


def favicon(request):
    """Serve favicon to prevent 404 errors"""
    svg_favicon = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
        <text y=".9em" font-size="90">🔥</text>
    </svg>'''
    return HttpResponse(svg_favicon, content_type='image/svg+xml')


def index(request):
    """Home page with drag-and-drop upload"""
    return render(request, 'index.html')


@require_http_methods(["POST"])
def upload_resume(request):
    """
    Handle PDF upload, extract text, fire Celery task
    """
    if 'pdf' not in request.FILES:
        return JsonResponse({'error': 'No PDF file provided'}, status=400)
    
    pdf_file = request.FILES['pdf']
    
    # Validate file size (10MB max)
    if pdf_file.size > 10 * 1024 * 1024:
        return JsonResponse({'error': 'File too large. Maximum 10MB.'}, status=400)
    
    # Validate file type
    if not pdf_file.name.lower().endswith('.pdf'):
        return JsonResponse({'error': 'Only PDF files are allowed'}, status=400)
    
    try:
        # Generate unique task ID
        task_id = str(uuid.uuid4())
        
        # Save PDF
        filename = f"{task_id}_{pdf_file.name}"
        pdf_path = default_storage.save(f'uploads/{filename}', ContentFile(pdf_file.read()))
        full_path = os.path.join(settings.MEDIA_ROOT, pdf_path)
        
        # Get IP address for rate limiting
        ip_address = get_client_ip(request)
        
        # Create RoastResult record
        result = RoastResult.objects.create(
            task_id=task_id,
            status='pending',
            pdf_path=pdf_path,
            ip_address=ip_address
        )
        
        # Try to fire Celery task (gracefully handle if Celery/Redis unavailable)
        try:
            roast_resume_task.delay(task_id, full_path)
        except Exception as celery_error:
            # If Celery is unavailable, process synchronously as fallback
            import logging
            logger = logging.getLogger(__name__)
            # Only log at debug level - this is expected when Redis isn't running
            logger.debug(f'Celery unavailable. Processing synchronously.')
            # Process immediately without Celery
            from .tasks import process_roast
            try:
                process_roast(task_id, full_path)
            except Exception as sync_error:
                logger.error(f'Synchronous processing failed: {str(sync_error)}')
                # Mark as failed and show example roast
                result.status = 'failed'
                result.save()
        
        # Redirect to roasting page
        return redirect('roast', task_id=task_id)
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f'Upload error: {str(e)}', exc_info=True)
        
        # Check if it's a database error (table doesn't exist)
        error_msg = str(e)
        if 'no such table' in error_msg.lower() or 'does not exist' in error_msg.lower():
            error_msg = 'Database not set up. Please run: python manage.py migrate'
        elif 'Failed to extract text' in error_msg:
            error_msg = 'Could not read PDF file. Please ensure it is a valid PDF.'
        else:
            error_msg = f'Upload failed: {error_msg}'
        
        # Add error message and redirect back to index
        messages.error(request, error_msg)
        return redirect('index')


def roast_status(request, task_id):
    """
    HTMX polling endpoint to check roast status
    """
    result = get_object_or_404(RoastResult, task_id=task_id)
    
    if result.status == 'completed':
        return render(request, 'result.html', {'result': result})
    elif result.status == 'failed':
        # Fallback to example roast
        return render(request, 'result.html', {'result': get_example_result()})
    else:
        # Still processing - return status for HTMX polling
        return render(request, 'roasting.html', {'task_id': task_id, 'status': result.status})


def roast_page(request, task_id):
    """
    Main roasting page with HTMX polling
    """
    result = get_object_or_404(RoastResult, task_id=task_id)
    
    if result.status == 'completed':
        return render(request, 'result.html', {'result': result})
    elif result.status == 'failed':
        # Fallback to example
        return render(request, 'result.html', {'result': get_example_result()})
    else:
        return render(request, 'roasting.html', {'task_id': task_id, 'status': result.status})


def get_example_result():
    """
    Return a random example roast result for fallback
    """
    from .tasks import get_fallback_roast
    
    # Create a mock result object (not saved to DB)
    class MockResult:
        def __init__(self):
            self.task_id = 'example'
            self.status = 'completed'
            self.roast_text = get_fallback_roast()
            self.image_url = None
    
    return MockResult()


def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

