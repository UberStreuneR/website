from django import template
register = template.Library()


@register.filter
def more_than_one_left(page_obj):
    if page_obj.paginator.num_pages - page_obj.number > 1:
        return True
    else:
        return False

@register.filter
def more_than_one_from_start(page_obj):
    if page_obj.number > 2:
        return True
    else:
        return False
