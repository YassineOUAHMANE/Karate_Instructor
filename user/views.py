import json
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import login, authenticate
from django.contrib.auth.hashers import check_password
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from .forms import SignUpForm, LoginForm
from feedback.models import MartialArt, Movement,ProgressHistory
from django.views.decorators.csrf import csrf_exempt

from codes.coding import provide_real_time_feedback
def login_or_register_view(request):
    signup_form = SignUpForm()
    login_form = LoginForm()
    if request.method == "POST":
        if 'signup' in request.POST:
            signup_form = SignUpForm(request.POST)
            login_form = LoginForm()
            if signup_form.is_valid():
                # Create the user
                user = signup_form.save(commit=False)
                user.set_password(signup_form.cleaned_data['password'])
                user.save()
                login(request, user)
                return redirect('home')
        elif 'signin' in request.POST:
            login_form = LoginForm(request, data=request.POST)
            signup_form = SignUpForm()
            if login_form.is_valid():
                user = authenticate(username=login_form.cleaned_data['username'], 
                                    password=login_form.cleaned_data['password'])
                if user is not None:
                    login(request, user)
                    return redirect('home')
                else : 
                    login_form.add_error(None, "Invalid email or password")
    return render(request, 'user/SignUp.html', {'signup_form': signup_form, 'login_form': login_form})

@login_required
def profile_view(request):
    martialArts = MartialArt.objects.all()
    context = {'martial_arts' : martialArts}
    user = request.user
    profile = user.profile

    # Start Generals
    if request.method == "POST":
        if "general-change" in request.POST:
            errors = []
            new_username = request.POST.get("Username")
            if new_username:
                user.username = new_username

            new_email = request.POST.get("Email")
            if new_email:
                if new_email != user.email:
                    try:
                        validate_email(new_email)
                    except ValidationError:
                        errors.append("Invalid email format.")
                    if User.objects.filter(email=new_email).exists():
                        errors.append("This email is already in use.")
                    else : 
                        user.email = new_email

            new_profile_image = request.FILES.get("profile-image")
            if new_profile_image:
                allowed_file_types = ["image/jpeg", "image/png", "image/gif"]
                if new_profile_image.content_type not in allowed_file_types:
                    errors.append("Invalid image type. Only JPEG, PNG, and GIF are allowed.")

            if errors:
                return render(request, "user/profile.html")

            user.save()
            profile.save()
            return redirect("profile")

        # Start Privacy
        elif "password-changed" in request.POST:
            current_password = request.POST["current_password"]
            new_password = request.POST["new_password"]
            confirm_password = request.POST["confirm_password"]
            if (current_password and new_password and (check_password(current_password, user.password)) and (new_password == confirm_password)) :
                user.set_password(new_password)
                user.save()
                return redirect("profile")

    return render(request, "user/profile.html", context=context)

def movements_json(request, martial_art_id):
    movements = Movement.objects.filter(martial_art_id=martial_art_id)
    data = {
        "movements": [
            {"name": movement.name}
            for movement in movements
        ]
    }
    return JsonResponse(data)

def movements_view(request, martial_art_id):
    martial_art = get_object_or_404(MartialArt, pk=martial_art_id)
    movements = Movement.objects.filter(martial_art_id=martial_art)
    return render(request, "movements.html", {"martial_art": martial_art, "movements": movements})

@login_required
def dashboard_view(request):
    user = request.user

    # Query all progress history entries for the current user
    progress_entries = ProgressHistory.objects.filter(user_id=user)

    # Prepare data for the dashboard (e.g., dates and scores)
    progress_data = []
    for entry in progress_entries:
        # Assuming that `entry.progress_scores` is a list of floats
        progress_data.append({
            'movement_name': entry.movement_id.name,
            'progress_scores': entry.progress_scores,
            "image_path" : "user/images/" + entry.movement_id.martial_art_id.name + ".png"
        })
    context = {
        "progress_data": json.dumps(progress_data),  # Pass data as JSON string to the template
    }
    return render(request, 'user/dashboard.html', context)
@login_required
@csrf_exempt
def train(request):
    if request.method == "POST":
        movement_id = request.POST.get("movement_id")
        if not movement_id or not movement_id.isdigit():
            return JsonResponse({'error': 'Movement ID is required and must be a number'})
        
        try:
            movement = Movement.objects.get(movement_id=movement_id)
            user = request.user
            progress_record, created = ProgressHistory.objects.get_or_create(
                user_id=user, movement_id=movement
            )
            
            score = provide_real_time_feedback(movement)
            print(score)
            progress_record.add_progress(score)
            return JsonResponse({"status": "success", "message": f"Training completed for {movement.name} with a score of {score}."})
        except Movement.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Invalid movement ID."}, status=400)
    else:
        movements = Movement.objects.all()
        return render(request, "user/train.html", {"movements": movements})


    
@login_required
def save_training_score(request):
    if request.method == "POST":
        user = request.user
        movement_id = request.POST.get("movement_id")
        score = request.POST.get("score")  # Assume this is sent from JS

        try:
            movement = Movement.objects.get(movement_id=movement_id)
            progress_record, _ = ProgressHistory.objects.get_or_create(
                user=user, movement=movement
            )
            progress_record.add_progress(float(score))
            return JsonResponse({"status": "success", "message": "Score saved!"})
        except Movement.DoesNotExist:
            return JsonResponse({"error": "Invalid movement ID"}, status=400)