# This Python file uses the following encoding: utf-8
from django.http import HttpResponse, HttpResponseServerError, HttpResponseRedirect, Http404
from django.core.cache import cache
from django.template.loader import get_template
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.template import Template, RequestContext
from django.conf import settings
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail, EmailMultiAlternatives

from math import fabs
from datetime import date, datetime

from biereapp.models import FactureForm, Facture, CommandeProduitForm, Transaction, Prix, ProduitForm, Produit, TransactionForm, ClientForm, PrixForm, Option, Client
from biereapp import models

from biereapp.models import logit

@login_required
def Dashboard(request):
    return render_to_response('dashboard.html', { 'user': request.user })
    
@login_required
def CreerFacture(request):
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
    client_interne = False
    
    try:
        client = Option.get('Client interne')
        if facture.Client.Nom == client:
            client_interne = True
    except:
        client_interne = False

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

    facture = False
    if facture_id > 0:
        facture = Facture.objects.get(id=facture_id)
    else: 
        raise Http404

    if facture:
        # Wasn't closed before, so we send the mail
        if not facture.EstFermee:
            mail_subject = render_to_string('mail/title.txt', {'facture': facture})
            mail_message = render_to_string('mail/content.html', {'facture': facture})
            mail_to = Option.get('Courriels')
            mail_to = mail_to.split(',')
            #send_mail(mail_subject, mail_message, 'biereapp@aep.polymtl.ca',mail_to, fail_silently=False)
            
            text_content = 'This is an important message.'
            html_content = '<p>This is an <strong>important</strong> message.</p>'
            msg = EmailMultiAlternatives(mail_subject, '', 'info@aep.polymtl.ca', mail_to)
            msg.attach_alternative(mail_message, "text/html")
            msg.send()
            
            facture.EstFermee = True
            facture.save()
    
    return HttpResponseRedirect('/factures/'+str(facture.id)+'/')  

@login_required    
def FactureInFermer(request, facture_id):
      
    facture = False
    if facture_id > 0:
        facture = Facture.objects.get(id=facture_id)
    else:
        raise Http404
        
    if facture:
        facture.EstFermee = False
        facture.save()
    
    return HttpResponseRedirect('/factures/'+str(facture.id)+'/')  
    
@login_required
def ProduitInventaire(request):
    liste_produits = Produit.objects.all().order_by('Brasseur', 'Nom')
    return render_to_response('produits/inventaire.html', {'produits': liste_produits}) 
    
@login_required
def CommandeFournisseur(request):
    # Try to get the Client interne Option
    try:
        client = Option.get('Client interne')
        client = Client.objects.filter(Nom = client)[0:1].get()
    except:
        raise Exception("Impossible de faire une commande fournisseur sans l'option Client interne ")
    
    facture = Facture()
    d = datetime.today()
    facture.Note = "Commande fournisseur du " + str(d.year) +'/'+ str(d.month) +'/'+ str(d.day)
    facture.Client = client
    facture.save()
    
    return render_to_response('facture/facture.html', {'facture': facture })
    
@login_required
def Commande(request):
    # Try to get the Client interne Option
    try:
        client = Option.get('Client interne')
        client = Client.objects.filter(Nom = client)[0:1].get()
    except:
        raise Exception("Impossible de faire une commande fournisseur sans l'option Client interne ")
    
    return render_to_response('clients/client.html', {'client': client})
    
@login_required
def AJAX_AddInventaire(request):
    if(request.POST):
        erreur = []
        try:
            facture = Option.get('Facture inventaire')
            facture = Facture.objects.get( id=int(facture) )
        except:
            erreur.append ("L'option Facture inventaire n'existe pas, vous ne pouvez faire de mise à jour de l'inventaire")
            
        try:
            prix = request.POST['Produit']
            prix = Produit.objects.get(id = prix)
            prix = Prix.objects.filter(Produit=prix)[0:1].get()
        except:
            erreur.append("Impossible d'identifier le produit")
            
        try:    
            qte = int(request.POST['Qte'])
        except:
            erreur.append("la quantité n'est pas une chiffre valide")
            
        if len(erreur) > 0:
            return render_to_response('ajax/ajust_qte.js', {'erreur': erreur})
            
        t = Transaction()
        t.Facture = facture
        t.Prix = prix
        if qte < 0:
            t.Type = "INV_OUT"
        else:
            t.Type = "INV_IN"
        t.Qte = abs(qte)
        t.save()
        
        return render_to_response('ajax/ajust_qte.js', {'trans': t})
        
    else:
        raise Http404();
        
        
        
    