from django.shortcuts import render,redirect,get_object_or_404
from .models import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash,logout, authenticate, login
from .forms import ProfileForm, CustomPasswordChangeForm
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Chat, Message, Dorm
from django.http import JsonResponse
from bs4 import BeautifulSoup
from django.db.models import Max
from django.contrib.auth.models import User


# Create your views here.
def home(request):
    dorms = Dorm.objects.all()
    user_favorites = request.user.favoritedorm_set.all() if request.user.is_authenticated else []
    user_favorites_ids = user_favorites.values_list('dorm', flat=True) if request.user.is_authenticated else []
    # Pass dorms to the template
    return render(request, 'index.html', {'dorms': dorms,'user_favorites':user_favorites,'user_favorites_ids':user_favorites_ids})

def mylisting(request):
    if request.user.profile.role=='Owner':
        dorms = Dorm.objects.filter(owner=request.user)
        user_favorites = request.user.favoritedorm_set.all() if request.user.is_authenticated else []
        user_favorites_ids = user_favorites.values_list('dorm', flat=True) if request.user.is_authenticated else []
        # Pass dorms to the template
        return render(request, 'mylisting.html', {'dorms': dorms,'user_favorites':user_favorites,'user_favorites_ids':user_favorites_ids})
    else:
        return redirect('home')
def fav(request):

    user_favorites = request.user.favoritedorm_set.all() if request.user.is_authenticated else []
    user_favorites_ids = user_favorites.values_list('dorm', flat=True) if request.user.is_authenticated else []

    # Pass dorms to the template
    return render(request, 'fav.html', {'dorms':user_favorites,'user_favorites_ids':user_favorites_ids})



def dorm_detail(request, dorm_id):
    dorm = get_object_or_404(Dorm, id=dorm_id)

    chat = Chat.objects.filter(user=dorm.owner).first()


    if not chat:
        chat = Chat.objects.create(user=dorm.owner)

    context = {
        'dorm': dorm,
        'chat_id': chat.id  
    }

    return render(request, 'details.html', context)





def chat_messages(request, chat_id):
    # Get the Chat object by ID
    chat = Chat.objects.get(id=chat_id)

    print(chat)
    messages = Message.objects.filter(Q(chat=chat) | Q(sender=chat.user)).order_by('timestamp')

    # Prepare message data to send in the response
    message_data = [{
        'content': message.content,
        'timestamp': message.timestamp.strftime('%I:%M %p'),
        'sender': message.sender,
        'is_sent': message.sender == request.user  # Flag to indicate if the message was sent by the current user
    } for message in messages]

    # Return the messages in JSON format
    return JsonResponse({'messages': message_data})
    # return render(request, 'message.html', message_data)
def success_view(request):
    return render(request,'success.html')



@login_required(login_url='/login/')
def Chatmessages(request):
    chat_id = request.GET.get('chat_id')

    dorms = Dorm.objects.all()
    chatd = Chat.objects.get(id=chat_id)
    # print(chatd.user.id)
    # Retrieve chats where the current user is either the sender or the recipient.
    chats = Chat.objects.filter(
        Q(user=request.user) | Q(message__sender=request.user)
    ).distinct()  # Use distinct() to avoid duplicates.

    chat_data = []
    messages = []

    # Fetch the specific chat based on chat_id from the URL, if available
    if chat_id:
        chat = get_object_or_404(Chat, id=chat_id)

        # Make sure the current user is involved in the chat either as a sender or recipient
        if chat.user == request.user or Message.objects.filter(chat=chat, sender=request.user).exists():
            messages = Message.objects.filter(chat=chat).order_by('timestamp')

    # Prepare the data for rendering
    for chat in chats:
    
        if(chat.user.username!=request.user.username):
            last_message = Message.objects.filter(chat=chat).order_by('timestamp').last()
            profile = Profile.objects.get(user=chat.user)

            chat_data.append({
                'chat': chat,
                
                'last_message': last_message,
                'chat_user': chat.user.username,
                'chat_id': chat.id,
                'profile_pic': profile.profile_pic.url if profile.profile_pic else None,
            })

    return render(request, 'message.html', {
        'dorms': dorms,
        'chatd':chatd,
        'chat_data': chat_data,
        'messages': messages,
    })

