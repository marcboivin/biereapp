{
    {% if erreur %}
        "erreur": [
        {% for e in erreur %}
         "{{e}}"
         {% endfor %}
     ]
    {% else %}  
    "qte": "{{ trans.Prix.Produit.get_stock }}"
    {% endif %}
    
}