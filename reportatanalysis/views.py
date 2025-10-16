from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models.functions import ExtractMonth
from django.db.models import Sum
from django.utils import timezone
from plan.models import InvoiceModel,Subscription


class AdminReportAnalysisView(APIView):
    def get(self, request):
        year = timezone.now().year
        
        # Sales grouped by month
        sales_data = InvoiceModel.objects.filter(
            created_at__year=year, type="outgoing"
        ).annotate(
            month=ExtractMonth('created_at')
        ).values('month').annotate(
            sales=Sum('total_amount')
        ).order_by('month')

        # Expenses grouped by month
        expense_data = InvoiceModel.objects.filter(
            created_at__year=year, type="incoming"
        ).annotate(
            month=ExtractMonth('created_at')
        ).values('month').annotate(
            expense=Sum('total_amount')
        ).order_by('month')

        # Combine sales and expense per month
        result = []
        months = set([d['month'] for d in sales_data] + [d['month'] for d in expense_data])
        for month in sorted(months):
            month_sales = next((d['sales'] for d in sales_data if d['month'] == month), 0)
            month_expense = next((d['expense'] for d in expense_data if d['month'] == month), 0)
            result.append({
                'month': month,
                'sales': month_sales or 0,
                'expense': month_expense or 0
            })
        
        sales=InvoiceModel.objects.filter(type="outgoing").aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        expense=InvoiceModel.objects.filter(type="incoming").aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        basic=Subscription.objects.filter(plan__plan_code=101).count()
        pro=Subscription.objects.filter(plan__plan_code=102).count()
        standard=Subscription.objects.filter(plan__plan_code=103).count()
        active_subscription=Subscription.objects.filter(status='active').count()
        
        
        return Response({
            "total_sales":sales,
            "total_expense":expense,
            "sales_vs_expense_data":result,
            "basic":basic,
            "pro":pro,
            "standard":standard,
            "active_subscription":active_subscription
        })
