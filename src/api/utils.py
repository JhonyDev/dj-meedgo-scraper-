def get_api_exception(detail, code):
    from rest_framework.exceptions import APIException
    api_exception = APIException()
    api_exception.status_code = code
    api_exception.detail = detail
    print(detail)
    return api_exception


def date_range(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        from datetime import timedelta
        yield start_date + timedelta(n)


def get_availability(date, end_date):
    from .models import Booking, Room
    parent_dict = None
    for single_date in date_range(date, end_date):
        bookings = Booking.objects.filter(check_in_date__gte=single_date, check_out_date__lt=single_date)
        booked_rooms = []
        for booking in bookings:
            for room in booking.rooms:
                booked_rooms.append(room.pk)
        rooms = Room.objects.all().exclude(pk__in=booked_rooms)
        booked_rooms_query = Room.objects.filter(pk__in=booked_rooms)
        cat_dict = {'Total': rooms.count()}
        print(f"PRED_DICS {parent_dict} ")
        for room in booked_rooms_query:
            print(f"DEDUCTING ROOMS {room.category} - {parent_dict[room.category]}")

            parent_dict[room.category] = parent_dict[room.category] - 1
            parent_dict['Total'] = parent_dict['Total'] - 1

        if parent_dict is None:
            for room in rooms:
                cat = cat_dict.get(room.category.name)
                if cat is None:
                    cat_dict[room.category.name] = 0
                cat = cat_dict.get(room.category.name)
                cat_dict[room.category.name] = cat + 1
            parent_dict = cat_dict

    return parent_dict


def get_target_dates(month, year):
    from dateutil import parser
    target_start_date = f'{year}-{month}-01'
    try:
        target_end_date = f'{year}-{month}-30'
    except:
        try:
            target_end_date = f'{year}-{month}-29'
        except:
            target_end_date = f'{year}-{month}-28'
    target_end_date = parser.parse(target_end_date)
    target_start_date = parser.parse(target_start_date)
    return target_start_date, target_end_date
