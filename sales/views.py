from django.db import transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from sales.models import Sale
from sales.serializers import SaleSerializer, SaleCreateSerializer, SaleDetailSerializer
from users.models import User
from config.pagination import CustomPagination


class SaleViewSet(ViewSet):
    pagination_class = CustomPagination

    def list(self, request):
        """
        판매 목록 조회
        """
        # 판매 중 상태인 최소 가격의 판매건
        queryset = Sale.objects.prefetch_related('photocard__artist_set').annotate(
            rank_in_price=Sale.get_annotate_fields()['rank_in_price']
        ).filter(state=1, rank_in_price=1).order_by('-id')

        # 페이지네이션
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)

        if page is not None:
            serializer = SaleSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = SaleSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        """
        판매 개별 조회
        """
        queryset = Sale.objects.prefetch_related('photocard__artist_set')
        sale = get_object_or_404(queryset, pk=pk)
        serializer = SaleDetailSerializer(sale)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        """
        판매 등록
        """
        serializer = SaleCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='order')
    def order(self, request, pk=None):
        """
        포토카드 구매
        1. 판매 상태 여부 확인
        2. 최소 가격 여부 확인
        3. 판매자와 구매자 동일 여부 확인
        """
        sale = get_object_or_404(Sale, id=pk)

        # 판매 상태 여부
        if sale.state != 1:  # (1, '판매 중')
            return Response({'detail': '판매 중인 상태가 아닙니다.'}, status=status.HTTP_400_BAD_REQUEST)

        # 최소 가격 여부
        try:
            sales = Sale.objects.annotate(rank_in_price=Sale.get_annotate_fields()['rank_in_price']).filter(
                photocard=sale.photocard, state=1
            )
            min_price_sale_id = sales.get(rank_in_price=1).id
        except Sale.DoesNotExist:
            return Response({'detail': '최소 가격의 판매건을 찾을 수 없습니다.'}, status=status.HTTP_400_BAD_REQUEST)

        # 구매하려는 판매건과 최소 가격 판매건이 다를 경우
        if int(pk) != min_price_sale_id:
            return Response(
                {'detail': '최소 가격의 판매건이 아닙니다.', 'min_price_sale_id': min_price_sale_id},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 판매자와 구매자 동일 여부
        buyer = get_object_or_404(User, id=request.data['buyer'])
        if buyer == sale.seller:
            return Response({'detail': '판매자와 구매자가 동일할 수 없습니다.'}, status=status.HTTP_400_BAD_REQUEST)

        # 판매 처리
        with transaction.atomic():
            # 판매
            # TODO: Cash, Order, Payment 모델 추가
            sale.buyer = buyer
            sale.state = 2  # (2, 판매 완료)
            sale.sold_date = timezone.now()
            sale.save()

            # 구매자 캐쉬 차감
            if buyer.cash < sale.total_price:
                return Response({'detail': '캐쉬가 부족합니다.'}, status=status.HTTP_400_BAD_REQUEST)
            buyer.cash -= sale.total_price
            buyer.save()

            # 판매자 캐쉬 부여
            sale.seller.cash += sale.price
            sale.seller.save()
            return Response({'detail': '구입이 완료되었습니다.'}, status=status.HTTP_200_OK)
