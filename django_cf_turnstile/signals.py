from django.dispatch import Signal

# Sent after every siteverify call. Receives `response_data` (the decoded
# siteverify JSON) and `remote_ip` (as given to the field, or None).
turnstile_validation_complete = Signal()
