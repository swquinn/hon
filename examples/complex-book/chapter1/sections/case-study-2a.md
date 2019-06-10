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
            <tr>
            {% for item in data %}
                <td>{{ loop.index }}</td>
                {% for key, value in item.items() %}<td>{{ value }}</td>{% endfor %}
            {% endfor %}
            </tr>
        </tbody>
    </table>
{% endmacro %}

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
