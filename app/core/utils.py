from datetime import datetime


def formatar_data(data: datetime) -> str:
    return data.strftime('%d/%m/%Y %H:%M:%S')
