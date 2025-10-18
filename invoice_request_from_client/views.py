from django.shortcuts import render
from .models import InvoiceRequestFromEmployee
from .serializers import InvoiceRequestFromEmployeeSerializer
from rest_framework import viewsets
from rest_framework import permissions

class OnlyEmployeeCanPost(permissions.BasePermission):
    def has_permission(self,request, view):
        user=request.user
        if user.user_type=='employee' or user.is_staff:
            return True
        else:
            return False        
    def has_object_permission(self, request, view, obj):
        user=request.user
        return user.is_staff or obj.vendor==user

        




# Create your views here.
from rest_framework import filters

class InvoiceRequestFromEmployeeView(viewsets.ModelViewSet):
    queryset=InvoiceRequestFromEmployee.objects.select_related('vendor')
    serializer_class=InvoiceRequestFromEmployeeSerializer
    # permission_classes=[OnlyEmployeeCanPost()]
    filter_backends=[filters.SearchFilter,filters.OrderingFilter]
    filterset_fields=['expense_date','vendor__name','vendor__email','vendor__employee_profile__department','expense_category__name']

    search_fields=['vendor_name','vendor__email','vendor__employee_profile__department','discription','expense_category__name','status','amount']

    def get_permissions(self):
        user=self.request.user
        if not user.is_authenticated:
            return [permissions.IsAuthenticated()]
        if self.request.method in ['GET','POST']:
            return [OnlyEmployeeCanPost()]
        return [permissions.IsAdminUser()]
    

    def perform_create(self, serializer):
        serializer.save(vendor=self.request.user)
    



            