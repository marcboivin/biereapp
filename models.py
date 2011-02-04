# This Python file uses the following encoding: utf-8
import logging
import datetime
from decimal import *
from types import *

from django.db import models
from django.contrib.auth.models import User, Group
from django import forms
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.template.loader import render_to_string

from biereapp import settings
from biereapp.middleware import GlobalUser

# Setup debugging
LOG_FILENAME = 'debug.log'
#logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG)

def logit(what):
    d = datetime.datetime.now()
    if settings.DEBUG:
        print "logit: " + what
        #logging.debug(d.ctime() + ": " + what)

TYPE_TRANS = (
    ('CMD', 'Commande'),
    ('CRE', 'Crédit'),
    ('INV_IN', 'Inventaire In'),
    ('INV_OUT', 'Inventaire Out'),
    ('PAIE', 'Paiement'),
    ('RBS', 'Rabais'),
    ('RT', 'Retour'),
    ('RTV', 'Retour vide'),
)

TYPE_PRIX = (
    ('COST', 'Prix cost'),
    ('AFF', 'Prix affiché'),
    ('SPE', 'Spécial'),
)

class Client(models.Model):
    Nom = models.CharField(max_length=60)
    def __unicode__(self):
        return self.Nom
        
    def get_factures(self):
        # ToDo
        factures = Facture.objects.filter(Client=self).order_by('-Date')
        
        return factures
        
    def get_factures_html(self, template="client_factures.html"):
        factures = self.get_factures()
        return render_to_string('snippets/'+ template, {'factures': factures})
    
    def is_client_interne(self):
        try:
            client_interne = Option.get("Client interne")
            if self.Nom == client_interne:
                return True
            else:
                return False
        except Exception as e:
            return False
        
        
    def save(self):
        # Can we have a global user that we could put here,  without having it passed
        # as a parameter
        try:


            if self.id:
                if not GlobalUser.user.has_perm('biereapp.change_client'):
                    raise Exception("Vous ne pouvez pas changer de Client")
                    return False
            else:
                if not GlobalUser.user.has_perm('biereapp.add_client'):
                    raise Exception("Vous ne pouvez pas ajouter de client")
                    return False

        except NameError:
            raise Exception(u"Erreur fatale, le Middleware GlobalUser n'est pas actif, impossible de faire des sauvegardes.") 

        # Call the parent method    
        super(Client, self).save()


class Brasseur(models.Model):
    Nom = models.CharField(max_length=60)
    def __unicode__(self):
        return self.Nom

    def save(self):
        # Can we have a global user that we could put here,  without having it passed
        # as a parameter
        try:

            if self.id:
                if not GlobalUser.user.has_perm('biereapp.change_rasseur'):
                    raise Exception("Vous ne pouvez pas changer de Brasseur")
                    return False
            else:
                if not GlobalUser.user.has_perm('biereapp.add_brasseur'):
                    raise Exception("Vous ne pouvez pas ajouter de Brasseur")
                    return False

        except NameError:
            raise Exception(u"Erreur fatale, le Middleware GlobalUser n'est pas actif, impossible de faire des sauvegardes.") 

        # Call the parent method    
        super(Brasseur, self).save()

