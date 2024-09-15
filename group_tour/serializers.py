from rest_framework import serializers
from django.contrib.auth import get_user_model
from accounts.models import Group

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
