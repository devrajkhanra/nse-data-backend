from datetime import datetime, timedelta

class DateUtils:
    def format_date(self, date_str, format_type):
        date = datetime.strptime(date_str, '%Y-%m-%d')
        return date.strftime('%d%m%Y') if format_type == 'ddmmyyyy' else (
            date.strftime('%d%m%y') if format_type == 'ddmmyy' else date_str
        )

    def get_date_range(self, start_date, end_date):
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        return [(start + timedelta(days=i)).strftime('%Y-%m-%d') for i in range((end - start).days + 1)]