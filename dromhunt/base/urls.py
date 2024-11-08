
from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('',home,name='home'),
    path('wishlist/',fav,name='fav'),
    path('mylisting/',mylisting,name='mylisting'),
    path('removedorm/<int:did>/',removedorm,name='removedorm'),
    path('dorms/',dorm_filter_view,name='dorm_filter_view'),
    path('filters/',dorm_filter,name='dorm_filter'),
    path('dorm/<int:dorm_id>/', dorm_detail, name='dorm_detail'),
    path('messages/',Chatmessages,name='messages'),
    path('submit-review/',submitreview,name='submit-review'),
    path('profile/',profile,name='profile'),
    path('deactivate/', deactivate_account, name='deactivate_account'),
    path('delete/', delete_account, name='delete_account'),
    path('add_to_favorites/<int:dorm_id>/', add_to_favorites, name='add_to_favorites'),
    path('remove_from_favorites/<int:dorm_id>/', remove_from_favorites, name='remove_from_favorites'),
    path('role-selection/', role_selection, name='role_selection'),
    path('login/', login_view, name='login'),
    path('signup/', signup_view, name='signup'),
    path('logout/', logout_view, name='logout'),
    path('dorm_create/', dorm_create, name='dorm_create'),
    path('dorm/create/part-2/<int:dorm_id>/', dorm_create_part_2, name='dorm_create_part_2'),
    path('dorm/create/part-3/<int:dorm_id>/', dorm_create_part_3, name='dorm_create_part_3'),
    path('owner_dashboard/', owner_dashboard, name='owner_dashboard'),
    path('dorm-suggestions/', dorm_suggestions, name='dorm_suggestions'),
    path('search/', dorm_search, name='dorm_search'),
    path('chat/messages/<int:chat_id>/', chat_messages, name='chat_messages'),
    path('success/', success_view, name='success'),
    

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
