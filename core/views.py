from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Room, Message
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.urls import reverse

@staff_member_required
def admin_dashboard(request):
    users = User.objects.all()
    rooms = Room.objects.all()
    messages = Message.objects.order_by('-timestamp')[:50]
    return render(request, 'admin_dashboard.html', {
        'users': users,
        'rooms': rooms,
        'messages': messages
    })

@login_required
def create_room(request):
    if request.method == 'POST':
        room_name = request.POST.get('room_name')
        if not Room.objects.filter(name=room_name).exists():
            Room.objects.create(name=room_name, created_by=request.user)
            # messages.success(request, 'Room created successfully')
            # Redirect to home with selected_room query param
            return redirect(f"{reverse('home')}?room={room_name}")
        else:
            messages.error(request, 'Room name already exists')
    return render(request, 'create_room.html')

@login_required
def delete_room(request, room_id):
    next_url = request.GET.get('next') or 'home'
    room = get_object_or_404(Room, id=room_id, created_by=request.user)

    if request.method == 'POST':
        room.delete()
        messages.success(request, 'Room deleted successfully.')
    return redirect(next_url)

@login_required
def profile(request):
    rooms = Room.objects.filter(created_by=request.user)
    messages = Message.objects.filter(user=request.user).order_by('-timestamp')[:20]
    return render(request, 'profile.html', {'rooms': rooms, 'messages': messages})

@login_required
def home(request):
    rooms = Room.objects.all()
    selected_room = None
    messages = []

    room_name = request.GET.get("room")
    if room_name:
        try:
            selected_room = Room.objects.get(name=room_name)
            messages = selected_room.messages.order_by('timestamp')[:50]
        except Room.DoesNotExist:
            messages.error(request, 'Selected room does not exist')

    return render(request, 'home.html', {
        'rooms': rooms,
        'selected_room': selected_room,
        'messages': messages,
    })

def signup_view(request):
    if request.method == 'POST':
        username = request.POST['username'].strip()
        password = request.POST['password']

        if not username or not password:
            messages.error(request, "Username and password are required.")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
        else:
            User.objects.create_user(username=username, password=password)
            messages.success(request, "Account created successfully. Please log in.")
            return redirect('login')
    return render(request, 'signup.html')

def login_view(request):
    next_url = request.GET.get('next', '')

    if request.method == 'POST':
        username = request.POST['username'].strip()
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect(request.POST.get('next') or 'home')
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, 'login.html', {'next': next_url})

def logout_view(request):
    logout(request)
    return redirect('login')
