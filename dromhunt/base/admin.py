from django.contrib import admin
from .models import *

# Inline models for nested relationships
class DormImageInline(admin.TabularInline):
    model = DormImage
    extra = 1

class ReviewInline(admin.TabularInline):
    model = Review
    extra = 1

# Admin models
@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(AccessibilityFeature)
class AccessibilityFeatureAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_host_provided')
    list_filter = ('is_host_provided',)
    search_fields = ('name',)

@admin.register(Dorm)
class DormAdmin(admin.ModelAdmin):
    list_display = ('name', 'type_of_dorm', 'area', 'bathroom', 'study_area', 'availability_status', 'reviews_count', 'reviews_avg_rating')
    list_filter = ('type_of_dorm', 'availability_status')
    search_fields = ('name', 'type_of_dorm')
    inlines = [DormImageInline, ReviewInline]

@admin.register(DormImage)
class DormImageAdmin(admin.ModelAdmin):
    list_display = ('dorm', 'image')

@admin.register(RentalCost)
class RentalCostAdmin(admin.ModelAdmin):
    list_display = ('dorm', 'rent', 'deposit', 'utilities')
    search_fields = ('dorm__name',)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('dorm', 'reviewer_name', 'rating')
    list_filter = ('rating',)
    search_fields = ('reviewer_name', 'dorm__name')

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('dorm', 'address', 'latitude', 'longitude', 'transit_options')
    search_fields = ('address', 'transit_options')

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'display_name', 'occupation', 'legal_name', 'phone_number')
    search_fields = ('display_name', 'occupation', 'legal_name')
    list_filter = ('occupation',)


admin.site.register(FavoriteDorm)

class ChatAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')
    search_fields = ('user__username',)  # Allows search by username

class MessageAdmin(admin.ModelAdmin):
    list_display = ('chat', 'sender', 'timestamp', 'content')
    search_fields = ('sender', 'content')
    list_filter = ('chat', 'timestamp')  # Filter by chat and timestamp
admin.site.register(Chat, ChatAdmin)
admin.site.register(Message, MessageAdmin)