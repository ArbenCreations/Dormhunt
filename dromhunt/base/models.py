from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Amenity(models.Model):
    name = models.CharField(max_length=50)
    icon_url=models.ImageField(upload_to='icons',null=True)
    def __str__(self):
        return self.name
class AccessibilityFeature(models.Model):
    name = models.CharField(max_length=100)
    is_host_provided = models.BooleanField(default=False, help_text="True if this feature was provided by the host")

    def __str__(self):
        return self.name
class Dorm(models.Model):
    dromTypes=(
                ('Single Room','Single Room'),
                ('Double Room','Double Room'),
                ('Deluxe Room','Deluxe Room'),
                ('Apartment Style','Apartment Style')
                )
    placeTypes = (
        ('Single Room', 'Guests will have their own private space within a larger accommodation'),
        ('Shared Room', 'Guests will have their own private space within a larger accommodation'),
        ('Entire Place', 'Guests will have the whole place to themselves, offering privacy and freedom'),
    )
    name = models.CharField(max_length=255)
    # price_per_month = models.DecimalField(max_digits=10, decimal_places=2)
    type_of_dorm = models.CharField(max_length=255, choices=dromTypes)
    place_type = models.CharField(max_length=50, choices=placeTypes, help_text="What type of place will guests have?" ,null=True)
    area = models.DecimalField(max_digits=10, decimal_places=2, help_text="Area in square feet",null=True)
    bathroom = models.CharField(max_length=10, default=0)
    guest = models.CharField(max_length=10, default=0)
    bed = models.CharField(max_length=10, default=0)
    bedroom = models.CharField(max_length=10, default=0)
    study_area = models.CharField(max_length=10, default=0)
    description=models.TextField(null=True)
    # rent = models.DecimalField(max_digits=10, decimal_places=2)
    # deposit = models.DecimalField(max_digits=10, decimal_places=2)
    # utilities = models.DecimalField(max_digits=10, decimal_places=2)
    # location = models.CharField(max_length=255)

    availability_status = models.BooleanField(default=False)
    reviews_count = models.PositiveIntegerField(default=0)
    reviews_avg_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    amenities = models.ManyToManyField(Amenity, blank=True, related_name='dorms')
    accessibility_features = models.ManyToManyField(AccessibilityFeature, blank=True, related_name='dorms')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_dorms')
    published = models.BooleanField(default=False)  # Field to mark if the dorm is published
    def __str__(self):
        return f"{self.name} - {self.owner}"





class DormImage(models.Model):
    dorm = models.ForeignKey(Dorm, related_name="images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to='dorm_images/')

    def __str__(self):
        return f"Image for {self.dorm.name}"
    
class RentalCost(models.Model):
    dorm = models.OneToOneField(Dorm, on_delete=models.CASCADE)
    rent = models.DecimalField(max_digits=10, decimal_places=2)
    deposit = models.DecimalField(max_digits=10, decimal_places=2,null=True)
    utilities = models.DecimalField(max_digits=10, decimal_places=2,null=True)

    def __str__(self):
        return f"{self.dorm.name} - Rental Costs"


class Review(models.Model):
    dorm = models.ForeignKey(Dorm, on_delete=models.CASCADE, related_name='reviews')
    reviewer_name = models.ForeignKey(User,on_delete=models.CASCADE)
    rating = models.DecimalField(max_digits=2, decimal_places=1)
    comment = models.TextField()

    def __str__(self):
        return f"{self.reviewer_name.profile.legal_name} - {self.rating} Stars"

class Location(models.Model):
    dorm = models.OneToOneField(Dorm, on_delete=models.CASCADE)
    address = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    google_map_embed_code = models.TextField(null=True, blank=True)  # New optional field for embed code
    nearby_schools = models.IntegerField(null=True, blank=True)
    grocery_stores = models.IntegerField(null=True, blank=True)
    hospitals = models.IntegerField(null=True, blank=True)
    malls = models.IntegerField(null=True, blank=True)
    coffee_shops = models.IntegerField(null=True, blank=True)
    transit_options = models.CharField(max_length=255,null=True, blank=True)
    city=models.CharField(max_length=255,null=True, blank=True)
    state=models.CharField(max_length=255,null=True, blank=True)
    zip_code=models.CharField(max_length=255,null=True, blank=True)
    country=models.CharField(max_length=255,null=True, blank=True)
    def __str__(self):
        return f"{self.address}"



class Profile(models.Model):
    ROLE_CHOICES = [
        ('Owner', 'Owner'),
        ('Hunter', 'Hunter'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    display_name = models.CharField(max_length=100)
    occupation = models.CharField(max_length=100, default="Student")
    legal_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    # email = models.EmailField()
    id_document_type = models.CharField(max_length=100, blank=True, null=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='Hunter')

    def __str__(self):
        return self.display_name


class FavoriteDorm(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    dorm = models.ForeignKey(Dorm, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.dorm.name}"

    class Meta:
        unique_together = ('user', 'dorm')


class Chat(models.Model):
    # Fields for Chat model
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user}"

class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    sender = models.CharField(max_length=100)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)  # New field to track if the message has been read

    def __str__(self):
        return f"Message from {self.sender}: {self.content[:20]}"
