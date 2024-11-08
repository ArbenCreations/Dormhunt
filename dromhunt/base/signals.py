# signals.py

from django.db.models.signals import post_save, post_delete
from django.db.models import Avg
from django.dispatch import receiver
from .models import Review, Dorm

@receiver(post_save, sender=Review)
@receiver(post_delete, sender=Review)
def update_dorm_review_stats(sender, instance, **kwargs):
    # Retrieve the dorm associated with this review
    dorm = instance.dorm
    
    # Calculate the average rating and review count
    reviews = dorm.reviews.all()
    reviews_count = reviews.count()
    avg_rating = reviews.aggregate(average_rating=Avg('rating'))['average_rating'] or 0.0
    
    # Update the dorm with the new values
    dorm.reviews_count = reviews_count
    dorm.reviews_avg_rating = avg_rating
    dorm.save()
