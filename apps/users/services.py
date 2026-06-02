from django.core.exceptions import PermissionDenied

from .models import HouseholdMembership


EDIT_ROLES = {HouseholdMembership.Role.OWNER, HouseholdMembership.Role.EDITOR}


def get_active_household(user):
    """Return a household for the user, creating one if necessary."""

    if not user.is_authenticated:
        return None
    return user.ensure_household()


def user_role(user, household):
    if not user.is_authenticated or not household:
        return None
    membership = HouseholdMembership.objects.filter(user=user, household=household).first()
    return membership.role if membership else None


def assert_household_member(user, household):
    if user.is_superuser:
        return
    if user_role(user, household) is None:
        raise PermissionDenied("You do not have access to this household.")


def assert_household_editor(user, household):
    """Raise PermissionDenied when the user cannot change household data."""

    if user.is_superuser:
        return
    if user_role(user, household) not in EDIT_ROLES:
        raise PermissionDenied("You do not have permission to change this household.")


def add_member_by_username(household, username, role=HouseholdMembership.Role.EDITOR):
    """Add an existing user account to the household with the selected role."""

    from .models import User

    user = User.objects.get(username=username)
    membership, _ = HouseholdMembership.objects.update_or_create(
        user=user,
        household=household,
        defaults={'role': role},
    )
    if not user.household_id:
        user.household = household
        user.save(update_fields=['household'])
    return membership