class Produit(models.Model):
    Nom = models.CharField(max_length = 60)
    Consigne = models.DecimalField(max_digits=5, decimal_places=2)
    Brasseur = models.ForeignKey('Brasseur')
    def prix(self):
        """
            Obtenir le liste de prix pour le produit
        """
        prix = Prix.objects.filter(Produit=self)
        return prix
    def __unicode__(self):
        return self.Brasseur.__unicode__() + ' ' + self.Nom
        
    def get_in(self):
        inventaire_in = Transaction.objects.filter(Type='INV_IN').filter(Prix__Produit=self)
        retour = Transaction.objects.filter(Type='RETOUR').filter(Prix__Produit=self)
        tot = 0
        for i in inventaire_in:
            tot += i.Qte
        for r in retour:
            tot += r.Qte

        return tot
        
    def get_out(self):
        inventaire_out = Transaction.objects.filter(Type='INV_OUT').filter(Prix__Produit=self)
        tot = 0
        for o in inventaire_out:
            tot += o.Qte
        return tot
        
    def get_stock(self):
        return self.get_in() - self.get_out()
        
    def get_commande_etudiant(self):
        client_interne = Option.get('Client interne')
        try:
            client_interne = Client.objects.filter(Nom=client_interne)[0:1].get()
        except DoesNotExist:
            client_interne = Client()
        
        # No Client interne, only opened Facture
        etudiant = Transaction.objects.filter(Facture__EstFermee=False).filter(Type='CMD').filter(Prix__Produit=self).exclude(Facture__Client=client_interne.id)
        return etudiant.count()
        
    def get_commande_fournisseur(self):
        client_interne = Option.get('Client interne')
        try:
            client_interne = Client.objects.filter(Nom=client_interne)[0:1].get()
        except DoesNotExist:
            client_interne = Client()
            
        # Only client interne and opened Facture
        fournisseur = Transaction.objects.filter(Facture__EstFermee=False).filter(Prix__Produit=self).filter(Type='CMD').filter(Facture__Client=client_interne.id)
        
        return fournisseur.count()
        
    def save(self):
        # Can we have a global user that we could put here,  without having it passed
        # as a parameter
        try:
            if self.id:
                if not GlobalUser.user.has_perm('biereapp.change_produit'):
                    raise Exception("Vous ne pouvez pas changer de Produit")
                    return False
            else:
                if not GlobalUser.user.has_perm('biereapp.add_produit'):
                    raise Exception("Vous ne pouvez pas ajouter de Produit")
                    return False

        except NameError:
            raise Exception(u"Erreur fatale, le Middleware GlobalUser n'est pas actif, impossible de faire des sauvegardes.") 

        # Call the parent method    
        super(Produit, self).save()
    
class Prix(models.Model):
    Note = models.CharField(max_length=140, blank=True)
    Prix = models.DecimalField(max_digits=5,decimal_places=2)
    Produit = models.ForeignKey('Produit')
    Type = models.CharField(max_length=5, choices=TYPE_PRIX)
    # Prix privée sont les trucs comme le cost ou les prix que 
    # les usagés régulier ne peuvent pas voir
    Prive = models.BooleanField()

    def __unicode__(self):
        return self.Produit.__unicode__() + ': ' + self.Type + ': ' + str(self.Prix)
        
    def save(self):
        # Can we have a global user that we could put here,  without having it passed
        # as a parameter
        try:

            if self.id:
                if not GlobalUser.user.has_perm('biereapp.change_prix'):
                    raise Exception("Vous ne pouvez pas changer de Prix")
                    return False
            else:
                if not GlobalUser.user.has_perm('biereapp.add_prix'):
                    raise Exception("Vous ne pouvez pas ajouter de Prix")
                    return False

        except NameError:
            raise Exception(u"Erreur fatale, le Middleware GlobalUser n'est pas actif, impossible de faire des sauvegardes.") 

        # Call the parent method    
        super(Prix, self).save()
    
