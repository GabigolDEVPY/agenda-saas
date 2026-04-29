def get_msg_form_invalid(self, form):
    errors = []

    for field, field_errors in form.errors.items():
        for error in field_errors:
            errors.append(error)

    msg = " | ".join(errors)
    return msg