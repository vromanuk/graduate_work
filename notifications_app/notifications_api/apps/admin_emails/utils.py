from django.template import Context, Template


def render_subject(ctx: Context, subject: str):
    template = Template(subject)
    return template.render(ctx)


def render_html_text(ctx: Context, text: str):
    template = Template(text)
    return template.render(ctx)
