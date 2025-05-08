from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError

User = get_user_model()

class Command(BaseCommand):
    help = 'Creates a superuser with predefined credentials'

    def handle(self, *args, **options):
        email = 'admin@example.com'
        password = 'adminpass123'
        first_name = 'Admin'
        last_name = 'User'
        phone = '1234567890'  # Adding a default phone number
        
        try:
            # Check if user already exists
            if User.objects.filter(email=email).exists():
                user = User.objects.get(email=email)
                user.is_staff = True
                user.is_superuser = True
                user.set_password(password)
                user.save()
                self.stdout.write(self.style.SUCCESS(f'Updated admin user: {email}'))
            else:
                # Create a new superuser
                User.objects.create_superuser(
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    phone=phone
                )
                self.stdout.write(self.style.SUCCESS(f'Created admin user: {email}'))
            
            # Output the credentials
            self.stdout.write(self.style.SUCCESS('Admin credentials:'))
            self.stdout.write(self.style.SUCCESS(f'Email: {email}'))
            self.stdout.write(self.style.SUCCESS(f'Password: {password}'))
            
        except IntegrityError as e:
            self.stdout.write(self.style.ERROR(f'Error creating admin user: {str(e)}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Unexpected error: {str(e)}')) 