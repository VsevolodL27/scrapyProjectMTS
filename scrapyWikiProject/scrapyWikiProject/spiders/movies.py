import re
import scrapy


def extract_year(text: list[str]) -> str:
    """
    Функция извлекает год премьеры фильма из списка строк
    :param text: Список дат для конкретного фильма
    :return: Год премьеры
    """
    if text is None or len(text) == 0:
        return 'Год неизвестен'
    years = []
    for t in text:
        years.extend(re.findall(r'\d{4}', t))
    return min(years) if years else 'Год неизвестен'


def clean_text(arr: list[str]) -> str:
    """
    Функция извлекает текст из переданного ей списка строк
    :param arr: Список строк в "сыром" виде
    :return: "Очищенную" строку
    """
    return ', '.join([word for word in arr if re.match(r'\b\w+\b', word)])


def parse_imdb_rating(response):
    imdb_rating = response.css('div[data-testid="hero-rating-bar__aggregate-rating__score"] span::text').get()

    if not imdb_rating:
        imdb_rating = "Рейтинг для данного фильма не найден"

    yield {
        'Название': response.meta['title'],
        'Жанр': response.meta['genre'],
        'Режиссер': response.meta['director'],
        'Страны': response.meta['countries'],
        'Год': response.meta['year'],
        'Рейтинг IMDb': imdb_rating
    }


def parse_movie(response) -> dict:
    """
    Функция парсит страницу фильма
    :param response: Текст из указанных селексторов
    :return: Словарь с названием, жанром, именем рижессеров, страны, снимавшие фильм и год
    """
    title = response.css('table.infobox tbody tr th.infobox-above::text').get().strip()
    genre = clean_text(response.css('table.infobox tbody tr th:contains("Жанр") + td ::text').getall())
    director = clean_text(response.css('table.infobox tbody tr th:contains("Реж") + td ::text').getall())
    countries = clean_text(response.css('table.infobox tbody tr th:contains("Стран") + td ::text').getall())
    year = extract_year(response.css('table.infobox tbody tr th:contains("Год") + td ::text').getall())
    imdb_link = response.xpath("//th[contains(a, 'IMDb')]/following-sibling::td//a/@href").get()

    if imdb_link:
        yield scrapy.Request(url=imdb_link, callback=parse_imdb_rating,
                             meta={'title': title,
                                   'genre': genre,
                                   'director': director,
                                   'countries': countries,
                                   'year': year
                                   }
                             )
    else:
        yield {
            'Название': title,
            'Жанр': genre,
            'Режиссер': director,
            'Страны': countries,
            'Год': year,
            'Рейтинг IMDb': "Рейтинг для данного фильма не найден"
        }


class MoviesSpider(scrapy.Spider):
    name = "movies"
    start_urls = ['https://ru.wikipedia.org/wiki/Категория:Фильмы_по_алфавиту']

    def parse(self, response, **kwargs):
        for selector in response.css('div.mw-category-group a::attr(href)'):
            yield response.follow(selector, callback=parse_movie)

        next_page = response.css('a:contains("Следующая страница")::attr(href)').get()

        if next_page:
            next_page = response.urljoin(next_page)
            yield response.follow(next_page, callback=self.parse)
