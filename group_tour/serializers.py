from rest_framework import serializers
from django.contrib.auth import get_user_model
from accounts.models import Group
from createDB.models import Tours
from .models import GroupTourList, GroupTourOrder

class GroupSerializer(serializers.ModelSerializer):
    User = get_user_model()
    members = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True, required=False)
    leader = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=True)
   
    class Meta:
        model = Group
        fields = ['id', 'name', 'members', 'leader', 'region', 'start_date', 'end_date']
        
    def create(self, validated_data):
        members = validated_data.pop('members', [])
        leader = validated_data.pop('leader')
        group = Group.objects.create(leader=leader, **validated_data)
        group.members.set(members)
        return group

class GroupListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        # tour 목록도 조회 가능하도록 수정 필요
        fields = ['id', 'name', 'start_date', 'end_date', 'region']

class ToursSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tours
        fields = ['id', 'title', 'addr1', 'mapx', 'mapy']

class GroupTourOrderSerializer(serializers.ModelSerializer):
    tour = ToursSerializer() 

    class Meta:
        model = GroupTourOrder
        fields = ['order', 'tour']

class GroupTourListSerializer(serializers.ModelSerializer):
    tour_list = GroupTourOrderSerializer(source='grouptourorder_set', many=True)

    class Meta:
        model = GroupTourList
        fields = ['group', 'tour_list']

    def update(self, instance, validated_data):
        tour_ids = validated_data.pop('tour_list', [])
        GroupTourOrder.objects.filter(group_tour_list=instance).delete()
        
        # for order, tour_id in enumerate(tour_ids):
        #     try:
        #         tour = Tours.objects.get(id=tour_id)
        #     except Tours.DoesNotExist:
        #         raise serializers.ValidationError(f'Tour with ID {tour_id} does not exist.')
            
        #     GroupTourOrder.objects.create(
        #         group_tour_list=instance,
        #         tour=tour,
        #         order=order
        #     )

        instance.save()
        return instance