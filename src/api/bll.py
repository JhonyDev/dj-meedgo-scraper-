from datetime import date

from django.db.models.query_utils import Q
from rest_framework import status
from rest_framework.generics import get_object_or_404

from src.accounts.models import User
from src.api import models as api_models
from dateutil.relativedelta import relativedelta


def create_like_logic(request):
    """
    1. CHECK  1: user can't like itself
    2. CHECK  2: like doesn't exists previously
    3. CHECK  3: reverse like

    4. CHANGE 4: update likes, likers and friends in User
    5. CHANGE 5: add friends_list
    6. CHANGE 6: add_likes
    7. CHANGE 7: check if user posted favorite, if yes follow next steps
    8. CHANGE 8: check if user already posted favorite
    9. CHANGE 9: if posted already remove favorite
    10. CHANGE 10: else insert favorite

    """

    response_message = {'message': "like Successful"}
    response_code = status.HTTP_201_CREATED

    liked_by = request.user
    like_type = request.data['like_type']
    liked_to = get_object_or_404(User.objects.all(), pk=request.data['liked_to'])
    likes = api_models.Like.objects.filter(liked_by=liked_by, liked_to=liked_to, like_type='l')

    reverse_likes = api_models.Like.objects.filter(liked_by=liked_to, liked_to=liked_by, like_type='l')
    friend_list = api_models.FriendList.objects.filter(
        Q(user=liked_by, friend=liked_to) |
        Q(user=liked_to, friend=liked_by)
    )

    if liked_by == liked_to:
        response_message['message'] = "You can't like yourself"
        response_code = status.HTTP_400_BAD_REQUEST
    else:
        if likes:
            '''
            IF ALREADY LIKED AND LIKED AGAIN
            '''
            delete_like = likes[0]

            if delete_like.like_type == 'l' and friend_list:
                friend_list.delete()
                liked_by.friends -= 1
                liked_to.friends -= 1

            if like_type == 'l':
                response_message['message'] = "like deleted"
                liked_by.likes -= 1
                liked_to.likers -= 1
                liked_by.save()
                liked_to.save()
                delete_like.delete()
                response_code = status.HTTP_204_NO_CONTENT
            else:
                '''
                IF ALREADY LIKED AND REQUESTED FAVORITE
                '''
                response_message['message'] = "favorite not allowed"
                response_code = status.HTTP_400_BAD_REQUEST
        else:
            faves = api_models.Like.objects.filter(liked_by=liked_by, liked_to=liked_to, like_type='f')
            if faves:
                if like_type == 'f':
                    '''
                    IF ALREADY FAVORITE AND REQUESTED FAVORITE AGAIN
                    '''
                    delete_like = faves[0]
                    delete_like.delete()
                    response_message = {'message': "favorite deleted"}
                    response_code = status.HTTP_204_NO_CONTENT
                else:
                    '''
                    IF ALREADY FAVORITE AND LIKED REQUESTED LIKE 
                    '''
                    response_message = {'message': "like not allowed"}
                    response_code = status.HTTP_400_BAD_REQUEST
            else:
                api_models.Like.objects.create(
                    liked_by=liked_by, liked_to=liked_to, like_type=like_type
                )

                if like_type == 'f':
                    response_message = {'message': "favorite Successful"}
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


def subscription_logic(request):
    """
    CHECK 1: Already Exists
    CHECK 2: expiry date
    """
    response_message = {'message': 'subscribed successfully'}
    response_code = status.HTTP_201_CREATED

    user = request.user
    if not user.is_paid:
        user.is_paid = True
        user.expiry_date = date.today() + relativedelta(months=+6)
    else:
        if user.expiry_date < date.today():
            user.is_paid = True
            user.expiry_date = date.today() + relativedelta(months=6)
            user.save()

    response_message['message'] = 'Failed to subscribed - already exists'
    response_code = status.HTTP_409_CONFLICT
    return response_message, response_code


def is_premium_member(user):
    if user.is_paid:
        if user.expiry_date >= date.today():
            return True
        else:
            user.is_paid = False
            user.expiry_date = None
            user.save()
    return False
