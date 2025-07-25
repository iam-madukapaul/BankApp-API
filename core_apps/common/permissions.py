from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import View


class IsUserRole(permissions.BasePermission):
    required_role = None

    def has_permission(self, request: Request, view: View) -> bool:
        return (
            request.user.is_authenticated
            and hasattr(request.user, "role")
            and request.user.role == self.required_role
        )


class IsAccountExecutive(IsUserRole):
    required_role = "account_executive"


class IsTeller(IsUserRole):
    required_role = "teller"


class IsBranchManager(IsUserRole):
    required_role = "branch_manager"
