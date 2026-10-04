from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class AuthApiTests(TestCase):
    def setUp(self):
        self.client_class = self.client.__class__

    def test_register_creates_user_and_profile(self):
        payload = {
            'username': 'player_one',
            'email': 'player@example.com',
            'nickname': 'MountainKnight',
            'password': 'example-password',
            'password_confirm': 'example-password',
        }

        response = self.client.post(reverse('auth-register'), payload, content_type='application/json')

        self.assertEqual(response.status_code, 201)
        self.assertTrue(User.objects.filter(username='player_one').exists())
        user = User.objects.get(username='player_one')
        self.assertEqual(user.profile.nickname, 'MountainKnight')
        self.assertEqual(user.profile.avatar_key, 'knight-1')
        self.assertTrue(user.check_password('example-password'))
        self.assertNotIn('password', response.json())

    def test_register_rejects_duplicate_username_email_and_nickname(self):
        user = User.objects.create_user(
            username='player_one',
            email='first@example.com',
            password='example-password',
        )
        user.profile.nickname = 'FirstKnight'
        user.profile.save()

        payload = {
            'username': 'player_one',
            'email': 'second@example.com',
            'nickname': 'SecondKnight',
            'password': 'example-password',
            'password_confirm': 'example-password',
        }
        response = self.client.post(reverse('auth-register'), payload, content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('username', response.json()['errors'])

        payload = {
            'username': 'player_two',
            'email': 'first@example.com',
            'nickname': 'ThirdKnight',
            'password': 'example-password',
            'password_confirm': 'example-password',
        }
        response = self.client.post(reverse('auth-register'), payload, content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('email', response.json()['errors'])

        payload = {
            'username': 'player_three',
            'email': 'third@example.com',
            'nickname': 'FirstKnight',
            'password': 'example-password',
            'password_confirm': 'example-password',
        }
        response = self.client.post(reverse('auth-register'), payload, content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('nickname', response.json()['errors'])

    def test_register_rejects_mismatched_passwords(self):
        payload = {
            'username': 'player_alpha',
            'email': 'alpha@example.com',
            'nickname': 'AlphaKnight',
            'password': 'example-password',
            'password_confirm': 'different-password',
        }

        response = self.client.post(reverse('auth-register'), payload, content_type='application/json')

        self.assertEqual(response.status_code, 400)
        self.assertIn('password_confirm', response.json()['errors'])

    def test_login_creates_session_and_me_returns_current_user(self):
        user = User.objects.create_user(
            username='player_one',
            email='player@example.com',
            password='example-password',
        )
        user.profile.nickname = 'MountainKnight'
        user.profile.save()

        response = self.client.post(
            reverse('auth-login'),
            {'username': 'player_one', 'password': 'example-password'},
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['username'], 'player_one')

        me_response = self.client.get(reverse('auth-me'))
        self.assertEqual(me_response.status_code, 200)
        self.assertEqual(me_response.json()['profile']['nickname'], 'MountainKnight')

    def test_login_rejects_invalid_credentials_and_no_session(self):
        User.objects.create_user(
            username='player_wrong',
            email='wrong@example.com',
            password='example-password',
        )

        response = self.client.post(
            reverse('auth-login'),
            {'username': 'player_wrong', 'password': 'bad-password'},
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('non_field_errors', response.json()['errors'])

        me_response = self.client.get(reverse('auth-me'))
        self.assertIn(me_response.status_code, (401, 403))

    def test_me_requires_authenticated_user(self):
        response = self.client.get(reverse('auth-me'))

        self.assertIn(response.status_code, (401, 403))

    def test_me_patch_updates_profile_fields(self):
        user = User.objects.create_user(
            username='player_two',
            email='player2@example.com',
            password='example-password',
        )
        self.client.force_login(user)

        response = self.client.patch(
            reverse('auth-me'),
            {'nickname': 'NewKnight', 'avatar_key': 'knight-3'},
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        user.refresh_from_db()
        self.assertEqual(user.profile.nickname, 'NewKnight')
        self.assertEqual(user.profile.avatar_key, 'knight-3')

    def test_me_patch_rejects_protected_fields(self):
        user = User.objects.create_user(
            username='player_three',
            email='player3@example.com',
            password='example-password',
        )
        self.client.force_login(user)

        response = self.client.patch(
            reverse('auth-me'),
            {'id': 99, 'username': 'hacker', 'is_staff': True},
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('errors', response.json())

    def test_logout_ends_session(self):
        user = User.objects.create_user(
            username='player_four',
            email='player4@example.com',
            password='example-password',
        )
        self.client.force_login(user)

        response = self.client.post(reverse('auth-logout'))

        self.assertEqual(response.status_code, 204)
        me_response = self.client.get(reverse('auth-me'))
        self.assertIn(me_response.status_code, (401, 403))

    def test_csrf_cookie_and_valid_csrf_request_succeeds(self):
        user = User.objects.create_user(
            username='player_five',
            email='player5@example.com',
            password='example-password',
        )

        csrf_response = self.client.get(reverse('auth-csrf'))
        self.assertEqual(csrf_response.status_code, 204)
        csrftoken = self.client.cookies['csrftoken'].value

        self.client = self.client_class(enforce_csrf_checks=True)
        self.client.cookies['csrftoken'] = csrftoken
        self.client.force_login(user)
        self.client.defaults['HTTP_X_CSRFTOKEN'] = csrftoken

        response = self.client.patch(
            reverse('auth-me'),
            {'nickname': 'CsrfKnight', 'avatar_key': 'knight-2'},
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['profile']['nickname'], 'CsrfKnight')
   
    def test_unsafe_request_without_csrf_token_is_rejected(self):
        user = User.objects.create_user(
            username='player_six',
            email='player6@example.com',
            password='example-password',
        )

        self.client = self.client_class(enforce_csrf_checks=True)
        self.client.force_login(user)

        response = self.client.patch(
            reverse('auth-me'),
            {'nickname': 'NoCsrfKnight'},
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 403)