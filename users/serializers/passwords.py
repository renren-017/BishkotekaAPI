from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomPasswordResetForm(PasswordResetForm):
    def send_mail(
        self,
        subject_template_name,
        email_template_name,
        context,
        from_email,
        to_email,
        html_email_template_name=None,
    ):
        pass


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        user = User.objects.filter(email=value).first()
        if not user:
            raise serializers.ValidationError("No user found with this email address.")
        return value

    def save(self):
        email = self.validated_data["email"]
        user = User.objects.get(email=email)
        token_generator = default_token_generator
        use_https = True
        request = self.context.get("request")
        reset_form = CustomPasswordResetForm({"email": email})
        if reset_form.is_valid():
            reset_form.save(
                use_https=use_https,
                token_generator=token_generator,
                request=request,
            )
        return user


class PasswordResetConfirmSerializer(serializers.Serializer):
    new_password1 = serializers.CharField(
        style={"input_type": "password"}, write_only=True
    )
    new_password2 = serializers.CharField(
        style={"input_type": "password"}, write_only=True
    )
