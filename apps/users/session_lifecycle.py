import ipaddress
import logging
from urllib.parse import urlencode

from django.conf import settings
from django.contrib.auth import logout
from django.http import JsonResponse
from django.shortcuts import redirect, resolve_url
from django.utils import timezone
from django.utils.crypto import salted_hmac


logger = logging.getLogger(__name__)

SESSION_STARTED_AT = '_eatfit_started_at'
SESSION_LAST_SEEN_AT = '_eatfit_last_seen_at'
SESSION_ROTATED_AT = '_eatfit_rotated_at'
SESSION_REMEMBERED = '_eatfit_remembered'
SESSION_USER_AGENT_HASH = '_eatfit_user_agent_hash'
SESSION_IP_PREFIX_HASH = '_eatfit_ip_prefix_hash'


def start_session_lifecycle(request, remember=False):
    """Initialize metadata for the authenticated browser session."""

    now = _now()
    request.session.cycle_key()
    request.session[SESSION_STARTED_AT] = now
    request.session[SESSION_LAST_SEEN_AT] = now
    request.session[SESSION_ROTATED_AT] = now
    request.session[SESSION_REMEMBERED] = bool(remember)
    request.session[SESSION_USER_AGENT_HASH] = _user_agent_hash(request)

    ip_prefix = _client_ip_prefix(request)
    if ip_prefix:
        request.session[SESSION_IP_PREFIX_HASH] = _stable_hash(ip_prefix)
    else:
        request.session.pop(SESSION_IP_PREFIX_HASH, None)

    if remember:
        request.session.set_expiry(settings.SESSION_REMEMBER_IDLE_TIMEOUT_SECONDS)
    else:
        request.session.set_expiry(0)
    request.session.modified = True


def apply_session_death_headers(response):
    if settings.SESSION_CLEAR_SITE_DATA_ON_LOGOUT:
        response.setdefault('Clear-Site-Data', '"cookies", "storage"')
    response.setdefault('Cache-Control', 'no-store, private')
    return response


class SessionLifecycleMiddleware:
    """Enforce idle timeout, absolute timeout, client binding, and key renewal."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if getattr(request, 'user', None) is not None and request.user.is_authenticated:
            reason = self._termination_reason(request)
            if reason:
                logger.warning(
                    "Terminating session for user_id=%s: %s",
                    request.user.pk,
                    reason,
                )
                return self._terminate(request, reason)

            self._ensure_metadata(request)
            self._renew_session_key_if_needed(request)
            self._touch(request)

        return self.get_response(request)

    def _ensure_metadata(self, request):
        if request.session.get(SESSION_STARTED_AT) and request.session.get(SESSION_LAST_SEEN_AT):
            return
        start_session_lifecycle(request, remember=False)

    def _termination_reason(self, request):
        self._ensure_metadata(request)

        now = _now()
        remembered = bool(request.session.get(SESSION_REMEMBERED))
        started_at = _timestamp(request.session.get(SESSION_STARTED_AT), now)
        last_seen_at = _timestamp(request.session.get(SESSION_LAST_SEEN_AT), now)

        idle_timeout = (
            settings.SESSION_REMEMBER_IDLE_TIMEOUT_SECONDS
            if remembered
            else settings.SESSION_IDLE_TIMEOUT_SECONDS
        )
        absolute_timeout = (
            settings.SESSION_REMEMBER_ABSOLUTE_TIMEOUT_SECONDS
            if remembered
            else settings.SESSION_ABSOLUTE_TIMEOUT_SECONDS
        )

        if idle_timeout > 0 and now - last_seen_at > idle_timeout:
            return 'idle_timeout'

        if absolute_timeout > 0 and now - started_at > absolute_timeout:
            return 'absolute_timeout'

        if settings.SESSION_BIND_USER_AGENT:
            expected = request.session.get(SESSION_USER_AGENT_HASH)
            current = _user_agent_hash(request)
            if expected and current and expected != current:
                return 'client_changed'

        if settings.SESSION_BIND_IP_PREFIX:
            expected = request.session.get(SESSION_IP_PREFIX_HASH)
            ip_prefix = _client_ip_prefix(request)
            current = _stable_hash(ip_prefix) if ip_prefix else ''
            if expected and current and expected != current:
                return 'client_changed'

        return ''

    def _renew_session_key_if_needed(self, request):
        interval = settings.SESSION_ROTATION_SECONDS
        if interval <= 0:
            return

        now = _now()
        rotated_at = _timestamp(request.session.get(SESSION_ROTATED_AT), now)
        if now - rotated_at <= interval:
            return

        request.session.cycle_key()
        request.session[SESSION_ROTATED_AT] = now
        request.session.modified = True

    def _touch(self, request):
        request.session[SESSION_LAST_SEEN_AT] = _now()
        if request.session.get(SESSION_REMEMBERED):
            request.session.set_expiry(settings.SESSION_REMEMBER_IDLE_TIMEOUT_SECONDS)
        request.session.modified = True

    def _terminate(self, request, reason):
        is_api = request.path.startswith('/api/')
        logout(request)

        if is_api:
            response = JsonResponse(
                {'detail': 'Session expired. Sign in again.', 'reason': reason},
                status=401,
            )
            return apply_session_death_headers(response)

        login_url = resolve_url(settings.LOGIN_URL)
        separator = '&' if '?' in login_url else '?'
        response = redirect(f"{login_url}{separator}{urlencode({'session': reason})}")
        return apply_session_death_headers(response)


def _now():
    return int(timezone.now().timestamp())


def _timestamp(value, default):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _user_agent_hash(request):
    return _stable_hash(request.META.get('HTTP_USER_AGENT', '')[:500])


def _stable_hash(value):
    if not value:
        return ''
    return salted_hmac('eatfit.session.lifecycle', value, secret=settings.SECRET_KEY).hexdigest()


def _client_ip_prefix(request):
    value = request.META.get('HTTP_X_FORWARDED_FOR') or request.META.get('REMOTE_ADDR', '')
    client_ip = value.split(',')[0].strip()
    if not client_ip:
        return ''

    try:
        address = ipaddress.ip_address(client_ip)
    except ValueError:
        return ''

    if address.version == 4:
        network = ipaddress.ip_network(f'{address}/24', strict=False)
    else:
        network = ipaddress.ip_network(f'{address}/64', strict=False)
    return str(network)
