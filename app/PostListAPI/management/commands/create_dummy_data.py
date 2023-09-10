from django.core.management import BaseCommand
from django.contrib.auth.models import User
from PostListAPI.models import Post, Follow
from django_seed import Seed


class Command(BaseCommand):
    help = "This command creates random users and posts"

    def handle(self, *args, **kwargs):
        seeder = Seed.seeder()

        # Seed users
        seeder.add_entity(
            User,
            5,
            {
                "username": seeder.faker.user_name(),
                "email": seeder.faker.email(),
                "password": "1234",
            },
        )
        created_users = seeder.execute()
        created_users_pks = created_users[User]

        # Seed posts
        for user_pk in created_users_pks:
            user = User.objects.get(pk=user_pk)
            seeder.add_entity(
                Post,
                3,
                {
                    "title": seeder.faker.sentence(nb_words=5),
                    "content": seeder.faker.text(max_nb_chars=20),
                    "author": user,
                },
            )
        seeder.execute()

        # Seed follows
        for i in range(len(created_users_pks) - 1):
            follower = User.objects.get(pk=created_users_pks[i])
            following = User.objects.get(pk=created_users_pks[i + 1])
            Follow.objects.create(follower=follower, following=following)

        self.stdout.write(self.style.SUCCESS("Data seeded successfully"))
