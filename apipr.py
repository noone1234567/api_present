from flask import Flask, request
import logging
import json

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

# создаём словарь, где для каждого пользователя мы будем хранить его имя
sessionStorage = {}


@app.route('/post', methods=['POST'])
def main():
    logging.info('Request: %r', request.json)
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }
    handle_dialog(response, request.json)
    logging.info('Response: %r', response)
    return json.dumps(response)


def handle_dialog(res, req):
    user_id = req['session']['user_id']

    # если пользователь новый, то просим его представиться.
    if req['session']['new']:
        res['response']['text'] = 'Привет! Назови свое имя!'
        # созда\м словарь в который в будущем положим имя пользователя
        sessionStorage[user_id] = {
            'first_name': None
        }
        return

    # если пользователь не новый, то попадаем сюда.
    # если поле имени пустое, то это говорит о том,
    # что пользователь ещё не представился.
    if sessionStorage[user_id]['first_name'] is None:
        # в последнем его сообщение ищем имя.
        first_name = get_first_name(req)
        # если не нашли, то сообщаем пользователю что не расслышали.
        if first_name is None:
            res['response']['text'] = \
                'Не расслышала имя. Повтори, пожалуйста!'
        # если нашли, то приветствуем пользователя.
        # И спрашиваем какой город он хочет увидеть.
        else:
            sessionStorage[user_id]['first_name'] = first_name
            res['response']['text'] = 'Приятно познакомиться, ' + first_name.title()\
                          + '. Я - Алиса. Какое число ты хочешь увидеть в разных системах счисления?'
    # если мы знакомы с пользователем и он нам что-то написал,
    # то это говорит о том, что он уже говорит о числе, что хочет увидеть.
    else:
        # ищем число в сообщение от пользователя
        try:
            num = str(get_num(req))
            ans = {'bin':'', 'eight':'', 'hex':''}
            ans['bin'] = convert_base(int(num), to_base=2)
            ans['eight'] = convert_base(int(num), to_base=8)
            ans['hex'] = convert_base(int(num), to_base=16)
            res['response']['text'] = ''.join(['В двоичной системе счисления: {}. '.format(str(ans['bin'])),
                                       'В восьмеричной системе счисления: {}. '.format(str(ans['eight'])),
                                       'В шестнадцатеричной системе счисления: {}.'.format(str(ans['hex']))])
        except Exception:
            res['response']['text'] = \
                'Первый раз слышу об этом числе. Попробуй еще разок!'


def get_num(req):
    # перебираем именованные сущности
    for entity in req['request']['nlu']['entities']:
        # если тип YANDEX.NUMBER то пытаемся получить число,
        # если нет то возвращаем None
        if entity['type'] == 'YANDEX.NUMBER':
            # возвращаем None, если не нашли сущности с типом YANDEX.NUMBER
            return int(entity['value'])
    return None


def get_first_name(req):
    # перебираем сущности
    for entity in req['request']['nlu']['entities']:
        # находим сущность с типом 'YANDEX.FIO'
        if entity['type'] == 'YANDEX.FIO':
            # Если есть сущность с ключом 'first_name',
            # то возвращаем ее значение.
            # Во всех остальных случаях возвращаем None.
            return entity['value'].get('first_name', None)


def convert_base(num, to_base=10, from_base=10):
    # first convert to decimal number
    if type(num) == "<class 'str'>":
        n = int(num, from_base)
    else:
        n = int(num)
    # now convert decimal to 'to_base' base
    alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    if n < to_base:
        return alphabet[n]
    else:
        return convert_base(n // to_base, to_base) + alphabet[n % to_base]


if __name__ == '__main__':
    app.run()
