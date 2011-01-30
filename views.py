# This Python file uses the following encoding: utf-8
from django.http import HttpResponse, HttpResponseServerError, HttpResponseRedirect
from django.core.cache import cache
from django.template.loader import get_template
from django.shortcuts import render_to_response
from django.template import Template, RequestContext
from django.conf import settings
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required

#from io.exceptions import IOPasswordProtected
#from io import signals
from biereapp.models import FactureForm, Facture, CommandeProduitForm, Transaction, Prix, ProduitForm, Produit, TransactionForm, ClientForm, PrixForm
from biereapp import models

from biereapp.models import logit

@login_required
def Dashboard(request):
    return render_to_response('dashboard.html', { 'user': request.user })
    
@login_required
def CreerCommande(request):
    created = False
    facture = False
    # There is a new commande to create
    if request.method == 'POST':
        factureform = FactureForm(request.POST)
        if factureform.is_valid():
            bill 		        = factureform.save( commit=False )
            bill.User           = request.user
            bill.save()
            created 	        = True
            facture				= bill
    else:
        factureform = FactureForm()
        facture 	= Facture() 
        commande    = False
        produits    = False
		
    return render_to_response('facture/new.html', {'created':created, 'factureform': factureform, 'user': request.user, 'facture': facture })
    
@login_required
def AddUserTransation(request):
    """Ajoute un produit à une commande"""
    facture             = False
    commande            = TransactionForm( request.POST )
    print request.POST
    # transaction to add
    # ToDo: Save the form in a instance of the Transaction model! Or make the ModelForm and override the __init__
    if commande.is_valid():
        transaction         = commande.save()
        facture             = transaction.Facture
        # Ajoute comme une commande
        #transaction.add_to_commande( )
        transaction.save()

    if not facture:
        facture = commande
        
    template_var = { 'user': request.user, 'facture': facture }
    
    # Detects AJAX requests made from jQuery (which I use in this program)
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        return render_to_response('facture/add_produit.ajax', template_var)
        
    return render_to_response('facture/facture.html', template_var)
    
@login_required
def NewProduit(request):
    created = False
    if request.method == 'POST':
        produit = ProduitForm(request.POST)
        if produit.is_valid():
            produit = produit.save();
            produit.save()
            created = True
            return HttpResponseRedirect('/produits/'+str(produit.id) +'/')
            
    else:
        produit = models.ProduitForm()

    return render_to_response('produits/new.html', {'created':created, 'produit': produit, 'user': request.user })
    
@login_required
def NewClient(request):
    client = False
    form = ClientForm()
    if request.POST:
        client = ClientForm(request.POST)
        
        if client.is_valid():
            # Save the form
            client = client.save()
            #save the entry
            client.save()
    return render_to_response('clients/new.html', {'client': client, 'form': form})
    
@login_required
def FactureDetails(request, facture_id):
    facture = Facture.objects.get(id = facture_id)

    return render_to_response('facture/details.html', {'facture': facture})
    
@login_required
def AddPrixProduit(request, object_id):
    created = False
    prix = False
    if request.POST:
        form = PrixForm(request.POST)
        if form.is_valid():
            prix = form.save()
            prix.save()
            created = True
            # Because a Prix was created, we can tell the template to use the empty form
            prix = False
    
    produit = Produit.objects.get(id=object_id)
    
    return render_to_response('produits/produit.html', { 'produit': produit, 'created': created, 'prix': prix })
    
@login_required
def FactureFermer(request, facture_id):
    print "Fermer une facture"
    facture = False
    if facture_id > 0:
        facture = Facture.objects.get(id=facture_id)
    print facture    
    if facture:
        facture.EstFermee = True
        facture.save()
        facture.EstFermee
    print "Alorss donc voilà, c'est fermé ou pas? À Vous de me le dire" 
    
    return HttpResponseRedirect('/factures/'+str(facture.id)+'/')   
        
    