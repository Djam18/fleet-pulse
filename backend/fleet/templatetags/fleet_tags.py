from urllib.parse import urlencode

from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
    """
    Safely preserves current GET query parameters while updating specified keys.
    Essential for pagination alongside search queries and filter parameters.
    """
    request = context.get('request')
    if not request:
        return urlencode(kwargs)
    query = request.GET.dict()
    query.update(kwargs)
    return urlencode(query)


@register.filter
def smart_page_range(page_obj, delta=2):
    """
    Generates a smart pagination sequence with ellipses (e.g. 1, '...', 4, 5, 6, '...', 300).
    Django 4.2 Paginator.get_elided_page_range can also be leveraged directly.
    """
    if not page_obj:
        return []
    paginator = page_obj.paginator
    return paginator.get_elided_page_range(
        number=page_obj.number,
        on_each_side=delta,
        on_ends=1
    )
