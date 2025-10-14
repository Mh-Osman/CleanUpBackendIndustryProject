from rest_framework.serializers import Serializer
from plan.serializers import CalculationsForInvoice
from plan.models import InvoiceModel
from django.utils import timezone
from django.db.models.functions import ExtractMonth
from django.db.models import Sum
class AdminReportAnalysisView(Serializer):
    money=CalculationsForInvoice(read_only=True)
    year=timezone.now().year
    sales=InvoiceModel.objects.filter(
        created_at__year=year,type="ougoing"
        ).annotate(
            month=ExtractMonth("created_at")
            ).values(
                'month'

    ).aggregate(total_amount=Sum("total_amount"))["total_amount"]
    expense= InvoiceModel.objects.filter(
        created_at__year=year,type="incoming"
        ).annotate(
            month=ExtractMonth("created_at")
            ).values(
                'month'

    ).aggregate(total_amount=Sum("total_amount"))["total_amount"]





