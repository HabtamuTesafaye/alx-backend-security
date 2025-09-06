from .models import RequestLog
from django.utils.timezone import now
from django.utils.deprecation import MiddlewareMixin
from ipware import get_client_ip

class IPLoggingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        ip, is_routable = get_client_ip(request)
        if ip is None:
            ip = "0.0.0.0"
        RequestLog.objects.create(
            ip_address=ip,
            path=request.path,
            timestamp=now()
        )
