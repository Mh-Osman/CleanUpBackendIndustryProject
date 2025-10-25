from rest_framework import serializers
from .models import FormNameModel, FormFieldModel, FormSubmissionModel
from django.contrib.auth import get_user_model
User = get_user_model()


class FormFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormFieldModel
        fields = '__all__'
        extra_kwargs = {
            'form': {'required': False}  # 👈 this line is critical
        }


class FormNameSerializer(serializers.ModelSerializer):
    fields = FormFieldSerializer(many=True)

    class Meta:
        model = FormNameModel
        fields = '__all__'

    def create(self, validated_data):
        fields_data = validated_data.pop('fields', [])
        form = FormNameModel.objects.create(**validated_data)

        for field_data in fields_data:
            FormFieldModel.objects.create(form=form, **field_data)

        return form
    
    def update(self, instance, validated_data):
        fields_data = validated_data.pop('fields', [])
        
        # Update form name fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update form fields
        existing_field_ids = [field.id for field in instance.fields.all()]
        new_field_ids = []

        for field_data in fields_data:
            field_id = field_data.get('id', None)
            if field_id and field_id in existing_field_ids:
                # Update existing field
                field = FormFieldModel.objects.get(id=field_id, form=instance)
                for attr, value in field_data.items():
                    setattr(field, attr, value)
                field.save()
                new_field_ids.append(field_id)
            else:
                # Create new field
                field = FormFieldModel.objects.create(form=instance, **field_data)
                new_field_ids.append(field.id)

        # Delete fields that are not in the new data
        for field_id in existing_field_ids:
            if field_id not in new_field_ids:
                FormFieldModel.objects.get(id=field_id, form=instance).delete()

        return instance 



from rest_framework import serializers
from .models import FormSubmissionModel

class FormSubmissionSerializer(serializers.ModelSerializer):
    form_name = serializers.ReadOnlyField(source='form.form_name')
    response_user_name = serializers.ReadOnlyField(source='response_user.name')  # <-- correct field

    class Meta:
        model = FormSubmissionModel
        fields = ['id', 'form', 'form_name', 'response_user', 'response_user_name', 'data', 'submitted_at']
