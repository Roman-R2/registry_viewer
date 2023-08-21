from django.contrib.auth import get_user_model
from django.contrib.auth.backends import RemoteUserBackend

from authapp.models import AppExtendedUser
from authapp.services import get_client_ip
from statisticapp.choices import ActivityChoices
from statisticapp.services import SaveUserActivityStatistics

UserModel = get_user_model()


class AppRemoteUserBackend(RemoteUserBackend):
    create_unknown_user = False

    def clean_username(self, username):
        """
        Perform any cleaning on the "username" prior to using it to get or
        create the user object.  Return the cleaned username.

        By default, return the username unchanged.
        """
        return username.upper()

    def authenticate(self, request, remote_user):
        """
        The username passed as ``remote_user`` is considered trusted. Return
        the ``User`` object with the given username. Create a new ``User``
        object if ``create_unknown_user`` is ``True``.

        Return None if ``create_unknown_user`` is ``False`` and a ``User``
        object with the given username is not found in the database.
        """
        if not remote_user:
            return
        user = None
        username = self.clean_username(remote_user)

        # Note that this could be accomplished in one try-except clause, but
        # instead we use get_or_create when creating unknown users since it has
        # built-in safeguards for multiple threads.
        if self.create_unknown_user:
            user, created = UserModel._default_manager.get_or_create(**{
                UserModel.USERNAME_FIELD: username
            })
            if created:
                user = self.configure_user(request, user)
        else:
            try:
                user = None
                users = AppExtendedUser.objects.all()
                for this_user in users:
                    if this_user.username.upper() == self.clean_username(username):
                        user = this_user
            except UserModel.DoesNotExist:
                pass

        # Запишем данные о том, что пользователь вошел в систему
        # if self.user_can_authenticate(user):
            # SaveUserActivityStatistics.with_data(
            #     user=user,
            #     user_ip=get_client_ip(request),
            #     activity=ActivityChoices.LOGIN,
            #     addition_data=f'Пользователь {user.username} произвел вход в систему.'
            # )

        return user if self.user_can_authenticate(user) else None

