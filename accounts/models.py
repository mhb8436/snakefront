from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser, AbstractBaseUser,BaseUserManager
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from django.db import models
from rest_framework.authtoken.models import Token
# Create your models here.

class CustomUserManager(BaseUserManager):
    def _create_user(
        self, email, password, is_staff, is_superuser, **extra_fields
    ):
        print('_create_user')
        if not email:
            raise ValueError('You must provide an email address')
        user = self.model(
            email = email,
            is_staff = is_staff,
            is_superuser = is_superuser,
            is_active = True,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_user(self, email, password, **extra_fields):
        self._create_user(email, password, False, False, **extra_fields)
    
    def create_superuser(self, email, password, **extra_fields):
        self._create_user(email, password, True, True, **extra_fields)
    
    def add_superuser(self, user):
        print('add_superuser')
        user.is_superuser = True
        user.save(using=self._db)
        return user
    
    def add_staff(self, user):
        print('add_staff')
        user.is_staff = True
        user.save(using=self._db)
        return user


class CustomUser(AbstractUser):

    email = models.EmailField(_("Email"), max_length=255, unique=True)
    nickname = models.CharField(_("Nick Name"), max_length=255, blank=True, null=True)

    agree_terms = models.BooleanField(_("Agree Temrs"),default=False)
    agree_terms_date = models.DateTimeField(_("Agree Temr Date"),blank=True, default=None, null=True)
    notebook_token = models.CharField(
        _("NoteBook Token"),
        max_length=36, default=None, null=True, blank=True
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()
    class Meta:
        verbose_name = "User"
        # app_label = "accounts"
    
    def __str__(self):
        return self.email


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    """Create a token for the user when the user is created (with oAuth2)

    1. Assign user a token
    2. Assign user to default group

    Create a Profile instance for all newly created User instances. We only
    run on user creation to avoid having to check for existence on each call
    to User.save.

    """
    # This auth token is intended for APIs
    if created and "api" in settings.PLUGINS_ENABLED:
        Token.objects.create(user=instance)