
from multiprocessing import context
from pyexpat import model
from wsgiref.util import request_uri
from django.shortcuts import redirect,render
from .forms import *
from django.contrib import messages
from django.views import generic
from youtubesearchpython import VideosSearch
import requests
import wikipedia
from django.contrib.auth.decorators import login_required
import time

# Home section
def home(request):
    return render(request,'kids/home.html')

#Notes Section
@login_required
def notes(request):
    if request.method == "POST":
        form = NotesForm(request.POST)
        if form.is_valid():
           notes = Notes(user=request.user,title=request.POST['title'],description=request.POST['description'])
           notes.save()
        messages.success(request,f"Notes from {request.user.username} added successfully!")  
    else:
        form = NotesForm()       
        
    notes = Notes.objects.filter(user=request.user)
    form = NotesForm()
    context = {'notes':notes,'form':form}
    
    return render(request,'kids/notes.html',context)

@login_required
def delete_notes(request,pk=None):
    Notes.objects.get(id=pk).delete()
    return redirect("notes")

class NotesDetailView(generic.DetailView):
     model = Notes

# Homework Section
@login_required
def homework(request):
    if request.method == "POST":
        form = HomeworkForm(request.POST)
        if form.is_valid():
            try:
                finished = request.POST['is_finished']
                if finished == 'on':
                    finished = True
                else:
                    finished = False
            except:
                finished = False
                homeworks = Homework(user=request.user,subject=request.POST['subject'],title=request.POST['title'],description=request.POST['description'],due=request.POST['due'],is_finished=finished)
                homeworks.save()
                messages.success(request,f'Homework from {request.user.username} Added!!')
    else:
        form = HomeworkForm()            


    form = HomeworkForm()
    homeworks = Homework.objects.filter(user=request.user)
    if len(homeworks)==0:
        homework_done = True
    else:
        homework_done = False
    context = {
               'homeworks':homeworks,
               'homework_done':homework_done,
               'forms':form
    }
    return render(request,'kids/homework.html',context)

@login_required
def update_homework(request,pk=None):
        homework = Homework.objects.get(id=pk)
        if homework.is_finished == True:
            homework.is_finished = False
        else:
            homework.is_finished = True
        homework.save()
        return redirect('homework')

@login_required
def delete_homework(request,pk=None):
        Homework.objects.get(id=pk).delete()
        return redirect('homework')

# Youtube Section
def youtube(request):
    if request.method == "POST":
        form = DashboardForm(request.POST)
        text = request.POST['text']
        video = VideosSearch(text,limit=10)
        result_list = []
        lm=1
        
        for i in video.result()['result']:
            
            result_dict = {
                'input' : text,
                'title' : i['title'],
                'duration' : i['duration'],
                'thumbnail' : i['thumbnails'][0]['url'],
                'channel' : i['channel']['name'],
                'link' : i['link'],
                'views' : i['viewCount']['short'],
                'published' : i['publishedTime'],
            }
            desc = ''
            if i['descriptionSnippet']:
                for j in i['descriptionSnippet']:
                    desc += j['text']
                    result_dict['description'] = desc
                result_list.append(result_dict) 
                lm+=1
                if lm==10:
                 break        
        context = {
                        'form':form,
                        'results':result_list
                    }
                   
        return render(request,'kids/youtube.html',context)
    else:                
      form = DashboardForm()
      context = {'forms':form}
      return render(request,'kids/youtube.html',context)

# Todo Section
@login_required
def todo(request):
    if request.method == "POST":
        form = TodoForm(request.POST)
        if form.is_valid():
            try:
                finished = request.POST["is_finished"]
                if finished == 'on':
                    finished = True
                else:
                    finished = False
            except:
                finished = False
            todos = Todo(
                user = request.user,
                title = request.POST["title"],
                is_finished = finished
            )
            todos.save()
            messages.success(request,f"Todo Added from {request.user.username} !!")
    else:
        form = TodoForm()
    todo = Todo.objects.filter(user=request.user)
    if len(todo)==0:
            todos_done = True
    else:
            todos_done = False

    context = {
        'form':form,
        'todos':todo,
        'todos_done':todos_done
    }
    return render(request,'kids/todo.html',context)

