# from django.db import models

# class Product(models.Model):
#     title = models.CharField(max_length=255)
#     price = models.DecimalField(max_digits=10, decimal_places=2)
#     link = models.URLField()
#     updated_date = models.DateField()
#     condition = models.CharField(max_length=100)
#     rarity = models.CharField(max_length=100)
#     game_name = models.CharField(max_length=255)
#     specialty = models.CharField(max_length=255, blank=True, null=True)
#     card_name = models.CharField(max_length=255, blank=True, null=True)
#     manufacturer = models.CharField(max_length=255, blank=True, null=True)
#     material = models.CharField(max_length=255, blank=True, null=True)
#     card_type = models.CharField(max_length=255, blank=True, null=True)
#     ebay_id = models.CharField(max_length=100, unique=True)

#     def __str__(self):
#         return self.title


