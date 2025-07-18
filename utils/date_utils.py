# from datetime import datetime, timedelta

# class DateUtils:
#     def format_date(self, date_str, format_type):
#         date = datetime.strptime(date_str, '%Y-%m-%d')
#         if format_type == 'ddmmyyyy':
#             return date.strftime('%d%m%Y')
#         elif format_type == 'ddmmyy':
#             return date.strftime('%d%m%y')
#         return date_str

#     def get_date_range(self, start_date, end_date):
#         start = datetime.strptime(start_date, '%Y-%m-%d')
#         end = datetime.strptime(end_date, '%Y-%m-%d')
#         date_list = []
#         current_date = start
#         while current_date <= end:
#             date_list.append(current_date.strftime('%Y-%m-%d'))
#             current_date += timedelta(days=1)
#         return date_list

from datetime import datetime, timedelta

class DateUtils:
    def format_date(self, date_str, format_type):
        date = datetime.strptime(date_str, '%Y-%m-%d')
        if format_type == 'ddmmyyyy':
            return date.strftime('%d%m%Y')
        elif format_type == 'ddmmyy':
            return date.strftime('%d%m%y')
        return date_str

    def get_date_range(self, start_date, end_date):
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        date_list = []
        current_date = start
        while current_date <= end:
            date_list.append(current_date.strftime('%Y-%m-%d'))
            current_date += timedelta(days=1)
        return date_list