# ip_tracking/admin_dashboard.py
from django.contrib.admin import AdminSite, ModelAdmin
from django.urls import path
from django.shortcuts import render
from django.db.models import Count
from .models import RequestLog, BlockedIP, SuspiciousIP
import json


# -------------------------
# Custom Admin Site
# -------------------------
class SecurityAdminSite(AdminSite):
    site_header = "ALX Backend Security Dashboard"
    site_title = "Security Admin"
    index_title = "Monitoring Console"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_view(self.dashboard_view), name='dashboard'),
        ]
        return custom_urls + urls

    def dashboard_view(self, request):
        # Metrics for dashboard
        top_ips_qs = (
            RequestLog.objects
            .values('ip_address')
            .annotate(count=Count('ip_address'))
            .order_by('-count')[:10]
        )
        top_ips = list(top_ips_qs)  # Convert QuerySet to list of dicts
        top_ips_json = json.dumps(top_ips)  # Convert list to JSON string

        blocked_ips = BlockedIP.objects.all()
        suspicious_ips = SuspiciousIP.objects.all()
        recent_requests = RequestLog.objects.order_by('-timestamp')[:50]
        
        total_requests = RequestLog.objects.count()
        blocked_count = blocked_ips.count()
        suspicious_count = suspicious_ips.count()
        normal_count = max(0, total_requests - suspicious_count - blocked_count)
        
        context = {
            'top_ips': top_ips_json,  # pass JSON string
            'blocked_ips': blocked_ips,
            'suspicious_ips': suspicious_ips,
            'recent_requests': recent_requests,
            'normal_traffic': normal_count,
            'suspicious_traffic': suspicious_count,
            'blocked_traffic': blocked_count,
        }
        return render(request, 'admin/analytics.html', context)


# -------------------------
# Admin Models
# -------------------------
class RequestLogAdmin(ModelAdmin):
    list_display = ('ip_address', 'path', 'timestamp', 'country', 'city')
    list_filter = ('timestamp', 'country', 'city')
    search_fields = ('ip_address', 'path', 'country', 'city')
    readonly_fields = ('ip_address', 'path', 'timestamp', 'country', 'city')

class BlockedIPAdmin(ModelAdmin):
    list_display = ('ip_address',)
    search_fields = ('ip_address',)

class SuspiciousIPAdmin(ModelAdmin):
    list_display = ('ip_address', 'reason', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('ip_address', 'reason')
    readonly_fields = ('ip_address', 'reason', 'timestamp')

# -------------------------
# Instantiate custom admin
# -------------------------
security_admin = SecurityAdminSite(name='security_admin')

# Register models with custom admin
security_admin.register(RequestLog, RequestLogAdmin)
security_admin.register(BlockedIP, BlockedIPAdmin)
security_admin.register(SuspiciousIP, SuspiciousIPAdmin)