def role_selection(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        if request.method == 'POST':
            role = request.POST.get('dorm-option')
            if role:
                # Save the selected role in session to be used in the next step
                request.session['role'] = role
                return redirect('signup')  # Redirect to the login page
        return render(request, 'login.html')

@login_required(login_url='/login/')
def owner_dashboard(request):
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

    return render(request, 'owner_welcome.html',{'dormTypes':dromTypes,'placeTypes':placeTypes})

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        if request.method == 'POST':
            role = request.session.get('role')
            name = request.POST.get('name')
            phone = request.POST.get('phone')
            email = request.POST.get('email')
            password = request.POST.get('password')
            user=User.objects.create(
                username=email,
                email=email
            )
            user.set_password(password)
            user.save()
            user_profile = Profile.objects.create(
                user=user,
                display_name=name,
                legal_name=name,
                phone_number=phone,
                role=role
                )
            user_profile.save()
            if user:
                login(request, user)
                if role=='Owner':
                    return redirect('owner_dashboard')
                else:
                    return redirect('profile')  # Redirect to the dashboard (or home page)
        
        return render(request,'signup.html')

def login_view(request):

    if request.user.is_authenticated:
        return redirect('home')
    else:
        if request.method == 'POST':
            email = request.POST.get('email')
            password = request.POST.get('password')
            
            # Authenticate the user with email and password
            user = authenticate(request, username=email, password=password)
            
            if user is not None:
                login(request, user)
                # Check if the role from session matches the one in the profile
        
                try:
                    profile = Profile.objects.get(user=user)
                    if profile.role=='Owner':
                        return redirect('owner_dashboard')
                    else:
                        return redirect('profile')  # Redirect to the dashboard (or home page)
                except Profile.DoesNotExist:
                    messages.error(request, "Profile not found.")
            else:
                messages.error(request, "Invalid credentials, please try again.")
        
        return render(request, 'login2.html')
def dorm_search(request):
    query = request.GET.get('query')
    dorms = Dorm.objects.all()
    user_favorites = request.user.favoritedorm_set.all() if request.user.is_authenticated else []
    user_favorites_ids = user_favorites.values_list('dorm', flat=True) if request.user.is_authenticated else []
    if query:
        dorms = dorms.filter(
            name__icontains=query
        )

    context = {
        'dorms': dorms,
        'query': query,
        'user_favorites':user_favorites,
        'user_favorites_ids':user_favorites_ids
    }
    return render(request, 'index.html', context)

def dorm_suggestions(request):
    query = request.GET.get('query', '')
    suggestions = []
    
    if query:
        dorms = Dorm.objects.filter(name__icontains=query)[:5]  # Limit to 5 results for performance
        suggestions = list(dorms.values('id', 'name'))

    return JsonResponse({'suggestions': suggestions})

def dorm_filter(request):
    amenitiess=Amenity.objects.all()
    accessibility_features = AccessibilityFeature.objects.all()
    max_price = RentalCost.objects.aggregate(Max('rent'))['rent__max']

    context={
        'amenitiess':amenitiess,
        'accessibility_features':accessibility_features,
        'max_price':max_price
    }
    return render(request, 'filters.html',context)

def dorm_filter_view(request):
    # Get filter values from GET request (or set defaults)
    max_priceD = RentalCost.objects.aggregate(Max('rent'))['rent__max']
    min_price = request.GET.get('min_price', '0')  # Set a default minimum price of 0
    max_price = request.GET.get('max_price', max_priceD)  # Set a reasonable default max price

    bath_count = request.GET.get('bath_count', None)
    dorm_types = request.GET.getlist('dorm_types', [])
    amenities = request.GET.getlist('amenities', [])
    accessibility_features = request.GET.getlist('accessibility_feature', [])

    amenitiess = Amenity.objects.all()

    # Convert prices to float if they are provided, with fallback to defaults
    try:
        min_price = float(min_price)
    except (TypeError, ValueError):
        min_price = 0  # Default fallback

    try:
        max_price = float(max_price)
    except (TypeError, ValueError):
        max_price = 10000  # Default fallback

    # Start with the base queryset
    dorms = Dorm.objects.all()

    # Filter by price range
    dorms = dorms.filter(rentalcost__rent__gte=min_price, rentalcost__rent__lte=max_price)

    # Filter by number of bathrooms (if selected)
    if bath_count:
        dorms = dorms.filter(bathroom=int(bath_count))

    # Filter by dorm type (if selected)
    if dorm_types:
        dorms = dorms.filter(type_of_dorm__in=dorm_types)

    # Filter by amenities (if selected)
    if amenities:
        dorms = dorms.filter(amenities__id__in=amenities)

    # Filter by accessibility features (if selected)
    if accessibility_features:
        dorms = dorms.filter(accessibility_features__id__in=accessibility_features)

    # Get all possible filter choices
    amenity_list = Amenity.objects.all()
    accessibility_feature_list = AccessibilityFeature.objects.all()

    user_favorites = request.user.favoritedorm_set.all() if request.user.is_authenticated else []
    user_favorites_ids = user_favorites.values_list('dorm', flat=True) if request.user.is_authenticated else []

    # Return the filtered results along with filter options
    return render(request, 'dorms.html', {
        'dorms': dorms,
        'amenities': amenity_list,
        'amenitiesF': amenities,
        'accessibility_features': accessibility_feature_list,
        'accessibility_featuresF': accessibility_features,
        'min_price': min_price,
        'max_price': max_price,
        'bath_count': bath_count,
        'dorm_types': dorm_types,
        'amenitiess': amenitiess,
        'user_favorites': user_favorites,
        'user_favorites_ids': user_favorites_ids,
    })


@login_required(login_url='/login/')
def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        return redirect('home')
    else:
        return redirect('home')
        


@login_required(login_url='/login/')
def dorm_create(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        type_of_dorm = request.POST.get('type_of_dorm')
        place_type = request.POST.get('place_type')
        images = request.FILES

        # matchmate = 'matchmate' in request.POST

        # Create a new Dorm instance and save it
        dorm = Dorm(
            name=title,
            type_of_dorm=type_of_dorm,
            place_type=place_type,
            description=description,
            owner=request.user,
            availability_status=True
            # Assuming you're setting this to True when submitted
        )
        dorm.save()
        for im in images:
            # print(request.FILES[im])
            DormImage.objects.create(dorm=dorm,image=request.FILES[im])
        return redirect('dorm_create_part_2', dorm_id=dorm.id)  # Redirect to a success page or the list page

    return redirect('dashboard')

def dorm_create_part_2(request, dorm_id):
    if request.method == 'POST':
        # Collect basic dorm information from form inputs
        
        guestsa = request.POST.get('guests')
        bedroomsa =request.POST['bedrooms'].replace('(','').replace(')','').replace(',','')
        bedsa = int(request.POST['beds'])
        bathroomsa = int(request.POST['bathrooms'])
        if bathroomsa:  # Check if the value is not None or an empty string
            bathroomsa = int(bathroomsa)
        else:
            bathroomsa = None
        price = request.POST.get('price')
        deposit = request.POST.get('deposit')
        utilities = request.POST.get('utilities')
        print(request.POST)
        selected_amenities = request.POST.getlist('amenities')
        # Create a new Dorm instance and save it
        dorm = Dorm.objects.get(id=dorm_id)
        
        # dorm.address=address,
        dorm.guest=guestsa
        dorm.bedroom=bedroomsa
        dorm.bed=bedsa
        dorm.bathroom=bathroomsa
        
        
        

        # Save selected amenities (assuming a ManyToMany relationship)
        dorm.amenities.set(selected_amenities)
        RentalCost.objects.create(dorm=dorm,rent=price,deposit=deposit,utilities=utilities)

        soup = BeautifulSoup(request.POST.get('map'), 'html.parser')

        # Find the iframe tag and get the src attribute
        iframe = soup.find('iframe')
        iframe_src = iframe['src'] if iframe else None
        Location.objects.create(
                    dorm=dorm,
                    address= request.POST.get('street_address'),
                    city= request.POST.get('city'),
                    state= request.POST.get('state'),
                    zip_code= request.POST.get('zip_code'),
                    country= request.POST.get('country'),
                    google_map_embed_code=iframe_src,
                )
        
        dorm.save()
        return redirect('dorm_create_part_3', dorm_id=dorm.id)  # Redirect to a success or listing page

    # Render form with all available amenities
    amenities = Amenity.objects.all()  # Fetch all available amenities for the form
    return render(request, 'owner_welcome2.html', {'dorm_id':dorm_id,'amenities':amenities})

def dorm_create_part_3(request, dorm_id):
    dor=Dorm.objects.filter(id=dorm_id).first()
    if request.method == 'POST':
        pub = 'pub' in request.POST
        # Create a new Dorm instance and save it
        dorm = Dorm.objects.get(id=dorm_id)
        
        dorm.published=pub
        
        dorm.save()

        # Save selected amenities (assuming a ManyToMany relationship)
    

        return redirect('success')  # Redirect to a success or listing page

    return render(request, 'owner_welcome3.html', {'dorm':dor,'dorm_id':dorm_id})


def removedorm(request,did):
    Dorm.objects.get(id=did).delete()
    return redirect('mylisting')

@login_required(login_url='/login/')
def submitreview(request):
    if request.method == 'POST':
        review_text = request.POST.get('review_text')
        rating = request.POST.get('rating')  # Get the rating from the hidden field

        # Save the review with the rating
        Review.objects.create(
            dorm=Dorm.objects.get(id=request.POST.get('dorm_id')),
            reviewer_name=request.user,
            comment=review_text,
            rating=rating
        )

        return redirect('dorm_detail',request.POST.get('dorm_id'))
    else:
        return redirect('home')
@login_required(login_url='/login/')
def profile(request):
    profile = Profile.objects.get(user=request.user)

    if request.method == 'POST':
        # Handle the profile update
        if 'update_profile' in request.POST:
            form = ProfileForm(request.POST, instance=profile)
            # print(form)
            if form.is_valid():
                form.save()
                return redirect('profile')  # Redirect to the same profile page after saving
        if 'update_number' in request.POST:
            profile.phone_number=request.POST['phone_number']
            profile.save()
            return redirect('profile')

        if 'update_doc' in request.POST:
            profile.id_document_type=request.POST['id_document_type']
            profile.save()
            return redirect('profile')
        # Handle the password update
        if 'update_password' in request.POST:
            password_form = CustomPasswordChangeForm(user=request.user, data=request.POST)
            print(password_form)
            if password_form.is_valid():
                user = password_form.save()
                messages.success(request, 'Password Updated')

                update_session_auth_hash(request, user)  # Keep the user logged in after password change
                return redirect('profile')
            else:
                messages.error(request, password_form.errors)
                # Redirect to the profile page
        if 'update_pic' in request.POST:
            # Handle the profile picture update
            profile.profile_pic=request.FILES['profile_pic']
            profile.save()
            return redirect('profile')  # Redirect to the profile page after updating
            
        if 'update_email' in request.POST:
            # Update the email
            new_email = request.POST.get('email')
            if new_email and new_email != request.user.email:
                # Check if email is already taken by another user
                if User.objects.filter(email=new_email).exists():
                    messages.error(request, "This email is already associated with another account.")
                else:
                    request.user.email = new_email
                    request.user.save()
                    messages.success(request, "Your email has been updated successfully.")
            else:
                messages.error(request, "The email is the same as the current one or invalid.")
        
    # else:
    form = ProfileForm(instance=profile)
    password_form = CustomPasswordChangeForm(user=request.user)

    return render(request, 'profile.html', {
        'profile': profile,
        'form': form,
        'password_form': password_form
    })

@login_required(login_url='/login/')
def deactivate_account(request):
    # Ensure the user is authenticated
    if request.user.is_authenticated:
        # Mark the user as inactive (deactivated)
        request.user.is_active = False
        request.user.save()

        # Log the user out after deactivation
        messages.success(request, "Your account has been deactivated.")
        return redirect('logout')  # Redirect to logout page after deactivation
    else:
        messages.error(request, "You must be logged in to deactivate your account.")
        return redirect('profile')
    

@login_required(login_url='/login/')
def delete_account(request):
    # Ensure the user is authenticated
    if request.user.is_authenticated:
        user = request.user
        username = user.username
        user.delete()

        # Log the user out after deletion
        messages.success(request, f"Your account ({username}) has been deleted.")
        return redirect('logout')  # Redirect to logout page after deletion
    else:
        messages.error(request, "You must be logged in to delete your account.")
        return redirect('profile')

@login_required(login_url='/login/')
def add_to_favorites(request, dorm_id):
    dorm = Dorm.objects.get(id=dorm_id)

    # Check if the dorm is already a favorite
    if not FavoriteDorm.objects.filter(user=request.user, dorm=dorm).exists():
        FavoriteDorm.objects.create(user=request.user, dorm=dorm)

    return redirect('home')

# View to remove a dorm from favorites
@login_required(login_url='/login/')
def remove_from_favorites(request, dorm_id):
    dorm = Dorm.objects.get(id=dorm_id)

    # Check if the dorm is a favorite and remove it
    favorite = FavoriteDorm.objects.filter(user=request.user, dorm=dorm)
    if favorite.exists():
        favorite.delete()

    return redirect('home')



