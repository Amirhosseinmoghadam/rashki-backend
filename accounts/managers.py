from django.contrib.auth.models import (
    BaseUserManager,
)


class UserManager(BaseUserManager):

    def create_user(
        self,
        phone_number,
        password=None,
        **extra_fields,
    ):
        if not phone_number:
            raise ValueError("Phone number is required.")

        phone_number = phone_number.strip()

        user = self.model(
            phone_number=phone_number,
            **extra_fields,
        )

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save(using=self._db)

        return user

    def create_superuser(
        self,
        phone_number,
        password=None,
        **extra_fields,
    ):
        extra_fields.setdefault(
            "is_staff",
            True,
        )

        extra_fields.setdefault(
            "is_superuser",
            True,
        )

        extra_fields.setdefault(
            "is_active",
            True,
        )

        if not extra_fields.get("is_staff"):
            raise ValueError("Superuser must have " "is_staff=True.")

        if not extra_fields.get("is_superuser"):
            raise ValueError("Superuser must have " "is_superuser=True.")

        if not password:
            raise ValueError("Superuser must have a password.")

        return self.create_user(
            phone_number=phone_number,
            password=password,
            **extra_fields,
        )
