from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from .services import UserService, generate_secure_password
from .validators import validate_username, validate_phone_number

User = get_user_model()


class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123',
            role='USER'
        )

    def test_user_creation(self):
        """Test tạo user thành công"""
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.role, 'USER')
        self.assertTrue(self.user.check_password('TestPass123'))

    def test_user_string_representation(self):
        """Test __str__ method"""
        self.assertEqual(str(self.user), 'test@example.com')


class UserServiceTest(TestCase):
    def test_create_user_success(self):
        """Test tạo user qua service"""
        result = UserService.create_user(
            username='newuser',
            email='newuser@example.com',
            fullname='Nguyen Van A',
            role='USER'
        )
        self.assertTrue(result['success'])
        self.assertIsNotNone(result['password'])
        
        user = User.objects.get(username='newuser')
        self.assertEqual(user.email, 'newuser@example.com')

    def test_create_user_duplicate_username(self):
        """Test tạo user với username đã tồn tại"""
        User.objects.create_user(username='existing', email='ex1@example.com', password='pass')
        
        result = UserService.create_user(
            username='existing',
            email='ex2@example.com',
            fullname='Test User',
            role='USER'
        )
        self.assertFalse(result['success'])
        self.assertIn('đã tồn tại', result['error'])

    def test_reset_password(self):
        """Test reset password"""
        user = User.objects.create_user(username='testuser', email='test@example.com', password='old')
        
        result = UserService.reset_password('testuser')
        self.assertTrue(result['success'])
        
        user.refresh_from_db()
        self.assertTrue(user.check_password(result['password']))
        self.assertFalse(user.is_password_changed)


class ValidatorTest(TestCase):
    def test_validate_username_valid(self):
        """Test username hợp lệ"""
        self.assertTrue(validate_username('user123'))
        self.assertTrue(validate_username('test_user'))

    def test_validate_username_invalid(self):
        """Test username không hợp lệ"""
        with self.assertRaises(Exception):
            validate_username('ab')  # Quá ngắn
        
        with self.assertRaises(Exception):
            validate_username('user@123')  # Ký tự không hợp lệ

    def test_validate_phone_valid(self):
        """Test số điện thoại hợp lệ"""
        self.assertTrue(validate_phone_number('0912345678'))
        self.assertTrue(validate_phone_number('+84912345678'))

    def test_validate_phone_invalid(self):
        """Test số điện thoại không hợp lệ"""
        with self.assertRaises(Exception):
            validate_phone_number('123456')


class LoginViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123',
            role='USER'
        )

    def test_login_page_loads(self):
        """Test trang login load được"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_login_success(self):
        """Test đăng nhập thành công"""
        response = self.client.post(reverse('login'), {
            'username': 'test@example.com',
            'password': 'TestPass123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect

    def test_login_invalid_credentials(self):
        """Test đăng nhập sai thông tin"""
        response = self.client.post(reverse('login'), {
            'username': 'test@example.com',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sai email hoặc mật khẩu')

    def test_login_inactive_user(self):
        """Test đăng nhập với user bị khóa"""
        self.user.is_active = False
        self.user.save()
        
        response = self.client.post(reverse('login'), {
            'username': 'test@example.com',
            'password': 'TestPass123'
        })
        self.assertContains(response, 'bị khóa')


class PasswordGeneratorTest(TestCase):
    def test_password_length(self):
        """Test độ dài password"""
        pwd = generate_secure_password(12)
        self.assertEqual(len(pwd), 12)

    def test_password_characters(self):
        """Test password có đủ loại ký tự"""
        pwd = generate_secure_password(20)
        has_upper = any(c.isupper() for c in pwd)
        has_lower = any(c.islower() for c in pwd)
        has_digit = any(c.isdigit() for c in pwd)
        
        self.assertTrue(has_upper or has_lower)
        self.assertTrue(has_digit)
