from django.db import models


class PublishStateOptions(models.TextChoices):
    PUBLISHED = "PU", "Published"
    DRAFT = "DR", "Draft"
    UNLISTED = "UN", "Unlisted"
    PRIVATE = "PR", "Private"