class Transaction(models.Model):
    Prix = models.ForeignKey('Prix', blank=True, null=True)
    Type = models.CharField(max_length=10, choices=TYPE_TRANS)
    Date = models.DateTimeField(auto_now_add=True)
    # Support for decimal in quantities in order to make 
    # Consigne esayer to support
    Qte = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    Facture = models.ForeignKey('Facture', blank=True, null=True)
    User = models.ForeignKey(User)
    # Dans le cas ou la transation est arbitraire (crédit ou autre)
    # On peut utiliser ce champs, il faut aussi remplir la raison
    # Le champs arbitraire est pour indiquer un prix et le Champs raison Expliquer pourquoi
    Arbitraire = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True, default=-1)
    Raison = models.CharField(max_length=140, blank=True)
    
    class Meta:
        # Chaque type de transation à besoin d'une permission pour
        # être effectué
        permissions = TYPE_TRANS
    # Ajoute le transaction comme une commande
    def add_to_commande(self):
        self.Type = 'CMD'
        
        self.save( )
        
    def get_total(self):
        # Returns the total for the current transaction
        # ToDo 
        # ('INV_IN', 'Inventaire In'),
        # ('INV_OUT', 'Inventaire Out'),
        # ('RT', 'Retour'),
        # ('CMD', 'Commande'),
        # ('RTV', 'Retour vide'),
        # ('CRE', 'Crédit'),
        # ('RBS', 'Rabais'),
        # ('PAIE', 'Paiement'),
        # Support Arbitraire priority
        if self.Type == 'RBS':
            return -self.Arbitraire
            
        if self.Arbitraire > -1:
            return self.Arbitraire
        #   - Calculate based on the transaction type 
        
        # You do not oay when making a Commande
        if self.Type == 'CMD' or self.Type == 'RTV':
            return 0
            
        if self.Type == 'PAIE':
            return -self.Qte
        
        # Those lines are just wrong     
        # Retour de Vide mean you give part of the Consigne back
        #if self.Type == 'RTV':
        #    return self.Qte * self.Prix.Produit.Consigne
        
        if type(self.Prix.Prix) is not Decimal:
            self.Prix.Prix = 0
            
        if type(self.Qte) is not Decimal:
            self.Qte = 0
            
        tot = self.Prix.Prix * self.Qte
        
        if not tot:
            tot = 0
        
        return tot
    
    # ToDo
    def get_consigne(self):
        # Only calculate the consigne for beers that
        # have left inventory
        # If the beer has come back, we make a negative 
        # consigne
        if self.Type == 'INV_OUT':
            return self.Qte * self.Prix.Produit.Consigne
        # Briging bottles back, we get a credit
        if self.Type == 'RTV':
            return -self.Qte * self.Prix.Produit.Consigne
        
        return 0
        
    def get_taxes(self):
        # ToDo: Get tha latest TAXES options by date this 
        # option should be formatted as such {TPS: {taux:0.05, aff: "5%"}, TVQ: {taux: 0.0895, aff: "8,5%"} }
        # return a dict with all the listed taxes and their value

        t = self.get_total()

        getcontext().prec = 10

        # Sub is the subtotal without the taxes
        taxes = { 'TPS': 0, 'TVQ': 0, 'sub': 0 }
        # We cannot apply taxes to negative numbers
        if t <= 0:
            return taxes

        TPS = Decimal( str(0.05) )
        TVQ = Decimal( str(0.085) )
        ratio = ((1 + TPS)*(1 + TVQ))

        ratio = Decimal( str( ratio ) )
        amount_without_taxes = Decimal( str(t / ratio) )

        amount_tps = amount_without_taxes * TPS
        amount_tvq = (amount_without_taxes + amount_tps) * TVQ

        taxes['TVQ'] = amount_tvq
        taxes['TPS'] = amount_tps
        taxes['sub'] = amount_without_taxes

        return taxes

        
    def save(self):
        # Can we have a global user that we could put here,  without having it passed
        # as a parameter
        try:
            self.User = GlobalUser.user
            
            # Get Facture based on the number needed
            user = BiereUser.as_current_user()
            client = user.is_restricted_user()
            if client:
                if self.Facture.Client != client:
                    raise Exception("Vous ne pouvez pas faire cette action, méchant garnement, hors d'ici!")
                    return false
                    
            if not GlobalUser.user.has_perm('biereapp.add_transaction'):
                raise Exception("Vous ne pouvez pas ajouter de Transaction")
                return False
                    
            if not GlobalUser.user.has_perm('biereapp.'+self.Type):
                raise Exception(u"Vous ne pouvez pas sauvegarder ce genre de transaction, désoler: " + self.Type)
                return False

            
        except NameError:
            raise Exception(u"Erreur fatale, le Middleware GlobalUser n'est pas actif, impossible de faire des sauvegardes.") 
        
        # Call the parent method    
        super(Transaction, self).save()
        
    def __unicode__(self):
        return self.Prix.Produit.Nom + str(self.get_total())
    
