# apkg errors

`apkg` communicates errors using custom exceptions in
{{ 'apkg/ex.py' | file_link }}.

Each exception contains message explaining what went wrong as well as
`exit_code` to return in case it's raised during CLI run.

A list of all `apkg` errors/exceptions with their default error message
sorted by exit code:

{% for e in exceptions  %}

### {{ e.__name__}}

```text
{{ e.msg_fmt }}
```

exit code: `{{ e.exit_code }}`

{% endfor %}
