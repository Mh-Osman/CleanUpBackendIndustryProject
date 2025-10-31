# from django.shortcuts import render

# # Create your views here.
# from rest_framework import viewsets, permissions
# from rest_framework.permissions import IsAuthenticated
# from .models import ClientCheckoutForm
# from .serializers import ClientCheckoutFormSerializer

# class persistentIsAuthenticated(permissions.BasePermission):
#     def has_permission(self, request, view):
#         #  user authenticated 
#         return request.user and request.user.is_authenticated
    
#     def has_object_permission(self, request, view, obj):
#         user = request.user
#         method = request.method

#         # Client can do all 
#         if user.user_type == 'client':
#             return obj.client == user  #  only object allowed

#         # Employee -> can only GET and PATCH their own records
#         elif user.user_type == 'employee':
#             if method in ['GET', 'PATCH']:
#                 return obj.special_service.worker == user or obj.subscription.employee == user
#             return False

#         # Admin -> can only GET and PATCH
#         elif user.is_staff or user.user_type == 'admin':
#             if method in ['GET', 'PATCH']:
#                 return True
#             return False

#         return False

# class ClientCheckoutFormViewSet(viewsets.ModelViewSet):
#     queryset = ClientCheckoutForm.objects.all()
#     serializer_class = ClientCheckoutFormSerializer
#     permission_classes = [IsAuthenticated]
  
#     def get_queryset(self):
        
#         user = self.request.user

#         if user.is_staff:
#             return ClientCheckoutForm.objects.all()
#         elif user.user_type in ['employee', 'supervisor']:
#             obj1 = ClientCheckoutForm.objects.filter(subscription__employee=user)
#             obj2 = ClientCheckoutForm.objects.filter(special_service__worker=user)
#             return obj1 | obj2
#         else:
#             return ClientCheckoutForm.objects.filter(client=user)
     
    

from rest_framework import viewsets, permissions
from .models import ClientCheckoutForm
from .serializers import ClientCheckoutFormSerializer


class PersistentIsAuthenticated(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        # POST block
        if request.method == 'POST' and (user.is_staff or user.user_type == 'admin'):
            return False  # Admin cannot POST

        return True

    def has_object_permission(self, request, view, obj):
        user = request.user
        method = request.method

        # Client -> can do everything on their own objects
        if user.user_type == 'client':
            return obj.client == user

        # Employee or Supervisor -> can only GET and PATCH related objects
        elif user.user_type in ['employee', 'supervisor']:
            if method in ['GET', 'PATCH']:
                return (
                    getattr(obj, 'special_service', None) and obj.special_service.worker == user
                ) or (
                    getattr(obj, 'subscription', None) and obj.subscription.employee == user
                )
            return False

        # Admin -> can only GET and PATCH any object
        elif user.is_staff or user.user_type == 'admin':
            return method in ['GET', 'PATCH']

        return False


class ClientCheckoutFormViewSet(viewsets.ModelViewSet):
    queryset = ClientCheckoutForm.objects.all()
    serializer_class = ClientCheckoutFormSerializer
    permission_classes = [PersistentIsAuthenticated]
    search_fields = ['form_name', 'form_type', 'client__name', 'client__email', 'subscription__plan__name',]

    def get_queryset(self):
        user = self.request.user

        if user.is_staff or user.user_type == 'admin':
            # Admin can see all
            return ClientCheckoutForm.objects.all()

        elif user.user_type in ['employee', 'supervisor']:
            obj1 = ClientCheckoutForm.objects.filter(subscription__employee=user)
            obj2 = ClientCheckoutForm.objects.filter(special_service__worker=user)
            return obj1 | obj2

        else:
            # Client can only see their own forms
            return ClientCheckoutForm.objects.filter(client=user)
