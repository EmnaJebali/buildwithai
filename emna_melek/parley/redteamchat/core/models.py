from django.db import models

class DocumentScore(models.Model):
    name = models.CharField(max_length=255)
    resistance_score = models.FloatField(default=0.0)
    attack_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @property
    def formatted_resistance(self):
        return f"{self.resistance_score:.1f}"
