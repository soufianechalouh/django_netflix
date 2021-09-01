import random
import string

from django.utils.text import slugify


def get_random_string(size=4, chars=string.ascii_lowercase+string.digits):
    return ''.join([random.choice(chars) for _ in range(size)])


def get_unique_slug(instance, new_slug=None):
    title = instance.title
    if new_slug is None:
        slug = slugify(title)
    else:
        slug = new_slug
    Klass = instance.__class__
    try:
        parent = instance.parent
    except:
        parent = None
    if parent is not None:
        qs = Klass.objects.filter(parent=parent, slug=slug)
    else:
        qs = Klass.objects.filter(slug=slug)
    if qs.exists():
        rand_str = get_random_string()
        slug = new_slug+rand_str
        return get_unique_slug(instance, slug)
    return slug
