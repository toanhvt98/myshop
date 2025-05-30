from datetime import timedelta
def string_to_timedelta(time_string):
    unit_type_string = time_string.split('|')[1]
    time = int(time_string.split('|')[0])
    kwargs = {unit_type_string:time}
    try:
        return timedelta(**kwargs)
    except TypeError as e:
        raise f'Error: {time_string} is not a valid time string for timedelta.'
    except Exception as e:
        raise f'An error occurred: {e}'
