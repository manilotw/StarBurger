from django.utils import timezone
from django.db import models

class Place(models.Model):
    address = models.CharField(
        verbose_name='адрес',
        max_length=50,
        db_index=True
    )

    lat = models.DecimalField(
        verbose_name='Широта',
        max_digits=10,
        decimal_places=2
        )
    lon = models.DecimalField(
        verbose_name='Долгота',
        max_digits=10,
        decimal_places=2
        )
    
    request_date = models.DateField(
        verbose_name='Дата запроса',
        default=timezone.now
    )

    class Meta:
        unique_together = ['address_place', 'lat', 'lon']