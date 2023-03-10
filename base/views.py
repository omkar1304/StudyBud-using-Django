from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm  
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Room, Topic, Message
from .forms import RoomForm, UserForm
from django.views.decorators.csrf import csrf_exempt
# Create your views here.

# rooms = [
#     {'id' : 1, 'name' : 'App Developer'},
#     {'id' : 2, 'name' : 'FrontEnd Developer'},
#     {'id' : 3, 'name' : 'BackEnd Developer'}
# ]

@csrf_exempt
def loginPage(request):
    page = 'login'
    context = {'page' : page}

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exist')
        
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username OR Password does not exist')

    return render(request, 'base/login_register.html', context)

@csrf_exempt
def registerPage(request):
    form = UserCreationForm

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "An error occurred during registraion")

    return render(request, 'base/login_register.html', {'form' : form})

@csrf_exempt
def logoutPage(request):
    logout(request)
    return redirect('home')

def userProfile(request, pk):
    user = User.objects.get(id=pk)
    topics = Topic.objects.all()[0:5]
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    context = {'rooms' : rooms, 'topics' : topics,'room_messages' : room_messages, 'user' : user}
    return render(request, 'base/profile.html', context)

def home(request):
    query = request.GET.get('q') if request.GET.get('q') != None else ''
    # i -> to accept any lower or uppercase and contains -> to match any string in q
    rooms = Room.objects.filter(Q(topic__name__icontains=query) | 
                                Q(name__icontains=query) | 
                                Q(description__icontains=query)) 
    topics = Topic.objects.all()[0:5]
    room_messages = Message.objects.filter(Q(room__topic__name__icontains = query))
    room_count = rooms.count # passing rooms count after filtering
    context = {'rooms' : rooms, 'topics' : topics, 'room_count' : room_count, 'room_messages' : room_messages}
    return render(request, 'base/home.html', context)

@csrf_exempt
def room(request, pk):
    room = Room.objects.get(id=pk)
    room_mesaages = room.message_set.all()
    participants = room.participants.all()

    if request.method == "POST":
        message = Message.objects.create(
            user = request.user,
            room = room,
            body = request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)

    context = {'room' : room, 'room_mesaages': room_mesaages, 'participants' : participants}
    return render(request, 'base/room.html', context)

# @login_required(login_url='home')
# def createRoom(request):
#     form = RoomForm
#     topics = Topic.objects.all()

#     if(request.method == 'POST'):
#         form = RoomForm(request.POST)
#         if form.is_valid():
#             room = form.save(commit=False)
#             room.host = request.user
#             room.save()
#             return redirect('home')

#     context = {'form' : form, 'topics' : topics}
#     return render(request, 'base/room_form.html', context)

@csrf_exempt
@login_required(login_url='login')
def createRoom(request):
    form = RoomForm
    topics = Topic.objects.all()

    if(request.method == 'POST'):
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)

        Room.objects.create(
            host = request.user,
            topic = topic,
            name = request.POST.get('name'),
            description = request.POST.get('description')
        )
        return redirect('home')

    context = {'form' : form, 'topics' : topics}
    return render(request, 'base/room_form.html', context)

# @login_required(login_url='home')
# def updateRoom(request, pk):
#     room = Room.objects.get(id=pk)
#     form = RoomForm(instance=room)

#     if request.method == "POST":
#         form = RoomForm(request.POST, instance=room)
#         if form.is_valid():
#             form.save()
#             return redirect('home')

#     context = {'form' : form}
#     return render(request, 'base/room_form.html', context)

@csrf_exempt
@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()

    if request.method == "POST":
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)

        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')

    context = {'form' : form, 'room' : room, 'topics' :topics}
    return render(request, 'base/room_form.html', context)

@csrf_exempt
@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)
    if request.method == "POST":
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': room})

@csrf_exempt
@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)
    if request.method == "POST":
        message.delete()
        return redirect('home')

    return render(request, 'base/delete.html', {'obj' : message})

@csrf_exempt
@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == "POST":
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)

    context = {'form' : form}
    return render(request, 'base/update_user.html', context)

def browseTopics(request):
    query = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=query)
    context = {'topics' : topics}

    return render(request, 'base/topics.html', context)

def activity(request):
    room_messages = Message.objects.all()
    context = {'room_messages': room_messages}

    return render(request, 'base/activity.html', context)