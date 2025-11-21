from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.db.models import Q
from .models import Post, Comment, Category, Tag, Like
from .forms import CommentForm, PostForm, RegisterForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
from .forms import ProfileForm, SubscriberForm, ContactForm
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required



class PostListView(ListView):
    model = Post
    paginate_by = 5
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'

    def get_queryset(self):
        qs = Post.objects.filter(status='published')
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(content__icontains=q) | Q(category__name__icontains=q) | Q(tags__name__icontains=q)).distinct()
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured_posts'] = Post.objects.filter(status='published', featured=True)[:5]
        context['categories'] = Category.objects.all()
        return context


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'

    def get_object(self):
        return get_object_or_404(Post, slug=self.kwargs.get('slug'), status='published')

    def post(self, request, *args, **kwargs):
        # handle new comment
        post = self.get_object()
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.approved = False
            comment.save()
            return redirect(post.get_absolute_url())
        return self.get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # provide an empty comment form for the template
        context['form'] = CommentForm()
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'

    def test_func(self):
        post = self.get_object()
        return post.author == self.request.user or self.request.user.is_staff


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'blog/post_confirm_delete.html'
    success_url = reverse_lazy('post_list')

    def test_func(self):
        post = self.get_object()
        return post.author == self.request.user or self.request.user.is_staff


def like_post(request, slug):
    post = get_object_or_404(Post, slug=slug)
    if not request.user.is_authenticated:
        return redirect('login')
    obj, created = Like.objects.get_or_create(post=post, user=request.user)
    # toggle like
    if obj.value == 1:
        obj.value = 0
    else:
        obj.value = 1
    obj.save()
    return redirect(post.get_absolute_url())


@require_POST
def publish_post(request, slug):
    post = get_object_or_404(Post, slug=slug)
    # only allow author or staff to publish
    if not request.user.is_authenticated:
        messages.error(request, 'You must be logged in to publish posts.')
        return redirect('login')
    if request.user != post.author and not request.user.is_staff:
        messages.error(request, 'You do not have permission to publish this post.')
        return redirect(post.get_absolute_url())

    if post.status != 'published':
        post.status = 'published'
        post.published_at = timezone.now()
        post.save()
        messages.success(request, 'Post published.')

        # Notify subscribers by email (console backend in development)
        try:
            from .models import Subscriber
            emails = list(Subscriber.objects.values_list('email', flat=True))
            if emails:
                subject = f'New post: {post.title}'
                post_url = request.build_absolute_uri(post.get_absolute_url())
                context = {'post': post, 'post_url': post_url}
                message = render_to_string('emails/new_post.txt', context)
                from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'webmaster@localhost')
                send_mail(subject, message, from_email, emails, fail_silently=True)
        except Exception:
            # avoid breaking publish if email send fails
            pass
    else:
        messages.info(request, 'Post is already published.')
    return redirect(post.get_absolute_url())


@require_POST
def unpublish_post(request, slug):
    post = get_object_or_404(Post, slug=slug)
    if not request.user.is_authenticated:
        messages.error(request, 'You must be logged in to unpublish posts.')
        return redirect('login')
    if request.user != post.author and not request.user.is_staff:
        messages.error(request, 'You do not have permission to unpublish this post.')
        return redirect(post.get_absolute_url())

    if post.status == 'published':
        post.status = 'draft'
        post.published_at = None
        post.save()
        messages.success(request, 'Post has been moved back to draft.')
    else:
        messages.info(request, 'Post is already a draft.')
    return redirect(post.get_absolute_url())


@login_required
def dashboard(request):
    """Author dashboard showing current user's posts and quick actions."""
    posts = Post.objects.filter(author=request.user).order_by('-created')
    return render(request, 'blog/dashboard.html', {'posts': posts})


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('post_list')
        else:
            # surface form errors to messages and server log for debugging
            try:
                messages.error(request, 'Registration error: ' + '; '.join([f"{k}: {v}" for k, v in form.errors.items()]))
            except Exception:
                messages.error(request, 'Registration failed — check input.')
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def edit_profile(request):
    profile, _ = request.user.profile, None
    try:
        profile = request.user.profile
    except Exception:
        from .models import Profile
        profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated')
            return redirect('post_list')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'registration/profile_edit.html', {'form': form})


def subscribe(request):
    if request.method == 'POST':
        form = SubscriberForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Thanks for subscribing!')
            return redirect('subscribe_thanks')
    else:
        form = SubscriberForm()
    return render(request, 'subscribe.html', {'form': form})


def subscribe_thanks(request):
    return render(request, 'subscribe_thanks.html')


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']
            subject = f'Contact from {name} <{email}>'
            body = message
            send_mail(subject, body, settings.DEFAULT_FROM_EMAIL if hasattr(settings,'DEFAULT_FROM_EMAIL') else 'webmaster@localhost', [settings.DEFAULT_FROM_EMAIL if hasattr(settings,'DEFAULT_FROM_EMAIL') else 'webmaster@localhost'])
            messages.success(request, 'Message sent — thank you!')
            return redirect('contact')
    else:
        form = ContactForm()
    return render(request, 'contact.html', {'form': form})


def about(request):
    return render(request, 'about.html')
