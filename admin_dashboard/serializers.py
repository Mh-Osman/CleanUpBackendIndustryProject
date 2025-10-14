import calendar
from datetime import datetime
from rest_framework import serializers

class DashBoardTopSerializer(serializers.Serializer):
    year = serializers.IntegerField(required=False)
    month = serializers.CharField()

    def validate_month(self, value):
        month_name = value.title()
        try:
            month_number = list(calendar.month_name).index(month_name)
        except ValueError:
            raise serializers.ValidationError(
                "Make sure the month name is valid. Recheck the month name."
            )
        return month_number  # returns integer month

    def validate_year(self, value):
        if value is None:
            value = datetime.now().year
        return value
   