from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.db import models


class UserManager(BaseUserManager):
    def _create_user(self, email, name, password, **other_fields):
        if not email:
            raise ValueError('이메일은 필수로 설정되어야 합니다.')
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, **other_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, name, password, **other_fields):
        return self._create_user(email, name, password, **other_fields)

    def create_superuser(self, email, name, password, **other_fields):
        return self._create_user(email, name, password, **other_fields)


class User(AbstractBaseUser):
    GENDER_CHOICES = (
        ('M', '남성'),
        ('F', '여성')
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    name = models.CharField('이름', max_length=12)
    email = models.EmailField('이메일 주소', unique=True)
    gender = models.CharField('성별', max_length=1, choices=GENDER_CHOICES, null=True)
    birth = models.DateField('생년월일', null=True)
    cash = models.IntegerField('캐쉬', default=10000)  # TODO: Cash 모델 추가 후 마이그레이션 필요

    objects = UserManager()
