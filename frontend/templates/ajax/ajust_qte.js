{
    {% if erreur %}
        "erreur": [
        {% for e in erreur %}
            {% autoescape off %}
         "{{e}}"
            {% endautoescape %}
         {% endfor %}
     ]
    {% else %}  
    "qte": "{{ trans.Prix.Produit.get_stock }}"
    {% endif %}
    
}