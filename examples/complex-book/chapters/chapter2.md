Chapter 2
=========

> This chapter tests using [Jinja2][_jinja2] template features, such as macros.

{% import './chapter2/macros.md' as m %}

{{ m.say_hello('Aurelias') }}

[_jinja2]: http://jinja.pocoo.org/