class Facture(models.Model):
    Client = models.ForeignKey(Client)
    Date = models.DateTimeField(auto_now_add=True)
    EstFermee = models.BooleanField(default=False)
    Note = models.CharField("Événement ou raison", max_length=140)
    
    def __unicode__(self):
        return self.Date.__str__() + ' pour ' + self.Client.Nom
        
    def transactions(self):

        # We need a user in order to discriminate
        # What transactions can be shown
        qs = Transaction.objects.filter(Facture=self);

        
        
        if len(qs) < 1:
            return {}

        return qs
        
    def total(self):

        trans = self.transactions()
        
        tot = 0
        for t in trans:
            if type(t) is Transaction:
                tot += t.get_total()
                
        if type(tot) is not Decimal:
            tot = 0    
        
        return tot
        
    def consigne(self):
        trans = self.transactions()
        tot = 0
        for t in trans:
            if type(t) is Transaction:
                tot += t.get_consigne()
        return tot

    def get_total_template(self, template_path):
        # Output the total of a Facture, with all the details
        # If there is a template_path we return a response
        # Otherwise we return a dict with all the values in it
        pass
    # Build a form with a product and the type of transaction a 
    # user can do. Hide the transaction form if there is only 
    # one possible TRANS_TYPE
    def transaction_form(self):
        form = TransactionForm({'Facture': self.id})
        return form.as_ul( )
        
    def transaction_details(self, template = 'transaction_details.html'):
        trans = Transaction.objects.filter(Facture=self).order_by( 'Prix__Produit__id', 'Date' )
        
        return render_to_string('facture/' + template, { 'transactions': trans, 'facture': self })
            
    def get_taxes(self):

        trans = self.transactions()

        tot = []
        tps = 0 
        tvq = 0 
        sub = 0

        for t in trans:

            if type(t) is Transaction:
                txs = t.get_taxes()
                
                tps += txs['TPS']
                tvq += txs['TVQ']
                sub += txs['sub']

        tot.append(['Sous-total', sub])
        tot.append(['TPS', tps])
        tot.append(['TVQ', tvq])
        
        return tot
        
    def is_client_interne(self):
        return self.Client.is_client_interne()
        
    def save(self):
        # Can we have a global user that we could put here,  without having it passed
        # as a parameter
        try:

            if self.id:
                if not GlobalUser.user.has_perm('biereapp.change_facture'):
                    raise Exception("Vous ne pouvez pas changer de Facture")
                    return False
            else:
                if not GlobalUser.user.has_perm('biereapp.add_facture'):
                    raise Exception("Vous ne pouvez pas ajouter de Facture")
                    return False
                    
            # Get Facture based on the number needed
            user = BiereUser.as_current_user()
            client = user.is_restricted_user()
            if client:
                if self.Client != client: 
                    raise Exception("Vous ne pouvez pas faire cette action, méchant garnement, hors d'ici!")
                    return false

        except NameError:
            raise Exception(u"Erreur fatale, le Middleware GlobalUser n'est pas actif, impossible de faire des sauvegardes.") 

        # Call the parent method    
        super(Facture, self).save()
        
    class Meta:
        permissions = (
            ("creer", "Peut creer des factures"),
            ("fermer", "Peut designer une facture comme payee"),
            ("crer_pour_lui", "Creer une facture pour seulement pour l'usage en cours"),
        )
        
class Option(models.Model):
    Nom = models.CharField(max_length=40)
    Valeur = models.CharField(max_length=255)
    Date = models.DateTimeField(auto_now_add=True)
    
    @staticmethod
    def get(option):
        try:
             valeur = Option.objects.filter(Nom=option)[0:1].get()
        except DoesNotExist:
            return ''
        return valeur.Valeur
         
    def __unicode__(self):
        return self.Nom + ': ' + self.Valeur

    def save(self):
        # Can we have a global user that we could put here,  without having it passed
        # as a parameter
        try:

            if self.id:
                if not GlobalUser.user.has_perm('biereapp.change_option'):
                    raise Exception("Vous ne pouvez pas changer d'Option")
                    return False
            else:
                if not GlobalUser.user.has_perm('biereapp.add_option'):
                    raise Exception("Vous ne pouvez pas ajouter d'Option")
                    return False

        except NameError:
            raise Exception(u"Erreur fatale, le Middleware GlobalUser n'est pas actif, impossible de faire des sauvegardes.") 

        # Call the parent method    
        super(Option, self).save()        

    class Meta:
        ordering = ('-Date', 'Nom')
        
class FactureForm(forms.ModelForm):
    class Meta:
        model = Facture
        fields = ('Note','Client')
        
