from ..models import Tours
from django.db.models import Q

def filter_type(areacode, tour_type):
    if tour_type == '힐링형 감자':
        tour_data = Tours.objects.filter(
        sigungucode=areacode
        ).filter(
            Q(cat2='A0101') | Q(cat3='A02010800') | Q(cat3='A02020300') | Q(cat3='A02020600') | Q(cat3='A02020700') | Q(cat3='A03030500') | Q(cat3='A03030600') | Q(cat3='A02010800')
        )
    elif tour_type == '액티비티형 옥수수':
        tour_data = Tours.objects.filter(
        sigungucode=areacode
        ).filter(
            Q(cat1='A03') | Q(cat3='A02020400') | Q(cat3='A02020500')
        )
    elif tour_type == '관람형 곤드레':
        tour_data = Tours.objects.filter(
        sigungucode=areacode
        ).filter(
            Q(cat2='A0201') | Q(cat3='A02030200') | Q(cat3='A02030300') | Q(cat3='A02050200') | Q(cat3='A02060100') | Q(cat3='A02060200') | Q(cat3='A02060300') | Q(cat3='A02060500') | Q(cat3='A04010700')
        )
    elif tour_type == '미식가형 송이':
        tour_data = Tours.objects.filter(
        sigungucode=areacode
        ).filter(
            Q(cat3='A05020700') | Q(cat3='A05020900') | Q(cat3='A04010100') | Q(cat3='A04010200') | Q(cat3='A02030100') | Q(cat3='A02040600')
        )
    elif tour_type == '사람좋아 쌀알':
        tour_data = Tours.objects.filter(
        sigungucode=areacode
        ).filter(
            Q(cat3='A01011200') | Q(cat3='A02020400') | Q(cat3='A02020600') | Q(cat3='A02020800') | Q(cat3='A02030600') | Q(cat3='A02060400') | Q(cat3='A03021200') | Q(cat3='A03021400') | Q(cat3='A03030800')
        )
    elif tour_type == '도전형 인삼':
        tour_data = Tours.objects.filter(
        sigungucode=areacode
        ).filter(
            Q(cat2='A0203') | Q(cat3='A02020200') | Q(cat3='A02020600') | Q(cat3='A03021800') | Q(cat3='A03022400') | Q(cat3='A03030200') | Q(cat3='A03030400') | Q(cat3='A03040300') | Q(cat3='A03040400')
        )
    elif tour_type == '인플루언서형 복숭아':
        tour_data = Tours.objects.filter(
        sigungucode=areacode
        ).filter(
            Q(cat1='A04') | Q(cat3='A01011200') | Q(cat2='A0202') | Q(cat3='A02030600') | Q(cat3='A02050200') | Q(cat3='A02050600') | Q(cat3='A02060100') | Q(cat3='A02060200') | Q(cat3='A02060300') | Q(cat3='A02060400') | Q(cat3='A02060500')
        )
    elif tour_type == '나무늘보형 순두부':
        tour_data = Tours.objects.filter(
        sigungucode=areacode
        ).filter(
            Q(cat2='A0201') | Q(cat2='A0202') | Q(cat2='A0203') | Q(cat3='A05020900')
        )
    else:
        tour_data = None
    return tour_data