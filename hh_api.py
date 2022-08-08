import requests
import json
import pickle
from pprint import pprint


class HHapi:

    def __init__(self, request='', area=2):
        self.DOMAIN = 'https://api.hh.ru/'
        self._area = area
        self._url_vac = f'{self.DOMAIN}vacancies'
        self._request = 'python' if not request else request
        self.found, self.pages, self.per_page = self._get_num_pages()

    def _get_params(self, page, area):
        if not area:
            return {
                'text': self._request,
                'page': page
            }
        return {
            'text': self._request,
            'area': area,
            'page': page
        }

    def _get_num_pages(self):
        """
        возвращает количество страниц в запросе
        :return:
        """
        result = requests.get(self._url_vac, params=self._get_params(0, self._area))

        if result.status_code != 200:
            return None

        return result.json()['found'], result.json()['pages'], result.json()['per_page']

    @staticmethod
    def _replace_highlight_text(s):
        return str(s).replace('<highlighttext>', '').replace('</highlighttext>', '')

    def print_vac_page(self, page):
        """
        вывод страницы с краткой информацией о вакансиях
        :param page: номер страницы
        :return:
        """
        response = requests.get(self._url_vac, params=self._get_params(page, self._area)).json()['items']
        for item in response:
            print('-' * 50)
            print(f"ID: {item['id']}")
            print(f"Работодатель: {item['employer']['name']}")
            print(f"Позиция: {item['name']}")
            if item['has_test']:
                print('Тестирование: есть')
            if item['response_letter_required']:
                print('Сопроводительное письмо: требуется')
            print('Ссылка на вакансию:', item['alternate_url'])
            # print('Ссылка API:', item['url'])
            print('Требования:', self._replace_highlight_text(item['snippet']['requirement']))
            print('Обязанности:', self._replace_highlight_text(item['snippet']['responsibility']))
            if item['salary']:
                print('Зарплата:' + ((' от ' + str(item['salary']['from'])) if item['salary']['from'] else '')\
                      + ((' до ' + str(item['salary']['to'])) if item['salary']['to'] else '')\
                      + ((' ' + str(item['salary']['currency'])) if item['salary']['currency'] else ''))
            if item['address']:
                print(f"Адрес: {item['address']['raw']}")

        print('=' * 50)

    def print_resume(self, page):
        print(f'Найдено {self.found} вакансий. Страница {page} из {self.pages}.')
        print('Введите номер страницы или ID вакансии для детального просмотра.')
        print('При выборе ID, вакансия будет сохранена в файл. Пустой ввод - выход.')

    @staticmethod
    def html_to_text(html=''):
        html = html.replace('<p>', '').replace('<strong>', '').replace('</strong>', '').replace('</p>', '\n')\
            .replace('<ul>', '').replace('</ul>', '').replace('</li>', '\n').replace('<li>', '- ')\
            .replace('<em>', '● ').replace('</em>', '').replace('<br />', '\n').replace('<br/>', '\n')\
            .replace('<br>', '\n').replace('​', '\n')

        return html

    def print_vac(self, id_vac):
        """
        вывод полной информации о вакансии
        :param id_vac: id вакансии
        :return:
        """
        url_vac_id = f'https://api.hh.ru/vacancies/{id_vac}?host=hh.ru'
        response = requests.get(url_vac_id).json()
        print('-' * 50)

        if 'errors' in response:
            print('Ошибка номера вакансии')
        else:
            print()
            vac = []
            try:
                # pprint(response)
                vac.append(f"Работодатель: {response['employer']['name']}")
                if response['address']:
                    vac.append(f"Адрес: {response['address']['raw']}")
                vac.append(f"Позиция: {response['name']}")
                vac.append(f"Ссылка на вакансию: {response['alternate_url']}")
                vac.append('')
                if response['description']:
                    vac.append('Описание:')
                    vac.append(self.html_to_text(response['description']))
                    vac.append('')
                if response['salary']:
                    vac.append(
                        'Зарплата:' + ((' от ' + str(response['salary']['from'])) if response['salary']['from'] else '') \
                        + ((' до ' + str(response['salary']['to'])) if response['salary']['to'] else '') \
                        + ((' ' + str(response['salary']['currency'])) if response['salary']['currency'] else ''))
                if 'employment' in response:
                    if response['employment']:
                        vac.append(f"Занятость: {response['employment']['name']}")
                if 'schedule' in response:
                    if response['schedule']:
                        vac.append(f"График: {response['schedule']['name']}")
                if 'experience' in response:
                    if response['experience']:
                        vac.append(f"Опыт работы: {response['experience']['name']}")
                if 'key_skills' in response:
                    if response['key_skills']:
                        vac.append('Ключевые навыки:')
                        for i in response['key_skills']:
                            vac.append(f"- {i['name']}")
                if 'professional_roles' in response:
                    if response['professional_roles']:
                        vac.append('Профессиональные роли:')
                        for i in response['professional_roles']:
                            vac.append(f"- {i['name']}")
                if 'specializations' in response:
                    if response['specializations']:
                        vac.append('Специализации:')
                        for i in response['specializations']:
                            vac.append(f"- {i['name']}")
                if 'languages' in response:
                    if response['languages']:
                        vac.append('Знание языков:')
                        for i in response['languages']:
                            print(f"- {i['name']}, уровень {i['level']['name']}")

                for i in vac:
                    print(i)

            except:
                # вывод в сыром виде, если была ошибка в обработке
                pprint(response)

            self._save_text(id_vac, vac)
            self._save_data(id_vac, response)

        print('=' * 50)

    @staticmethod
    def _save_text(id_vac, text):
        # сохранение файла в текстовом формате
        try:
            with open(f'{id_vac}.txt', 'w') as f:
                for i in text:
                    s = '' if not len(i) else i + '\n' if i[-1] != '\n' else ''
                    f.write(s)
        except:
            pass

    @staticmethod
    def _save_data(id_vac, data):
        # сохранение в формате pickle
        try:
            with open(f'{id_vac}.pkl', 'wb') as f:
                pickle.dump(data, f)
        except:
            pass

        # сохранение в формате json
        try:
            with open(f'{id_vac}.json', 'w', encoding='utf8') as f:
                f.write(json.dumps(data, ensure_ascii=False))
        except:
            pass
