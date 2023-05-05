from django_seed import Seed

from .models import Medicine, PLATFORMS


def seed_data():
    seeder = Seed.seeder()
    seeder.add_entity(Medicine, 50, {
        'name': lambda x: seeder.faker.name(),
        'salt_name': lambda x: seeder.faker.text(),
        'price': lambda x: seeder.faker.random_int(min=1, max=1000),
        'med_image': lambda x: seeder.faker.image_url(),
        'platform': lambda x: seeder.faker.random_element(elements=[choice[0] for choice in PLATFORMS]),
        'dosage': lambda x: seeder.faker.random_int(min=1, max=100),
    })
    inserted_pks = seeder.execute()
    print(f"{len(inserted_pks[Medicine]):,} medicine records seeded successfully.")
