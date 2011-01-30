from django import template
from biereapp import settings
from biereapp.models import BiereUser, Facture, TYPE_TRANS, Prix, PrixForm
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.template.defaultfilters import stringfilter
from types import *
from locale import currency
from decimal import Decimal
from biereapp.middleware import GlobalUser

register = template.Library()

@register.simple_tag
def get_path(which):
    return settings.MEDIA_PATHS[which.upper()]
    
@register.simple_tag
def transaction_form(facture):
    print facture.id
    if(facture.id > 0):
        print 'Higher then 0'
        return facture.transaction_form( )
        
@register.simple_tag
def get_user_facture(biere_user, count=False):

    if type(biere_user) is User:
        biere_user = BiereUser(id=biere_user.id)

    if type(biere_user) is BiereUser:
        return biere_user.get_facture(count)
        
    return False

@register.simple_tag
def trans_type(code):
    for t in TYPE_TRANS:
        if t[0] == code:
            return t[1]
    
    
# Function prefixed by design are only to create markup
# not used
@register.filter
def design_ribbon(string, heading_number):
    """
        Ribbon header
        heading_number is the integer of the H you want (h1,h2,h3,h4,h5,h6)
    """
    # Make sure we have a integer
    h = int(h)
    
    template = render_to_string("snippets/ribbons.html", {'h': heading_number, 's': string})
    return template

@register.simple_tag
def gravatar( user=None, size = 96): 
    # No user given
    if user is None:
        u= UserMethods( )
        return u.get_gravatar_url(size)
        
    if isinstance(user, User):
        # ToDo: Find a more elegant way to solve this case:
        # No matching user. If there is one we loop and return the first
        # Becasue anyway there can only be one user 
        u = UserMethods.objects.filter(username=user.username)
        for user in u:
            return user.get_gravatar_url(size)
    
        u= UserMethods( )
    else : 
        # Its a string, because I say so
        u= UserMethods( )
        u.email = user
    return u.get_gravatar_url(size)

@register.simple_tag    
def get_main_menu():
    try:
        User = GlobalUser.user
    except NameError:
        raise Exception(u"Erreur fatale, le Middleware GlobalUser n'est pas actif, impossible de faire des sauvegardes.") 
        
    return render_to_string('snippets/menu.html', {'user': User})
    
    
@register.simple_tag
def facture_summary(number=10, template="default.html"):
    #if type(user) is User:
    #    user = BiereUser(id=user.id)

    #if type(user) is BiereUser:
    #    return user.show_user_facture(GET)
    
    # Get Facture based on the number needed
    factures = Facture.objects.all()[0:number-1]
    return render_to_string("snippets/facture_summary/"+template, {'factures':factures, 'number': number})    

@register.simple_tag
def list_prix(produit):
    if type(produit) is not int:
        return false
    
    qs = Prix.objects.filter(Produit=produit)
    
    return render_to_string("snippets/liste_prix_produit.html", {'prix': qs})

@register.simple_tag
def prix_form(produit):
    if type(produit) is not int:
        return false
        
    return PrixForm({'Produit': produit}).as_ul()
    
@register.filter(name='monetize')
@stringfilter    
def monetize(value):
    """
        Applies money style to a number. Only the current local is supported
        Beware... 
    """
    
    if settings.DEBUG:
        print "monetize: " + str(value)
    
    if type(value) is int:
        value = Decimal(value)
    
    if value == "":
        return 0
    
    # NaN we return 0
    if type(value) is not Decimal:
        value = Decimal(value)
    
    return currency( value, grouping=True )
        
"Mark string as safe"
monetize.is_safe = True

"""
@register.simple_tag
def get_url(io, action = "view"):
	from django.contrib.sites.models import Site
	url = ['http://']
	cur_site = Site.objects.get(id=settings.SITE_ID)
	url.append(cur_site.domain)

	if action != "view":
		url.append(action)
		url.appends('/')

	url.append(io.lien)
	
	return ''.join(url)
"""