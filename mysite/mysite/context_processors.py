"""
Import this context processor in settings TEMPLATE_CONTEXT_PROCESSORS
"""

def resolver_context_processor(request):
    return {
        'app_name': request.resolver_match.app_name,
        'namespace': request.resolver_match.namespace,
        'url_name': request.resolver_match.url_name
    }