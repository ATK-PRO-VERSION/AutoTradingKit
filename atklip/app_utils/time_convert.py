from datetime import datetime
import pytz

class TimeConverter:
    @staticmethod
    def convert_string_to_utc_timestamp(time_str):
        datetime_object = datetime.strptime(time_str, "%d/%m/%Y %H:%M")
        utc_obj = pytz.timezone('UTC').localize(datetime_object)
        return utc_obj.timestamp()
