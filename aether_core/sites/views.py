# AetherVane Sites App — Views (API Endpoints)
# ==============================================
# These views handle CRUD operations for organizations, sites, and devices.
#
# CRUD = Create, Read, Update, Delete — the 4 basic data operations.
#
# MULTI-TENANT FILTERING (the key security feature):
# When a site_manager requests their sites, we filter the queryset to only
# show sites belonging to THEIR organization. They never see other orgs' data.
# This is enforced at the database query level — not just hidden in the UI.

import secrets
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from .models import Organization, Site, Device, Circuit
from .serializers import (
    OrganizationSerializer, SiteSerializer,
    DeviceSerializer, DeviceRegistrationSerializer, CircuitSerializer
)
from accounts.permissions import IsSuperAdmin, IsSiteManagerOrAbove


class OrganizationListCreateView(APIView):
    """
    GET  /api/v1/sites/organizations/ — List organizations
    POST /api/v1/sites/organizations/ — Create a new organization (super_admin only)
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if request.user.is_super_admin:
            orgs = Organization.objects.all().order_by('id')
        else:
            # Non-super-admins only see their own organization
            orgs = Organization.objects.filter(id=request.user.organization_id)
        
        serializer = OrganizationSerializer(orgs, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        if not request.user.is_super_admin:
            return Response(
                {'error': 'Only super admins can create organizations'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = OrganizationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SiteListCreateView(APIView):
    """
    GET  /api/v1/sites/ — List sites (filtered by tenant)
    POST /api/v1/sites/ — Create a new site
    """
    permission_classes = [IsSiteManagerOrAbove]
    
    def get(self, request):
        if request.user.is_super_admin:
            sites = Site.objects.all().order_by('id')
        else:
            # Filter to only this user's organization's sites
            sites = Site.objects.filter(organization=request.user.organization).order_by('id')
        
        serializer = SiteSerializer(sites, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        # Force the organization to the user's org (can't create sites for other orgs)
        if not request.user.is_super_admin:
            data = {**request.data, 'organization': request.user.organization_id}
        else:
            data = request.data
        
        serializer = SiteSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SiteDetailView(APIView):
    """
    GET    /api/v1/sites/<id>/ — View a specific site
    PUT    /api/v1/sites/<id>/ — Update a site
    DELETE /api/v1/sites/<id>/ — Delete a site
    """
    permission_classes = [IsAuthenticated]
    
    def _get_site_or_404(self, request, site_id):
        """Get a site, filtering by organization for non-super-admins."""
        try:
            if request.user.is_super_admin:
                return Site.objects.get(id=site_id)
            return Site.objects.get(id=site_id, organization=request.user.organization)
        except Site.DoesNotExist:
            return None
    
    def get(self, request, site_id):
        site = self._get_site_or_404(request, site_id)
        if not site:
            return Response({'error': 'Site not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = SiteSerializer(site)
        return Response(serializer.data)
    
    def put(self, request, site_id):
        if not request.user.is_site_manager and not request.user.is_super_admin:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        site = self._get_site_or_404(request, site_id)
        if not site:
            return Response({'error': 'Site not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = SiteSerializer(site, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, site_id):
        if not request.user.is_super_admin:
            return Response({'error': 'Only super admins can delete sites'}, status=status.HTTP_403_FORBIDDEN)
        
        site = self._get_site_or_404(request, site_id)
        if not site:
            return Response({'error': 'Site not found'}, status=status.HTTP_404_NOT_FOUND)
        
        site.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class DeviceListCreateView(APIView):
    """
    GET  /api/v1/sites/devices/ — List devices (filtered by tenant)
    POST /api/v1/sites/devices/ — Register a new device
    """
    permission_classes = [IsSiteManagerOrAbove]
    
    def get(self, request):
        if request.user.is_super_admin:
            devices = Device.objects.all().order_by('id')
        else:
            # Only show devices for this org's sites
            devices = Device.objects.filter(site__organization=request.user.organization).order_by('id')
        
        serializer = DeviceSerializer(devices, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        # Auto-generate a secure API token for the device
        # secrets.token_hex(32) generates a 64-character random string
        # This token is like a password for the ESP32 — it must send this
        # in the Authorization header when posting telemetry data
        data = {**request.data}
        
        serializer = DeviceRegistrationSerializer(data=data)
        if serializer.is_valid():
            # Verify the site belongs to this org (for non-super-admins)
            site_id = serializer.validated_data.get('site')
            if site_id and not request.user.is_super_admin:
                if site_id.organization_id != request.user.organization_id:
                    return Response(
                        {'error': 'You can only register devices for your own sites'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            
            # Generate the API token
            device = serializer.save()
            device.api_token = secrets.token_hex(32)
            device.device_status = 'offline'
            device.save()
            
            # Return with the token (shown once!)
            return Response(
                DeviceRegistrationSerializer(device).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeviceDetailView(APIView):
    """
    GET /api/v1/sites/devices/<id>/ — View a specific device
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, device_id):
        try:
            if request.user.is_super_admin:
                device = Device.objects.get(id=device_id)
            else:
                device = Device.objects.get(id=device_id, site__organization=request.user.organization)
        except Device.DoesNotExist:
            return Response({'error': 'Device not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = DeviceSerializer(device)
        return Response(serializer.data)


class CircuitListCreateView(APIView):
    """
    GET  /api/v1/sites/circuits/ — List circuits for a device
    POST /api/v1/sites/circuits/ — Create/update a circuit (name a relay channel)
    """
    permission_classes = [IsSiteManagerOrAbove]
    
    def get(self, request):
        device_id = request.query_params.get('device_id')
        if device_id:
            circuits = Circuit.objects.filter(device_id=device_id)
        else:
            circuits = Circuit.objects.all()
        
        serializer = CircuitSerializer(circuits, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = CircuitSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
