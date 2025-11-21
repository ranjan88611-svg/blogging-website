import os
import django
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blog_project.settings')
import django
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from blog.models import Post
from django.utils import timezone

User = get_user_model()

USERNAME = 'publish_tester'
PASSWORD = 'TestPass123!'
EMAIL = 'publish_tester@example.com'

# Create or get user
user, created = User.objects.get_or_create(username=USERNAME, defaults={'email': EMAIL})
if created:
    user.set_password(PASSWORD)
    user.save()
    print('Created test user')
else:
    # ensure password is correct for login
    user.set_password(PASSWORD)
    user.save()
    print('Ensured test user exists and password set')

# Create a draft post
title = f'Test Publish Post {timezone.now().timestamp()}'
post = Post.objects.create(author=user, title=title, content='Sample content for publish test', status='draft')
print('Created draft post:', post.slug)

c = Client()
logged = c.login(username=USERNAME, password=PASSWORD)
print('Logged in:', logged)

# Publish
resp = c.post(f'/post/{post.slug}/publish/')
print('Publish POST status:', resp.status_code)
post.refresh_from_db()
print('Post status after publish:', post.status, 'published_at=', post.published_at)

# Unpublish
resp2 = c.post(f'/post/{post.slug}/unpublish/')
print('Unpublish POST status:', resp2.status_code)
post.refresh_from_db()
print('Post status after unpublish:', post.status, 'published_at=', post.published_at)

print('Done')
