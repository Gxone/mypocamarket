from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from photocards.models import PhotoCard, Artist
from sales.models import Sale
from users.models import User


class SaleViewTest(APITestCase):
    def setUp(self):
        # 사용자 생성
        self.seller = User.objects.create_user(name='user_1', email='test1@test.com', password='1234', cash=10000)
        self.buyer = User.objects.create_user(name='user_2', email='test2@test.com', password='1234', cash=10000)

        # 아티스트 및 포토카드 생성
        self.artist = Artist.objects.create(name='artist_1')
        photocard = PhotoCard.objects.create(title='포토카드_ver1')
        photocard.artist_set.add(self.artist)
        self.photocard = photocard

        # 판매 내역 생성
        self.sale = Sale.objects.create(photocard=self.photocard, seller=self.seller, price=2000, state=1)

        # URL
        self.sale_list_url = reverse('sales-list')
        self.sale_detail_url = reverse('sales-detail', args=[self.sale.id])
        self.sale_order_url = reverse('sales-order', args=[self.sale.id])

    def test_sale_list(self):
        """
        판매 목록 조회 테스트
        """
        response = self.client.get(self.sale_list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('count', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
        self.assertIn('results', response.data)

    def test_retrieve_sale(self):
        """
        판매건 상세 조회 테스트
        """
        response = self.client.get(self.sale_detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_price'], response.data['price'] + response.data['fee'])
        self.assertEqual(response.data['photocard']['title'], self.photocard.title)
        artist_ids = [artist['id'] for artist in response.data['photocard']['artist_set']]
        self.assertIn(self.artist.id, artist_ids)

    def test_retrieve_sale_not_found(self):
        """
        존재하지 않는 판매건 상세 조회 테스트
        """
        response = self.client.get(reverse('sales-detail', args=[999]))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_sale(self):
        """
        판매건 생성 테스트
        """
        data = {
            'state': 1,
            'photocard': self.photocard.id,
            'seller': self.seller.id,
            'price': 2000
        }
        response = self.client.post(self.sale_list_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['price'], data['price'])
        self.assertEqual(response.data['state'], data['state'])
        self.assertEqual(response.data['photocard'], data['photocard'])

        # Sale 객체 생성 확인
        self.assertEqual(Sale.objects.count(), 2)

    def test_order(self):
        """
        포토카드 구매 테스트
        """
        data = {
            'buyer': self.buyer.id
        }
        response = self.client.post(self.sale_order_url, data, format='json')

        self.sale.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.sale.buyer.id, data['buyer'])
        self.assertEqual(self.sale.state, 2)  # (2, '판매 완료')
        self.assertIsNotNone(self.sale.sold_date)
        # TODO: Cash, Order, Payment 모델을 추가할 경우 필요한 테스트 작성

    def test_order_not_on_sale(self):
        """
        유효하지 않은 상태의 판매건 구매 테스트
        """
        data = {
            'buyer': self.buyer.id
        }

        self.sale.state = 2
        self.sale.save()

        response = self.client.post(self.sale_order_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_order_not_min_price(self):
        """
        최소 가격이 아닌 판매건 구매 테스트
        """
        data = {
            'buyer': self.buyer.id
        }

        Sale.objects.create(photocard=self.photocard, seller=self.seller, price=1500, state=1)  # 최소 가격의 새로운 판매건 생성
        response = self.client.post(self.sale_order_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_order_same_buyer_seller(self):
        """
        판매자와 구매자 동일 여부 테스트
        """
        data = {
            'buyer': self.seller.id  # 구매자와 판매자를 동일하게 설정
        }

        response = self.client.post(self.sale_order_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_order_not_enough_cash(self):
        """
        구매자의 캐쉬가 부족한 경우 테스트
        """
        self.buyer.cash = 500  # 캐쉬 부족 상태로 설정
        self.buyer.save()

        data = {
            'buyer': self.buyer.id
        }
        response = self.client.post(self.sale_order_url, data, format='json')

        # 응답 상태 코드 확인
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
