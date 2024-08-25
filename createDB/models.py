from django.db import models
from django.conf import settings

# Create your models here.

# 국문관광지 데이터
class Tours(models.Model):
  sigungucode = models.IntegerField()
  addr1 = models.TextField()
  addr2 = models.TextField()
  image = models.TextField(null=True)
  cat1 = models.CharField(max_length=3)
  cat2 = models.CharField(max_length=5)
  cat3 = models.CharField(max_length=9)
  type_id = models.IntegerField()
  mapx = models.FloatField()
  mapy = models.FloatField()
  title = models.TextField(null=True)
  zipcode = models.TextField(null=True)
  tel = models.TextField(null=True)
  eventstartdate = models.DateTimeField(null=True)
  eventenddate = models.DateTimeField(null=True)
  

class Groups(models.Model):
  users = models.ManyToManyField(
    settings.AUTH_USER_MODEL, related_name='joined_group', through='Group_Members'
    )
  people_num = models.IntegerField()
  tour_type = models.CharField(max_length=10, null=True)
  group_name = models.CharField(max_length=20)

class Routes_plan(models.Model):
  route_name = models.CharField(max_length=20)
  lodge = models.TextField()
  route_area = models.IntegerField()
  tour_startdate = models.DateTimeField(null=True, blank=True)
  tour_enddate = models.DateTimeField(null=True, blank=True)
  group = models.ForeignKey(Groups, on_delete=models.CASCADE, null=True, blank=True)
  route_details = models.ManyToManyField(Tours, related_name='get_routes', through='Tour_plan_data')


# 지금 상황에서는 중개 테이블이 필요 없지만, 나중에 추가 정보 저장 가능성을 위해 제작
class Tour_plan_data(models.Model):
  tour = models.ForeignKey(Tours, on_delete=models.CASCADE)
  route = models.ForeignKey(Routes_plan, on_delete=models.CASCADE)
  tour_seq = models.IntegerField()

class Group_Members(models.Model):
  users = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
  group = models.ForeignKey(Groups, on_delete=models.CASCADE)