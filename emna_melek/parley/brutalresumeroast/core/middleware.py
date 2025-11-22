"""
Rate limiting middleware
"""
from django.core.cache import cache
from django.core.cache.backends.base import InvalidCacheBackendError
from django.http import JsonResponse
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
import logging

logger = logging.getLogger(__name__)


class RateLimitMiddleware(MiddlewareMixin):
    """
    Rate limit middleware: max 1 request per IP per 30 seconds
    Gracefully handles Redis connection errors
    """
    def process_request(self, request):
        if not settings.RATE_LIMIT_ENABLED:
            return None
        
        # Only rate limit POST requests to upload endpoint
        if request.method == 'POST' and request.path == '/upload/':
            try:
                ip_address = self.get_client_ip(request)
                cache_key = f'rate_limit_{ip_address}'
                
                # Try to check rate limit (may fail if Redis is down)
                try:
                    if cache.get(cache_key):
                        return JsonResponse({
                            'error': 'Rate limit exceeded. Please wait 30 seconds before uploading another resume.'
                        }, status=429)
                    
                    # Set rate limit
                    cache.set(cache_key, True, settings.RATE_LIMIT_PERIOD)
                    request.rate_limit_ip = ip_address
                except (ConnectionError, InvalidCacheBackendError, Exception) as e:
                    # Redis unavailable - skip rate limiting silently
                    # No logging needed - this is expected in development
                    pass
                    
            except Exception as e:
                # Any other error - silently allow request (don't spam logs)
                pass
        
        return None
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

