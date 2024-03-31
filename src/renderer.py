"""
Функции для формирования выходной информации.
"""
from datetime import datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal

from tabulate import tabulate

from collectors.models import LocationInfoDTO


class Renderer:
    """
    Генерация результата преобразования прочитанных данных.
    """

    def __init__(self, location_info: LocationInfoDTO) -> None:
        """
        Конструктор.

        :param location_info: Данные о географическом месте.
        """

        self.location_info = location_info

    async def render(self) -> tuple[str, ...]:
        """
        Форматирование прочитанных данных.

        :return: Результат форматирования
        """

        location = [
            ["Страна", self.location_info.location.name],
            ["Столица", self.location_info.location.capital],
            ["Регион", self.location_info.location.subregion],
            ["Языки", await self._format_languages()],
            ["Население страны", f"{await self._format_population()} чел."],
            ["Площадь страны", f"{self.location_info.location.area} кв.км"],
            ["Часовой пояс", await self._format_timezone()],
            ["Текущее время", await self._format_current_time()],
            ["Курсы валют", await self._format_currency_rates()],
        ]

        capital = [
            ["Столица", self.location_info.location.capital],
            ["Широта", self.location_info.location.latitude],
            ["Долгота", self.location_info.location.longitude]
        ]

        weather = [
            ["Погода", self.location_info.weather.description],
            ["Температура", f"{self.location_info.weather.temp} °C"],
            ["Видимость", f"{self.location_info.weather.visibility} м"],
            ["Скорость ветра", f"{self.location_info.weather.wind_speed} м/с"]
        ]

        location_table = tabulate(location, tablefmt="simple_grid")
        capital_table = tabulate(capital, tablefmt="simple_grid")
        weather_table = tabulate(weather, tablefmt="simple_grid")

        return (
            "Информация о стране",
            location_table,
            "Информация о столице",
            capital_table,
            "Информация о погоде",
            weather_table
        )

        # return (
        #     f"Страна: {self.location_info.location.name}",
        #     f"Столица: {self.location_info.location.capital}",
        #     f"Регион: {self.location_info.location.subregion}",
        #     f"Языки: {await self._format_languages()}",
        #     f"Население страны: {await self._format_population()} чел.",
        #     f"Площадь страны: {self.location_info.location.area} кв.км",
        #     f"Широта: {self.location_info.location.latitude}",
        #     f"Долгота: {self.location_info.location.longitude}",
        #     f"Часовой пояс: {await self._format_timezone()}",
        #     f"Текущее время: {await self._format_current_time()}",
        #     f"Курсы валют: {await self._format_currency_rates()}",
        #     f"Погода: {self.location_info.weather.description}",
        #     f"Температура: {self.location_info.weather.temp} °C",
        #     f"Видимость: {self.location_info.weather.visibility} м",
        #     f"Скорость ветра: {self.location_info.weather.wind_speed} м/с",
        # )

    async def _format_languages(self) -> str:
        """
        Форматирование информации о языках.

        :return:
        """

        return ", ".join(
            f"{item.name} ({item.native_name})"
            for item in self.location_info.location.languages
        )

    async def _format_population(self) -> str:
        """
        Форматирование информации о населении.

        :return:
        """

        # pylint: disable=C0209
        return "{:,}".format(self.location_info.location.population).replace(",", ".")

    async def _format_currency_rates(self) -> str:
        """
        Форматирование информации о курсах валют.

        :return:
        """

        return ", ".join(
            f"{currency} = {Decimal(rates).quantize(exp=Decimal('.01'), rounding=ROUND_HALF_UP)} руб."
            for currency, rates in self.location_info.currency_rates.items()
        )

    async def _format_timezone(self) -> str:
        """
        Форматирование информации о часовом поясе.

        :return:
        """

        return f"UTC+0{self.location_info.weather.timezone // (60 * 60)}:00"

    async def _format_current_time(self) -> str:
        """
        Форматирование информации о текущем времени в столице.

        :return:
        """

        dt = datetime.utcnow() + timedelta(seconds=self.location_info.weather.timezone)
        time = dt.strftime("%H:%M")
        return time