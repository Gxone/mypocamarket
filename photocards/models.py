from django.db import models


class PhotoCard(models.Model):
    title = models.CharField('포토카드명', max_length=128)
    artist_set = models.ManyToManyField(
        'Artist',
        verbose_name='아티스트',
        related_name='photocard_set',
        related_query_name='photocard'
    )


class Group(models.Model):
    name = models.CharField('그룹명', max_length=64)


class Artist(models.Model):
    name = models.CharField('이름', max_length=64)
    group = models.ForeignKey(
        'Group',
        verbose_name='그룹',
        related_name='artist_set',
        related_query_name='artist',
        on_delete=models.SET_NULL,
        null=True
    )
