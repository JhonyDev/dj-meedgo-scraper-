from django.db.models.query_utils import Q
from rest_framework import status
from rest_framework.generics import get_object_or_404

from src.accounts.models import User
from src.api import models as api_models


def create_like_logic(request):
    """
    1. CHECK  1: user can't like itself
    2. CHECK  2: like doesn't exists previously
    3. CHECK  3: reverse like

    4. CHANGE 4: update likes, likers and friends in User
    4. CHANGE 5: add friends_list
    4. CHANGE 6: add_likes
    """

    response_message = {'message': "Liked Successfully"}
    response_code = status.HTTP_201_CREATED

    liked_by = request.user
    like_type = request.data['like_type']
    liked_to = get_object_or_404(User.objects.all(), pk=request.data['liked_to'])
    likes = api_models.Like.objects.filter(liked_by=liked_by, liked_to=liked_to)
    reverse_likes = api_models.Like.objects.filter(liked_by=liked_to, liked_to=liked_by, like_type='l')
    friend_list = api_models.FriendList.objects.filter(
        Q(user=liked_by, friend=liked_to) |
        Q(user=liked_to, friend=liked_by)
    )

    if likes:
        delete_like = likes[0]

        if delete_like.like_type == 'l' and friend_list:
            friend_list.delete()
            liked_by.friends -= 1
            liked_to.friends -= 1

        liked_by.likes -= 1
        liked_to.likers -= 1
        liked_by.save()
        liked_to.save()
        delete_like.delete()

        response_message['message'] = "Successfully disliked"
        response_code = status.HTTP_204_NO_CONTENT
    else:
        api_models.Like.objects.create(
            liked_by=liked_by, liked_to=liked_to, like_type=like_type
        )

        if like_type == 'l' and reverse_likes:
            api_models.FriendList(user=liked_by, friend=liked_to).save()
            api_models.FriendList(user=liked_to, friend=liked_by).save()
            liked_by.friends += 1
            liked_to.friends += 1

        liked_by.likes += 1
        liked_to.likers += 1
        liked_by.save()
        liked_to.save()

    return response_message, response_code
