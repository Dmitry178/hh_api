from hh_api import HHapi


if __name__ == '__main__':

    request = input('Введите запрос (по умолчанию "python"), 0 - для выхода: ')
    if request == '0':
        exit()

    area = input('Введите номер региона поиска в hh.ru (без номера - все регионы): ')
    try:
        if area == '':
            area = None
        else:
            area = int(area)
    except:
        print('Ошибка номера региона, поиск будет по всем регионам')
        area = None
    hh_api = HHapi(request, area)

    page = 0
    br = False
    while True:
        if not br:
            hh_api.print_vac_page(page)
        hh_api.print_resume(page)

        ent = input('Ввод: ')
        if ent == '':
            break

        num = -1
        try:
            num = int(ent)
            if num < 0:
                raise Exception()
        except:
            br = True
            continue

        if num > hh_api.pages:
            hh_api.print_vac(num)
            br = True
        else:
            page = num
            br = False
