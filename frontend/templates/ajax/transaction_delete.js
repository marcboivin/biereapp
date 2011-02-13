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
        "deleted": "true"
    {% endif %}
    
}