# Proxy model for User
class BiereUser(User):
    @staticmethod
    def as_current_user():
        try:
            u = BiereUser.objects.get(id=GlobalUser.user.id)
            return u
        except:
            # Empty user
            return BiereUser()
        
    class Meta:
        proxy = True
    # Returns all the facture, 
    # returns the number if count is true
    def get_facture(self, count=False):
        bills = Facture.objects.filter(User=self).order_by('-Date')
        if count:
            return len(bills)
        return bills
    # returns a list of ferme Facture, returns the number
    # if count is set to True
    def get_facture_fermee(self, count = False):
        bills = Facture.objects.filter(User=self, EstFermee=True).order_by('-Date')
        if count:
            return len(bills)
        return bills
        
    # Returned the rendered template to show 
    # a standardized list of Facture for the current
    # user. We ask for a copy of GET but it can be any old
    #QueryDict with a page index int it.
    def show_user_facture(self, GET):
        factures = self.get_facture()
        number = self.get_facture(True)
        paginator = Paginator(factures, 5)

        number_fermee = self.get_facture_fermee(True)
        
        # Make sure page request is an int. If not, deliver first page.
        try:
            page = int(GET.get('page', '1'))
        except ValueError:
            page = 1

        # If page request (9999) is out of range, deliver last page of results.
        try:
            bills = paginator.page(page)
        except (EmptyPage, InvalidPage):
            bills = paginator.page(paginator.num_pages)
            
        return render_to_string('snippets/user_facture.html', {'paged_factures': bills, 'user': self, 'nb_fact_tot': number, 'nb_fact_fermee': number_fermee})
    def is_restricted_user(self):

        try:
            # We return the client, more efficient, enventhough misleading
            client = Client.objects.filter(Nom=self.username)[0:1].get()
            return client
        except:
            return False
class ProduitForm(forms.ModelForm):
    class Meta:
        model = Produit
        
class TransactionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(TransactionForm, self).__init__(*args, **kwargs)
        #self.fields['Facture'] = forms.CharField(facture.id,widget=forms.HiddenInput, initial=facture.id)
        
    class Meta: 
        model = Transaction
        fields = ['Type', 'Prix', 'Qte', 'Raison', 'Arbitraire', 'Facture' ]
        
class CommandeProduitForm(forms.Form):
    # ToDo: Faire marcher la discrimination de produit
    Type = forms.ChoiceField(choices=TYPE_TRANS, label="Type de transaction")
    Prix = forms.ModelChoiceField(queryset=None, empty_label="Aucun produit", label="Produits disponibles")
    Qte = forms.IntegerField(min_value=1, max_value=100, label="Quantité (max 100)")
    Facture = forms.CharField(widget=forms.HiddenInput)
    Arbitraire = forms.DecimalField(decimal_places=2)
    Raison = forms.CharField()
    def __init__(self, facture, *args, **kwargs):
        # facture doit être une instance de la classe Facture
        self.facture = facture

        qs = self.DiscriminateProduits()
        super(CommandeProduitForm, self).__init__(*args, **kwargs)
        self.fields['Prix'].queryset =  qs
        
        

        self.fields['Facture'] = forms.CharField(facture.id,widget=forms.HiddenInput, initial=facture.id)
    def DiscriminateProduits(self):
        # Get the users' permissions
        perms = ('',)
        #for p in TYPE_TRANS:
            # Loop permissions to check what kind of Prix you can get
            #if self.user.has_perm('Prix.'+p[0]):
            #    perms = perms + (p[0],)
        #queryset = Prix.objects.all().filter(Type__in=perms)
        queryset = Prix.objects.all()
        

        return queryset

    def DiscriminateTransaction(self):
        """Select the kind of transaction a user can make"""
        perms = ('',)
        #for p in TYPE_PRIX:
            # Loop permissions to check what kind of Prix you can get
            #if self.user.has_perm('Prix.'+p[0]):
            #    perms = perms + (p[0],)
        #queryset = Prix.objects.all().filter(Type__in=perms)


    def __unicode__(self):
        return super(CommandeProduitForm, self).__unicode__()
        
class ClientForm(forms.ModelForm):
    class Meta:
        model = Client

class PrixForm(forms.ModelForm):
    class Meta:
        model = Prix
        widgets = {
            'Produit': forms.HiddenInput(),
        }