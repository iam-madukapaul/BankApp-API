# Generated by Django 4.2.15 on 2025-07-29 07:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="BankAccount",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "account_number",
                    models.CharField(
                        max_length=20, unique=True, verbose_name="Account Number"
                    ),
                ),
                (
                    "account_balance",
                    models.DecimalField(
                        decimal_places=2,
                        default=0.0,
                        max_digits=20,
                        verbose_name="Account Balance",
                    ),
                ),
                (
                    "currency",
                    models.CharField(
                        choices=[
                            ("us_dollar", "US Dollar"),
                            ("pound_sterling", "Pound Sterling"),
                            ("naira", "Naira"),
                        ],
                        max_length=20,
                        verbose_name="Currency",
                    ),
                ),
                (
                    "account_status",
                    models.CharField(
                        choices=[("active", "Active"), ("inactive", "Inactive")],
                        default="inactive",
                        max_length=10,
                        verbose_name="Account Status",
                    ),
                ),
                (
                    "account_type",
                    models.CharField(
                        choices=[("current", "Current"), ("savings", "Savings")],
                        max_length=20,
                        verbose_name="Account Type",
                    ),
                ),
                (
                    "is_primary",
                    models.BooleanField(default=False, verbose_name="Primary Account"),
                ),
                (
                    "kyc_submitted",
                    models.BooleanField(default=False, verbose_name="KYC Submitted"),
                ),
                (
                    "kyc_verified",
                    models.BooleanField(default=False, verbose_name="KYC Verified"),
                ),
                (
                    "verification_date",
                    models.DateField(
                        blank=True, null=True, verbose_name="Verification Date"
                    ),
                ),
                (
                    "verification_notes",
                    models.TextField(blank=True, verbose_name="Verification Notes"),
                ),
                (
                    "fully_activated",
                    models.BooleanField(default=False, verbose_name="Fully Activated"),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="bank_accounts",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "verified_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="verified_accounts",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Bank Account",
                "verbose_name_plural": "Bank Accounts",
                "unique_together": {("user", "currency", "account_type")},
            },
        ),
        migrations.CreateModel(
            name="Transaction",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "amount",
                    models.DecimalField(
                        decimal_places=2,
                        default=0.0,
                        max_digits=20,
                        verbose_name="Amount",
                    ),
                ),
                (
                    "description",
                    models.CharField(
                        blank=True,
                        max_length=500,
                        null=True,
                        verbose_name="Description",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("completed", "Completed"),
                            ("failed", "Failed"),
                        ],
                        default="pending",
                        max_length=20,
                        verbose_name="Status",
                    ),
                ),
                (
                    "transaction_type",
                    models.CharField(
                        choices=[
                            ("deposit", "Deposit"),
                            ("withdrawal", "Withdrawal"),
                            ("transfer", "Transfer"),
                            ("interest", "Interest"),
                        ],
                        max_length=20,
                        verbose_name="Type",
                    ),
                ),
                (
                    "receiver",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="received_transactions",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "receiver_account",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="received_transactions",
                        to="accounts.bankaccount",
                    ),
                ),
                (
                    "sender",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="sent_transactions",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "sender_account",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="sent_transactions",
                        to="accounts.bankaccount",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="transactions",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
                "indexes": [
                    models.Index(
                        fields=["created_at"], name="accounts_tr_created_b2c597_idx"
                    )
                ],
            },
        ),
    ]
