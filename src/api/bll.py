from django.db.models.query_utils import Q

def create_like_logic(like):
    """
    1. UPDATE USERS RECORD [liked_by and Liked_to]
    2. UPDATE LIKE RECORD
    3. CHECK FOR FRIEND_LIST AVAILIBILITY
    """
    liked_by = like.liked_by
    liked_to = like.liked_to



def delete_like_logic(like):
    """
    1. UPDATE USERS RECORD [liked_by and Liked_to]
    2. DELETE LIKE RECORD
    3. CHECK TO REMOVE FRIEND's LIST
    """
    pass
