"""Dynamic/randomized test data generation (Faker) so tests never rely on
hard-coded, reusable inputs -- each run exercises fresh data."""
import uuid
from dataclasses import dataclass, field

from faker import Faker

fake = Faker()


@dataclass
class UserData:
    username: str
    email: str
    password: str


@dataclass
class ArticleData:
    title: str
    description: str
    body: str
    tags: list[str] = field(default_factory=list)


def random_user() -> UserData:
    """The Conduit API rejects usernames over 20 chars, so keep this short
    and collision-safe for parallel workers instead of using a Faker name."""
    unique = uuid.uuid4().hex[:12]
    return UserData(
        username=f"qa{unique}",
        email=f"qa{unique}@example.com",
        password=fake.password(length=14, special_chars=True, digits=True, upper_case=True),
    )


def random_article() -> ArticleData:
    return ArticleData(
        title=f"{fake.catch_phrase()} {uuid.uuid4().hex[:6]}",
        description=fake.sentence(nb_words=8),
        body=fake.paragraph(nb_sentences=5),
        tags=[fake.word(), fake.word()],
    )


def random_bio() -> str:
    return fake.paragraph(nb_sentences=3)


def random_image_url() -> str:
    return f"https://picsum.photos/seed/{uuid.uuid4().hex[:8]}/200/200"
