from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from .models import BankAccount


class AccountVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        fields = [
            "kyc_submitted",
            "kyc_verified",
            "verification_date",
            "verification_notes",
            "fully_activated",
            "account_status",
        ]
        read_only_fields = ["fully_activated"]

    def validate(self, data: dict) -> dict:
        kyc_verified = data.get("kyc_verified")
        verification_date = data.get("verification_date")
        verification_notes = data.get("verification_notes")

        if kyc_verified:
            missing_fields = []
            if not verification_date:
                missing_fields.append("verification_date")
            if not verification_notes:
                missing_fields.append("verification_notes")
            if missing_fields:
                raise serializers.ValidationError(
                    {
                        field: _(
                            f"{field.replace('_', ' ').capitalize()} is required when verifying an account."
                        )
                        for field in missing_fields
                    }
                )

        return data
