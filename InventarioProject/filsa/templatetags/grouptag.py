from django import template

register = template.Library() 

# <app>/templatetags/my_tags.py


@register.simple_tag(takes_context=True)
def param_replace(context, **kwargs):
    """
    Return encoded URL parameters that are the same as the current
    request's parameters, only with the specified GET parameters added or changed.

    It also removes any empty parameters to keep things neat,
    so you can remove a parm by setting it to ``""``.

    For example, if you're on the page ``/things/?with_frosting=true&page=5``,
    then

    <a href="/things/?{% param_replace page=3 %}">Page 3</a>

    would expand to

    <a href="/things/?with_frosting=true&page=3">Page 3</a>

    Based on
    https://stackoverflow.com/questions/22734695/next-and-before-links-for-a-django-paginated-query/22735278#22735278
    """
    d = context['request'].GET.copy()
    print('d in context request is',d)
    print('kwars is', kwargs.items())
    for k, v in kwargs.items():
        #print('k in kwargs.items is', k)
        #print('v in kwargs.items is', v)
        d[k] = v
    #for k in [k for k, v in d.items() if not v]:
     #   del d[k]
        #print('k is',k)
        #print('v is', v)

        #print('d.items is', d.items()) 
    
    return d.urlencode()

@register.filter
def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists() 

# Antes estaba este condicional para mostrar los items de la navbar
#{% if request.user|has_group:"Administrador" %} 
#{% endif %}


@register.filter('startswith')
def startswith(text, starts):
    if isinstance(text, str):
        return text.startswith(starts)
    return False