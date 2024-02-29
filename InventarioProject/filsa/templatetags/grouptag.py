from django import template

register = template.Library() 

@register.filter
def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists() 

# Antes estaba este condicional para mostrar los items de la navbar
#{% if request.user|has_group:"Administrador" %} 
#{% endif %}