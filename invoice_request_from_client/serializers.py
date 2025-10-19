from .models import InvoiceRequestFromEmployee
from rest_framework import serializers


class InvoiceRequestFromEmployeeSerializer(serializers.ModelSerializer):
    expense_date=serializers.DateField(format="%m/%d/%Y",input_formats=["%m/%d/%Y"])
    vendor=serializers.SerializerMethodField(read_only=True)
    category_show_by_name=serializers.StringRelatedField(many=True,source='expense_category',read_only=True)
    class Meta:
        model=InvoiceRequestFromEmployee
        fields='__all__'
        # read_only_fields=['category_show_by_name']
    

    def get_vendor(self,obj):
        data=[]
        if obj.vendor:
            data.append(obj.vendor.id)
            data.append(obj.vendor_name)
        return data