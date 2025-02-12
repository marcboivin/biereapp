from django.conf.urls.defaults import patterns, include, url
from django.contrib.auth.views import login, logout
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from biereapp import settings
from biereapp.views import Dashboard, CreerFacture, AddUserTransation, NewProduit, NewClient, FactureDetails, AddPrixProduit, FactureFermer, FactureInFermer, ProduitInventaire, CommandeFournisseur, Commande, AJAX_AddInventaire, AJAX_DeleteTransaction, super_facture
from biereapp.models import Facture, Produit, Client

admin.autodiscover()


#Values for generic views
liste_client = {
    'template_name': 'clients/liste.html',
    'queryset' : Client.objects.all()
}

single_client = {
    'queryset': Client.objects.all(),
    'template_name': 'clients/client.html',
    'template_object_name': 'client',
}

liste_factures = {
    'template_name': 'facture/liste.html',
    'queryset' : Facture.objects.order_by('-Date')
}

single_facture = {
    'queryset': Facture.objects.all(),
    'template_name': 'facture/facture.html',
    'template_object_name': 'facture',
}

liste_produit = {
    'template_name': 'produits/liste.html',
    'queryset' : Produit.objects.order_by('Brasseur', 'Nom')
}

single_produit = {
    'queryset': Produit.objects.all(),
    'template_name': 'produits/produit.html',
    'template_object_name': 'produit',
}

# Url patterns for generic views
urlpatterns = patterns('django.views.generic',
    (r'^clients/liste/', 'list_detail.object_list', liste_client),     
    (r'^clients/(?P<object_id>\d+)/$', 'list_detail.object_detail', single_client),
    (r'^factures/liste/', 'list_detail.object_list', liste_factures),  
    (r'^factures/(?P<object_id>\d+)/$', 'list_detail.object_detail', single_facture),   
    (r'^produits/liste/', 'list_detail.object_list', liste_produit),     
    (r'^produits/(?P<object_id>\d+)/$', 'list_detail.object_detail', single_produit),   
)

urlpatterns += patterns('',
    # Enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    (r'^accounts/login/$', login),
    (r'^accounts/logout/$', logout),
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT }),
    (r'^factures/creer/$', CreerFacture),
    (r'^factures/produit/ajout/$', AddUserTransation), 
    (r'^produits/creer/$', NewProduit),
    (r'^clients/creer/$', NewClient),
    (r'^factures/(?P<facture_id>\d+)/details/$', FactureDetails),
    (r'^factures/(?P<facture_id>\d+)/fermer/$', FactureFermer),
    (r'^factures/(?P<facture_id>\d+)/ouvrir/$', FactureInFermer),
    (r'^factures/super/$', super_facture),
    (r'^produits/(?P<object_id>\d+)/add/$', AddPrixProduit),
    (r'^produits/inventaire/$', ProduitInventaire),
    (r'^commandes/creer/$', CommandeFournisseur),
    (r'^commandes/$', Commande),
    (r'^ajax/inventaire/ajust/$', AJAX_AddInventaire),
    (r'^ajax/transactions/delete/$', AJAX_DeleteTransaction),
    (r'^$', Dashboard),


    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

)

