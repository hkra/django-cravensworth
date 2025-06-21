from django.db import models
from django.urls import reverse


class FancyModel(models.Model):
    class Meta:
        app_label = 'testapp'

    def get_absolute_url():
        return reverse('model-view-redirect')
