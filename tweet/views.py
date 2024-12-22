from django.shortcuts import render
from .models import Tweet
from .forms import TweetForm, UserRegistrationForm
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required 
from django.contrib.auth import login
from django.db.models import Q
from django.http import JsonResponse
# Create your views here.

def index(request):
    return render(request, 'index.html')

def tweet_list(request):
    tweets = Tweet.objects.all().order_by('-created_at')
    # Add a boolean flag for each tweet that tells whether the user has liked it
    for tweet in tweets:
        tweet.liked_by_user = request.user in tweet.likes.all()
    return render(request, 'tweet_list.html',{'tweets':tweets})

@login_required
def tweet_create(request):
    if request.method == "POST":
        form = TweetForm(request.POST, request.FILES)
        if form.is_valid():
            tweet = form.save(commit=False)
            tweet.user = request.user
            tweet.save()
            return redirect('tweet_list')
    else:
        form = TweetForm()
    return render(request, 'tweet_form.html', {'form':form}) 

@login_required
def tweet_edit(request, tweet_id):
        tweet = get_object_or_404(Tweet, pk=tweet_id, user = 
        request.user)
        if request.method == 'POST':
            form = TweetForm(request.POST, request.FILES,
            instance=tweet)
            if form.is_valid():
                tweet = form.save(commit=False)
                tweet.user = request.user
                tweet.save()
                return redirect('tweet_list')
        else:
            form = TweetForm(instance=tweet)
        return render(request, 'tweet_form.html', {'form':form}) 

@login_required
def tweet_delete(request, tweet_id):
    tweet = get_object_or_404(Tweet, pk=tweet_id, user =
    request.user)
    if request.method == 'POST':
        tweet.delete()
        return redirect('tweet_list')
    return render(request, 'tweet_confirm_delete.html', 
    {'tweet': tweet}) 

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.save()
            login(request, user)
            return redirect('tweet_list')
    else:
        form = UserRegistrationForm()

    return render(request, 'registration/register.html',
    {'form': form})

def search_tweets(request):
    query = request.GET.get('query', '').strip()
    print(f"Search query: {query}") 
    
    if query:
        results = Tweet.objects.filter(
            Q(text__icontains=query) | Q(user__username__icontains=query)
    ) # Search tweets by text or username
    else:
        results = Tweet.objects.none()

    return render(request, 'search_results.html',
    {'results': results, 'query': query})

# Add a Detail View for Each Tweet
def tweet_detail(request, tweet_id):
    tweet = get_object_or_404(Tweet, pk=tweet_id)
    return render(request, 'tweet_detail.html', {'tweet': tweet})

#Like the Tweet
@login_required
def like_tweet(request, tweet_id):
    tweet = get_object_or_404(Tweet, id=tweet_id)
    if request.user in tweet.likes.all():
        tweet.likes.remove(request.user)  # Unlike if already liked
    else:
        tweet.likes.add(request.user)  # Add a like

    return JsonResponse({'likes_count': tweet.total_likes})