/* Where all the Javascript is */
jQuery(function($){
    var add_form = $('#add_prod_comm');
    var type_trans = $('#id_Type');
    var start_val = type_trans.val();
    
    change_fields(start_val); 
    
    // What happens when the transation changes
    type_trans.change(function(){
        var t = $(this);
        var val = t.val();
        change_fields(val); // Change the form according to the transaction type
    });
    
    function change_fields(transaction){
        var arbirtraire = 'RBS CRE PAIE';
        var qte_only = 'CMD INV_IN RT INV_OUT RTV';
        hide_all_fields();
        // We always want to show Type
        show_field('id_Type');
        // No transaction type, we quit!
        if(transaction == ""){
            return true;
        }
        if(arbirtraire.indexOf(transaction) != -1 ){
            show_field('id_Arbitraire');
            show_field('id_Raison');
            return true;
        }
        if(qte_only.indexOf(transaction) != -1){
            show_field('id_Prix');
            show_field('id_Qte');
            return true;
        }
        
        return false;
    }
    
    function show_field(id) {
        f = $('#'+id).show(); // The field
        l = $('label[for="'+id+'"]').show();// The label
    }
    
    function hide_field(id){
        f = $('#'+id).hide(); // The field
        l = $('label[for="'+id+'"]').hide();// The label
    }
    function hide_all_fields(){
        add_form.find('input[type="text"]').hide(); 
        add_form.find('select').hide();
        add_form.find('label').hide();
    }
});

/* Ajustment for stocks */
jQuery(function($){
    var err = $('#erreurs');
    var m = $('#message');
    $('.inventaire table tr').each(function(){
       var t = $(this);
       
       var s = t.find('.stock');
       var qte = s.html();
       var input = $('<input type="text" value="'+qte+'">').keypress(function(e){
              if (e.which == '13'){
                  err.fadeOut();
                  m.fadeOut();
                  new_qte = s.find('input').val();
                  qte_to_send = new_qte - qte;
                  console.log(qte_to_send);
                  
                  // Uglyass AJAX to get the new Qte if it was updated at all
                  $.post('/ajax/inventaire/ajust/', 
                           { Produit: t.find('.id').first().html(), Qte: qte_to_send }, 
                           function(data){
                               console.log(data)
                               if(data.erreur){
                                   
                                   // Errors, we show them and set it to the old qte
                                   var html = '';
                                   for(i=0; i < data.erreur.length; i++){
                                       html += '<p>'+data.erreur[i]+'</p>';
                                   }
                                   
                                   err.html(html).fadeIn();
                                   s.find('input').val(qte);
                                   
                               }else{
                                   s.find('input').val(data.qte);
                                   qte = data.qte; // Set to the newly approve quantity
                                   m.html('Mise à jour effecutée avec succès').fadeIn();
                                   t.animate({backgroundColor:'#9DFF00'},200);
                               }
                           }, 'json');
              }
          }); 
       s.html(input);
        
    });
    
});

