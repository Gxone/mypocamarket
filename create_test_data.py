# 테스트 데이터를 위한 임시 파일
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mypocamarket.settings')

application = get_wsgi_application()

import random
from random import randint

from photocards.models import Group, Artist, PhotoCard
from sales.models import Sale
from users.models import User

# group 생성
groups = [Group(name='group_{}'.format(i)) for i in range(5)]
Group.objects.bulk_create(groups)

# artist 생성
artists = [Artist(name='artist_{}'.format(i), group_id=randint(1, 5)) for i in range(10)]
Artist.objects.bulk_create(artists)

# user 생성
for i in range(5):
    User.objects.create_user(name='user_{}'.format(i), email='test{}@test.com'.format(i), password='1234', cash=10000)

# photocard 생성
photocard_list = [PhotoCard(title='포토카드_ver{}'.format(i)) for i in range(10)]
photocards = PhotoCard.objects.bulk_create(photocard_list)

for photocard in photocards:
    photocard.artist_set.set([randint(1, 10)])

# sale 생성
sales = []
for i in range(30):
    price = random.randrange(0, 30000, 500)
    sale = Sale(photocard=PhotoCard.objects.get(id=randint(1, 10)), seller_id=randint(1, 5), price=price, fee=price * 0.2)
    sales.append(sale)
Sale.objects.bulk_create(sales)