@login_required
def update_todo(request,pk=None):
        todo = Todo.objects.get(id=pk)
        if todo.is_finished == True:
            todo.is_finished = False
        else:
            todo.is_finished = True
        todo.save()
        return redirect('todo')

@login_required
def delete_todo(request,pk=None):
    Todo.objects.get(id=pk).delete()
    return redirect("todo")

# Books Section

def books(request):
    
    if request.method == "POST":
        form = DashboardForm(request.POST)
        text = request.POST['text']
        url = "https://www.googleapis.com/books/v1/volumes?q="+text
        r = requests.get(url)
        answer = r.json()
        result_list = []
        for i in range(10):
            result_dict = {
                'input':text,
                'title':answer['items'][i]['volumeInfo']['title'],
                'subtitle':answer['items'][i]['volumeInfo'].get('subtitle'),
                'description':answer['items'][i]['volumeInfo'].get('description'),
                'count':answer['items'][i]['volumeInfo'].get('pageCount'),
                'categories':answer['items'][i]['volumeInfo'].get('categories'),
                'rating':answer['items'][i]['volumeInfo'].get('pageRating'),
                'thumbnail':answer['items'][i]['volumeInfo'].get('imageLinks').get('thumbnail'),
                'preview':answer['items'][i]['volumeInfo'].get('previewLink'),
            }
                       
            result_list.append(result_dict)
            context={
                'forms':form,
                'results':result_list,
            }
        
        return render(request,'kids/books.html',context)    
    else:                
      form = DashboardForm()
    context = {'forms':form}
    return render(request,'kids/books.html',context)

# Dictionary Section
def dictionary(request):
    if request.method == "POST":
        form = DashboardForm(request.POST)
        text = request.POST['text']
        url = "https://api.dictionaryapi.dev/api/v2/entries/en_US/"+text
        r = requests.get(url)
        answer = r.json()
        try:
            phonetics = answer[0]['phonetics'][0]['text']
            audio = answer[0]['phonetics'][0]['audio']
            definition = answer[0]['meanings'][0]['definitions'][0]['definition']
            example = answer[0]['meanings'][0]['definitions'][0]['example']
            synonyms = answer[0]['meanings'][0]['definitions'][0]['synonyms']
            context = {
                        'forms':form,
                        'input':text,
                        'phonetics':phonetics,
                        'audio':audio,
                        'definition':definition,
                        'example':example,
                        'synonyms':synonyms,
            }
        except:
            context = {
                    'forms':form,
                    'input':''
            }
        return render(request,'kids/dictionary.html',context)
    else:
        form = DashboardForm()
        context = {'forms':form}
    return render(request,'kids/dictionary.html',context)

# Wikipedia Section
def wiki(request):
    if request.method == "POST":
      text = request.POST['text']
      form = DashboardForm(request.POST)
      search = wikipedia.page(text)
      context = {
          'forms':form,
          'title':search.title,
          'link':search.url,
          'details':search.summary,
      }
      return render(request,"kids/wiki.html",context)
    else:
        form = DashboardForm()
        context = {
            'forms':form
        }
    return render(request,"kids/wiki.html",context)

# Coding Section
def coding(request):
    languages = Coding.objects.all()
    context ={
        'lang':languages
    }
    return render(request,"kids/coding.html",context)

# Register Section
def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request,f"Account created for {username} ")
            return redirect("login")
    else:
        form = UserRegistrationForm()
    context = {
         'forms':form
    }
    return render(request,"kids/register.html",context)
 
# Profile Section
@login_required
def profile(request):
    homeworks = Homework.objects.filter(is_finished=False,user=request.user)
    todos = Todo.objects.filter(is_finished=False,user=request.user)
    if len(homeworks)==0:
        homework_done  = True
    else:
        homework_done = False
    if len(todos) ==0:
        todos_done = True
    else:
        todos_done = False
    context ={
        'homeworks':homeworks,
        'todos':todos,
        'homework_done':homework_done,
        'todos_done':todos_done,
    }


    return render(request,"kids/profile.html",context)


    


