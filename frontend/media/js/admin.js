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