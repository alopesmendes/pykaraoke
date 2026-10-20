from collections.abc import Callable
from functools import wraps

from django.conf import settings
from django.http import Http404, HttpRequest, HttpResponse


def api_docs_only(view: Callable[..., HttpResponse]) -> Callable[..., HttpResponse]:
    """Answer 404 unless ENABLE_API_DOCS is on.

    Checked on every request, so a changed setting takes effect at once and
    the route is never reachable while the flag is off.
    """

    @wraps(view)
    def guarded(request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not settings.ENABLE_API_DOCS:
            raise Http404
        return view(request, *args, **kwargs)

    return guarded
