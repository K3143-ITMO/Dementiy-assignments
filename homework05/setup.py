import vkapi
from setuptools import setup  # type: ignore

AUTHOR = "Dmitrii Sorokin"
AUTHOR_EMAIL = "dementiy@yandex.ru"
HOME_PAGE = "https://github.com/Dementiy/pybook-assignments"

setup(
    name="vkapi",
    version="0.1.0",
    description="vkapi package",
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    packages=["vkapi"],
    entry_points={"console_scripts": ["vkapi = vkapi.__main__:main"]},
    url=HOME_PAGE,
    license="GPLv3",
    python_requires=">=3.6.0",
)
