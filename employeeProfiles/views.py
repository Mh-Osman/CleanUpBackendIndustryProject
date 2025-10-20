from rest_framework import viewsets
from .models import CustomUser,EmployeeSalary, EmployeeProfile
from rest_framework.response import Response 
from rest_framework import status, decorators, response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from .serializers import EmployeeWithProfileSerializer , EmployeeSalarySerializer,EmployOverView 
from rest_framework.permissions import IsAdminUser,IsAuthenticated,SAFE_METHODS,BasePermission
from rest_framework.views import APIView
from invoice_request_from_client.models import InvoiceRequestFromEmployee
from django.db.models import Sum,Q

# from .models import EmployeeProfile, InvoiceRequestFromEmployee

# from invoice_request_from_client.models import InvoiceRequestFromEmployee
from plan.models import Subscription
from assign_task_employee.models import SpecialServicesModel

class CustomEmployeePermission(BasePermission):
    """
    Allow employees to view only their own profiles.
    """
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = EmployeeWithProfileSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['id','name', 'email', 'employee_profile__department', 'employee_profile__role']
    search_fields = ['name', 'email', 'employee_profile__national_id', 'employee_profile__contact_number']

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [IsAuthenticated()]
        elif self.request.method in ['PUT', 'PATCH']:
            return [CustomEmployeePermission()]
        else:
            return [IsAdminUser()]
        

