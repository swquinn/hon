{% macro render_table(data) %}
{% set keys = data[0].keys() %}
<table>
    <thead>
        <tr>
            <th>Index</th>
            {% for key in keys %}<th>{{ key }}</th>{% endfor %}
        </tr>
    </thead>
    <tbody>
        {% for item in data %}
        <tr>
            <td>{{ loop.index }}</td>
            {% for key, value in item.items() %}<td>{{ value }}</td>{% endfor %}
        </tr>
        {% endfor %}
    </tbody>
</table>
{% endmacro %}

Pellentesque lacinia nisl vitae semper condimentum. Sed fringilla nisi vitae dui efficitur lacinia. Orci varius natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus.

Integer tempor finibus ornare: {{ book.simple_variable }}

Phasellus a velit mauris.

{{ render_table([
{
    'Nunc et risus':  'Faucibus, porta ligula et, aliquet nisl.',
    'Proin blandit':  'Mollis efficitur.',
    'Donec accumsan': 'Justo augue, ut tempus nisl elementum in.'
},
{
    'Nunc et risus':  'Integer gravida mi at ante rutrum, eget posuere quam cursus.',
    'Proin blandit':  'Curabitur tincidunt tempus pretium.',
    'Donec accumsan': 'Aliquam at velit eros.'
},
{
    'Nunc et risus':  'Nulla at ante malesuada, convallis metus eu, pellentesque dolor.',
    'Proin blandit':  'Aliquam pretium, sem eu porttitor efficitur.',
    'Donec accumsan': 'Adio mauris molestie nisl, a scelerisque dolor nibh vel magna.'
}]) }}
