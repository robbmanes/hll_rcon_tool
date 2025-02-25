import os
from http.client import CannotSendRequest
from logging import getLogger
from xmlrpc.client import Fault, ServerProxy

from django.views.decorators.csrf import csrf_exempt

from rcon.discord import send_to_discord_audit

from .audit_log import record_audit
from .auth import api_response, login_required
from .decorators import permission_required, require_content_type, require_http_methods
from .utils import _get_data

logger = getLogger(__name__)

supervisor_client = None


def get_supervisor_client():
    global supervisor_client

    if not supervisor_client:
        url = os.getenv("SUPERVISOR_RPC_URL")
        if not url:
            raise ValueError("Can't start services, the url of supervisor isn't set")
        supervisor_client = ServerProxy(url)

    return supervisor_client


@csrf_exempt
@login_required()
@permission_required("api.can_view_available_services", raise_exception=True)
@require_http_methods(["GET"])
def get_services(request):
    info = {
        "broadcasts": "The automatic broadcasts.",
        "log_event_loop": "Blacklist enforcement, chat/kill forwarding, player history, etc...",
        "log_stream": "Optionally store game server logs in a redis stream",
        "auto_settings": "Applies commands automaticaly based on your rules.",
        "cron": "The scheduler, cleans logs and whatever you added.",
    }
    client = get_supervisor_client()

    try:
        processes = client.supervisor.getAllProcessInfo()
        result = [dict(info=info.get(p["name"], ""), **p) for p in processes]
    except:
        if os.getenv("DJANGO_DEBUG"):
            result = []
        else:
            raise
    return api_response(
        result=result,
        command="get_services",
        failed=False,
    )


@csrf_exempt
@login_required()
@permission_required("api.can_toggle_services", raise_exception=True)
@record_audit
@require_http_methods(["POST"])
@require_content_type()
def do_service(request):
    data = _get_data(request)
    client = get_supervisor_client()
    error = None
    res = None
    command_name = "do_service"
    failed = False

    actions = {
        "START": client.supervisor.startProcess,
        "STOP": client.supervisor.stopProcess,
    }
    action = data.get("action")
    service_name = data.get("service_name")

    if not action or action.upper() not in actions:
        failed = True
        return api_response(
            command=command_name,
            arguments=data,
            failed=failed,
            error="action must be START or STOP",
            status_code=400,
        )
    if not service_name:
        failed = True
        return api_response(
            command=command_name,
            arguments=data,
            failed=failed,
            error="service_name must be set",
            status_code=400,
        )

    try:
        res = actions[action.upper()](service_name)
        send_to_discord_audit(
            message=f"{service_name} {action}",
            command_name=f"service {action}",
            by=request.user.username,
        )
    except CannotSendRequest as e:
        error = "Service request already sent"
        logger.info(f"{error=}")
    except Fault as e:
        error = repr(e)

    return api_response(
        command=command_name,
        arguments=data,
        failed=failed,
        result=res,
        error=error,
    )
