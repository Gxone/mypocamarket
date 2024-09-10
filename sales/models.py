from django.db import models
from django.db.models import Window, F
from django.db.models.functions import RowNumber

class Sale(models.Model):
    STATE_CHOICES = (
        (1, '판매 중'),
        (2, '판매 완료')
    )

    state = models.PositiveSmallIntegerField('판매 상태', choices=STATE_CHOICES, default=1)
    photocard = models.ForeignKey(
        'photocards.PhotoCard',
        verbose_name='포토카드',
        related_name='sale_set',
        related_query_name='sale',
        on_delete=models.PROTECT
    )
    seller = models.ForeignKey(
        'users.User',
        verbose_name='판매자',
        related_name='sale_set',
        related_query_name='sale',
        on_delete=models.PROTECT
    )
    buyer = models.ForeignKey(
        'users.User',
        verbose_name='구매자',
        related_name='order_set',
        related_query_name='order',
        on_delete=models.PROTECT,
        null=True
    )
    price = models.PositiveIntegerField('판매 가격', default=0)
    fee = models.PositiveIntegerField('수수료', default=0)

    create_date = models.DateTimeField('생성 일시', auto_now_add=True)
    renewal_date = models.DateTimeField('수정 일시', auto_now=True)
    sold_date = models.DateTimeField('판매 일시', null=True)

    @property
    def total_price(self):
        return self.price + self.fee

    @property
    def recent_order_price_list(self):
        """
        최근 거래가를 반환합니다.
        """
        recent_order_prices = Sale.objects.filter(
            state=2,  # (2, '판매 완료')
            photocard=self.photocard
        ).order_by('-sold_date').values_list('price', flat=True)[:5]
        return list(recent_order_prices)

    @classmethod
    def get_annotate_fields(cls):
        """
        자주 쓰이는 annotate 필드 표현식을 반환합니다.
        """
        return {
            # 최소 가격을 구하기 위한 표현식
            'rank_in_price': Window(
                expression=RowNumber(),
                partition_by=F('photocard_id'),
                order_by=[F('price'), F('renewal_date').desc()]
            )
        }

    def save(self, *args, **kwargs):
        # 수수료 = 판매가 * 0.2
        self.fee = self.price * 0.2
        super().save(*args, **kwargs)
