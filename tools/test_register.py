import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blog_project.settings')
import sys
from pathlib import Path
# Ensure project root is on sys.path so imports of blog_project work
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

django.setup()
from django.test import Client

c = Client()
# Attempt registration with sample data
payload = {
    'username': 'testuser1',
    'email': 'testuser1@example.com',
    'password1': 'ComplexPwd123!',
    'password2': 'ComplexPwd123!',
}
resp = c.post('/register/', payload)
print('Status code:', resp.status_code)
# If form re-rendered, context may have 'form' with errors
if resp.status_code == 200 and resp.context:
    form = resp.context.get('form')
    if form:
        print('Form valid:', form.is_valid())
        print('Form errors:', form.errors.as_json())
    else:
        print('No form in context; response length:', len(resp.content))
else:
    # Redirect probably to post_list
    print('Response redirected to:', resp.url if hasattr(resp, 'url') else 'N/A')

# Try a second attempt with mismatched passwords to see validation
payload2 = payload.copy()
payload2['username'] = 'testuser2'
payload2['email'] = 'testuser2@example.com'
payload2['password2'] = 'mismatch'
resp2 = c.post('/register/', payload2)
print('\nSecond attempt status:', resp2.status_code)
if resp2.status_code == 200 and resp2.context:
    form2 = resp2.context.get('form')
    if form2:
        print('Form2 valid:', form2.is_valid())
        print('Form2 errors:', form2.errors.as_json())

print('\nDone')