class EmpployeeSalaryViewSet(viewsets.ModelViewSet):
    queryset = EmployeeSalary.objects.all()
    serializer_class = EmployeeSalarySerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['employee__name', 'employee_id','month', 'paid' , 'prime_phone' ,'shift' ]
    search_fields = ['employee__name', 'employee_id', 'month' , 'prime_phone' ]
    
    # Custom update by employee + month
    @decorators.action(detail=False, methods=["put", "patch"], url_path="update-by-employee")
    def update_by_employee(self, request):
        employee_id = request.data.get("employee_id")
        month = request.data.get("month")
        if not employee_id or not month:
            return response.Response({"error": "employee_id and month are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            salary = EmployeeSalary.objects.get(employee_id=employee_id, month=month)
        except EmployeeSalary.DoesNotExist:
            return response.Response({"error": "Salary not found for this employee in given month"}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy()
        data.pop("employee", None)
        data.pop("employee_id", None)
        data.pop("month", None)

        serializer = self.get_serializer(salary, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(serializer.data, status=status.HTTP_200_OK)

    # Optional: latest salary per employee
    @decorators.action(detail=False, methods=["get"], url_path="latest-by-employee/(?P<employee_id>[^/.]+)")
    def latest_by_employee(self, request, employee_id=None):
        salary = EmployeeSalary.objects.filter(employee_id=employee_id).order_by('-month').first()
        if not salary:
            return response.Response({"error": "No salary found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(salary)
        return response.Response(serializer.data)
    

class EmployeeOverviewViewset(APIView):
    permission_classes=[IsAdminUser]
    def get(self, request):

        tasks = SpecialServicesModel.objects.all()
        total_tasks = tasks.count() or 1  # avoid division by zero
        completed = tasks.filter(status='completed').count()
        started = tasks.filter(status='started').count()
        assigned = tasks.filter(status='pending').count()
        canceled = tasks.filter(status='canceled').count()

        # Simple performance formula
        average_performance = (
            (completed * 100 + started * 50 + assigned * 20 + canceled * 0) / total_tasks
        )
        overview = {
            "total_employee": EmployeeProfile.objects.all().count(),
            "active": EmployeeProfile.objects.filter(
                status='Active',
                user__user_type='employee'
            ).count(),
            "leave": EmployeeProfile.objects.filter(
               Q(is_on_leave=True) | Q(status='On Leave'),
                user__user_type='employee'
            ).count(),
            "total_payroll": InvoiceRequestFromEmployee.objects.filter(
                status="Submitted"
            ).aggregate(total=Sum('amount'))['total'] or 0,
            "average_performance": average_performance,
        }
        return Response(overview)



# from rest_framework import viewsets
# from rest_framework.response import Response
# from rest_framework.permissions import IsAdminUser
# from django.db.models import Q, Prefetch

# from locations.models import CustomUser, Region, Building, Apartment
# from assign_task_employee.models import SpecialServicesModel




# #osman provided the view below

# from locations.models import CustomUser, Region, Building, Apartment
# from assign_task_employee.models import SpecialServicesModel
# from plan.models import Subscription
 
 
# from rest_framework.permissions import IsAuthenticated
# class EmployeeRegionBuildingApartmentView(viewsets.ViewSet):
#     """
#     Returns regions -> buildings -> apartments
#     for employees with:
#         - Active subscriptions
#         - Services with status 'pending' or 'started'
#     Includes the status of subscription/service.
#     """
# <<<<<<< HEAD
   
#     permission_classes = [IsAuthenticated]
# =======
#     #permission_classes = [IsAdminUser]
# >>>>>>> origin/main

#     permission_classes = [IsAuthenticated]
    

# <<<<<<< HEAD
 
#     def list(self, request):
#         data = {}
 
#         # Filter active subscriptions and relevant services
#         active_subscriptions = Subscription.objects.filter(status='active')
#         active_services = SpecialServicesModel.objects.filter(status__in=['pending', 'started'])
 
#         # Get regions involved in either active subscriptions or services
#         region_ids = set(active_subscriptions.values_list('region_id', flat=True)) | \
#                      set(active_services.values_list('region_id', flat=True))
 
#         regions = Region.objects.filter(id__in=region_ids)
 
#         for region in regions:
#             region_dict = {}
#             buildings = Building.objects.filter(region=region)
 
#             for building in buildings:
#                 apartments_list = []
 
# =======
#     def list(self, request):
#         data = {}

#         # Filter active subscriptions and relevant services
#         active_subscriptions = Subscription.objects.filter(status='active')
#         active_services = SpecialServicesModel.objects.filter(status__in=['pending', 'started'])

#         # Get regions involved in either active subscriptions or services
#         region_ids = set(active_subscriptions.values_list('region_id', flat=True)) | \
#                     set(active_services.values_list('region_id', flat=True))

#         regions = Region.objects.filter(id__in=region_ids)

#         for region in regions:
#             region_dict = {
#                 "region_name": region.name,
#                 "buildings": {}
#             }

#             buildings = Building.objects.filter(region=region)

#             for building in buildings:
#                 apartments_list = []

# >>>>>>> origin/main
#                 # 1️⃣ Apartments with active subscriptions
#                 sub_apartments = Apartment.objects.filter(
#                     subscription__in=active_subscriptions.filter(building=building)
#                 ).distinct()
#                 for apt in sub_apartments:
#                     apartments_list.append({
#                         "apartment_number": apt.apartment_number,
#                         "status": "active",
#                     })

#                 # 2️⃣ Apartments with pending/started services
#                 service_apartments = Apartment.objects.filter(
#                     special_services_apartments__in=active_services.filter(building=building)
#                 ).distinct()
#                 for apt in service_apartments:
#                     matching_service = active_services.filter(building=building, apartment__in=[apt]).first()
#                     if matching_service:
#                         apartments_list.append({
#                             "apartment_number": apt.apartment_number,
#                             "status": matching_service.status,
#                         })

#                 # Deduplicate apartments
#                 seen = set()
#                 unique_apartments = []
#                 for apt in apartments_list:
#                     if apt["apartment_number"] not in seen:
#                         unique_apartments.append(apt)
#                         seen.add(apt["apartment_number"])

#                 if unique_apartments:
#                     region_dict["buildings"][building.id] = {
#                         "building_name": building.name,
#                         "address": building.location,
#                         "building_type": building.type,
#                         "city": building.city,
#                         "region_id": building.region.id,
#                         "latitude": str(building.latitude),
#                         "longitude": str(building.longitude),
#                         "apartments": unique_apartments,
#                     }

#             if region_dict["buildings"]:
#                 data[region.id] = region_dict

#         return Response(data)


