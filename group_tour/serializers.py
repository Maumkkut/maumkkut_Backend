from rest_framework import serializers
from django.contrib.auth import get_user_model
from accounts.models import Group
from createDB.models import Tours
from .models import GroupTourList, GroupTourOrder, LikeDislike

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
        fields = ['id', 'title', 'addr1', 'mapx', 'mapy', 'image']

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

class LikeDislikeSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = LikeDislike
        fields = ['user', 'tour', 'is_liked', 'is_disliked']
    
    def validate(self, data):
        # 좋아요와 싫어요가 동시에 True일 수 없도록 검증
        if data.get('is_liked') and data.get('is_disliked'):
            raise serializers.ValidationError("좋아요와 싫어요를 동시에 선택할 수 없습니다.")
        return data 
    
    
class LikeTourOrderSerializer(serializers.ModelSerializer):
    is_liked = serializers.SerializerMethodField()
    is_disliked = serializers.SerializerMethodField()
    tour_id = serializers.IntegerField(source='tour.id')
    tour_name = serializers.CharField(source='tour.title')
    class Meta:
        model = GroupTourOrder
        fields = ['tour_id', 'tour_name', 'is_liked', 'is_disliked']

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return LikeDislike.objects.filter(user=request.user, tour=obj.tour, is_liked=True).exists()
        return False

    def get_is_disliked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return LikeDislike.objects.filter(user=request.user, tour=obj.tour, is_disliked=True).exists()
        return False


class LikeTourListSerializer(serializers.ModelSerializer):
    tour_list = serializers.SerializerMethodField()

    class Meta:
        model = GroupTourList
        fields = ['group', 'tour_list']

    def get_tour_list(self, obj):
        serializer = LikeTourOrderSerializer(obj.grouptourorder_set.all(), many=True, context=self.context)
        return serializer.data

class GroupLikeOrderSerializer(serializers.ModelSerializer):
    tour_id = serializers.IntegerField(source='tour.id')
    tour_name = serializers.CharField(source='tour.title')
    like_count = serializers.SerializerMethodField()
    dislike_count = serializers.SerializerMethodField()
    like_members = serializers.SerializerMethodField()
    dislike_members = serializers.SerializerMethodField()

    class Meta:
        model = GroupTourOrder
        fields = ['tour_id', 'tour_name', 'like_count', 'dislike_count', 'like_members', 'dislike_members']

    def get_like_count(self, obj):
        request = self.context.get('request')
        group_id = request.GET.get('group_id')
        group = Group.objects.get(id=group_id)
        users = group.get_members_with_leader()
        if not group:
            return 0
        return LikeDislike.objects.filter(user__in=users, tour=obj.tour, is_liked=True).count()

    def get_dislike_count(self, obj):
        request = self.context.get('request')
        group_id = request.GET.get('group_id')
        group = Group.objects.get(id=group_id)
        users = group.get_members_with_leader() 
        if not group:
            return 0
        return LikeDislike.objects.filter(user__in=users, tour=obj.tour, is_disliked=True).count()
    
    def get_like_members(self, obj):
        request = self.context.get('request')
        group_id = request.GET.get('group_id')
        group = Group.objects.get(id=group_id)
        users = group.get_members_with_leader() 
        User = get_user_model()

        like_users = LikeDislike.objects.filter(user__in=users, tour=obj.tour, is_liked=True).values_list('user', flat=True)
        liked_users_list = User.objects.filter(id__in=like_users)
        usernames = liked_users_list.values_list('username', flat=True)
        return list(usernames)
    
    def get_dislike_members(self, obj):
        request = self.context.get('request')
        group_id = request.GET.get('group_id')
        group = Group.objects.get(id=group_id)
        users = group.get_members_with_leader() 
        User = get_user_model()

        dislike_users = LikeDislike.objects.filter(user__in=users, tour=obj.tour, is_disliked=True).values_list('user', flat=True)
        disliked_users_list = User.objects.filter(id__in=dislike_users)
        usernames = disliked_users_list.values_list('username', flat=True)
        return list(usernames)

class GroupLikeTourListSerializer(serializers.ModelSerializer):
    tour_list = serializers.SerializerMethodField()

    class Meta:
        model = GroupTourList
        fields = ['group', 'tour_list']

    def get_tour_list(self, obj):
        serializer = GroupLikeOrderSerializer(obj.grouptourorder_set.all(), many=True, context=self.context)
        return serializer.data