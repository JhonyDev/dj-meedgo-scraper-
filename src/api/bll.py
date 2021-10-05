from django.db.models.query_utils import Q


def create_like_logic(like):
    """
    1. UPDATE USERS RECORD [liked_by and Liked_to]
    2. UPDATE LIKE RECORD
    3. CHECK FOR FRIEND_LIST AVAILIBILITY
    """
    pass
    # DATA FETCHING
    # liked_by = like.liked_by
    # liked_to = like.liked_to
    # like_type = like.like_type

    # IF NOT EXISTS ALREADY
    # likes = Like.objects.filter(liked_by=liked_by, liked_to=liked_to)
    # if not likes:

    # IF ALREADY FRIEND OR NOT
    # friend_list = FriendList.objects.filter(user=liked_by)
    # if not friend_list.filter(friend=liked_to):
    # pass


def delete_like_logic(like):
    """
    1. UPDATE USERS RECORD [liked_by and Liked_to]
    2. DELETE LIKE RECORD
    3. CHECK TO REMOVE FRIEND's LIST
    """
    pass
