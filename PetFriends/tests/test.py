"""
pip install requests-toolbelt
pip install Faker
pip install random
pycharm > set UTF-8 in Settings | Editor | General | Console | Default Encoding
"""
# -*- coding: utf-8 -*-
import os
import pytest
import time
import random
from api import PetFriends
from settings import valid_email, valid_password
from faker import Faker
import requests
import json
from requests_toolbelt import MultipartEncoder

pf = PetFriends()
fake = Faker()
# photo_random = ('images/' + random.choice(os.listdir('images/'))


""" Проверяем, что запрос API ключа возвращает статус 200 и в результате содержится слово key"""
def test_get_api_key_for_valid_user(email=valid_email, password=valid_password):
    status, result = pf.get_api_key(email, password)
    assert status == 200
    assert 'key' in result
    print(result)


'''Проверяем получение ключа с не корректным email'''
def test_get_api_key_with_invalid_email(email='123456', password=valid_password):

    status, result = pf.get_api_key(email, password)
    assert status == 403 #доступ пользователя с неизвестным email запрещен, значит тест пройден
    assert 'key' not in result


'''Проверяем получение ключа с не корректным паролем'''
def test_get_api_key_with_invalid_password(email=valid_email, password='hgfdukj'):

    status, result = pf.get_api_key(email, password)
    assert status == 403 #доступ пользователя с неизвестным password запрещен, значит тест пройден
    assert 'key' not in result


'''Проверяем получение ключа с незаполненными (пустыми) полями email и password'''
def test_get_api_key_with_empty_fields_email_and_password(email='', password=''):

    status, result = pf.get_api_key(email, password)
    assert status == 403 #доступ пользователя с неизвестным password запрещен, значит тест пройден
    assert 'key' not in result


""" Проверяем, запрос всех моих питомцев c неправильным ключом."""
# def test_invalid_key(filter='my_pets'):
#     headers = {'auth_key': 'ghfgdhfjghkjkhj'}
#     res = requests.get('https://petfriends.skillfactory.ru/api/pets', headers=headers, params=filter)
#     status = res.status_code
#     assert status == 403, 'Запрос выполнен неуспешно'
#
#
# """ Проверяем, запрос всех моих питомцев c неправильным ключом2."""
# def test_invalid_key_2(filter='my_pets'):
#     headers = {'auth_key': 'наплдютигпгп'}
#     res = requests.get('https://petfriends.skillfactory.ru/api/pets', headers=headers, params=filter)
#     status = res.status_code
#     assert status == 403, 'Запрос выполнен неуспешно'


""" Проверяем, что запрос всех питомцев возвращает не пустой список."""
def test_get_all_pets_with_valid_key():
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.get_list_of_pets(auth_key, "")
    assert status == 200
    assert len(result['pets']) > 0


""" Проверяем, что запрос всех моих питомцев возвращает не пустой список."""
def test_get_all_my_pets_with_valid_key(filter='my_pets'):
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.get_list_of_pets(auth_key, filter)
    assert status == 200
    assert len(result['pets']) > 0
    print(result)


""" Проверяем, что не верный запрос всех питомцев возвращает ошибку."""
def test_get_all_pets_with_valid_key():
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.get_list_of_pets(auth_key, "2n4a8e")
    assert status == 500


"""Проверяем что можно добавить питомца с корректными данными и фото """
def test_add_new_pet_with_photo_valid_data(name=fake.first_name(), animal_type='Чупакабра',
                                     age=str(random.randint(1, 10)), pet_photo = 'images/DKpmtaHU8AE-fbJ.jpg'):
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)
    assert status == 200
    assert result['name'] == name



"""Проверяем возможность обновления информации о питомце"""
def test_successful_update_self_pet_info(name=fake.first_name(), animal_type='Попкугал', age=7):
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Если список не пустой, то пробуем обновить его имя, тип и возраст
    if len(my_pets['pets']) == 0:
        pf.add_new_pet(auth_key, fake.first_name(), "Дельфинчег", "7", 'images/CcLVTiTW4AA7fkp.jpg')
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)

    assert status == 200 # Проверяем что статус ответа = 200 и имя питомца соответствует заданному
    assert result['name'] == name


"""Проверяем возможность удаления питомца"""
def test_successful_delete_self_pet():
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    if len(my_pets['pets']) == 0:
        pf.add_new_pet(auth_key, fake.first_name(), "Дельфинчег", "7", 'images/CcLVTiTW4AA7fkp.jpg')
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    pet_id = my_pets['pets'][0]['id']
    status, _ = pf.delete_pet(auth_key, pet_id)

    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    assert status == 200
    assert pet_id not in my_pets.values()


"""Проверяем, что можно успешно добавить питомца без фото"""
def test_successful_create_pet_simple(name=fake.first_name(), animal_type='Очковая Змея',
                                     age=str(random.randint(1, 10))):
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.create_pet_simple(auth_key, name, animal_type, age)

    assert status == 200
    assert result['name'] == name


"""Проверяем, что можно обновить фото питомца"""
def test_successful_add_photo_of_my_pet(pet_photo="images/CaHXM3nWwAAikwc.jpg"):
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    pet_id = my_pets['pets'][0]['id']

    if len(my_pets['pets']) == 0:
        pf.add_new_pet(auth_key, fake.first_name(), "стасик", "2", "bfbf0de89082c0f9760dbbb21718bb58.jpg")
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    status, result = pf.add_photo_of_pet(auth_key, pet_id, pet_photo)
    assert status == 200
    assert result['pet_photo'] is not None


"""Проверяем можно ли добавить питомца с фото в другом формате"""
def test_add_new_pet_with_invalid_photo(name=fake.first_name(), animal_type='Сява',
                                     age=str(random.randint(1, 10)), pet_photo='images/DKpmtaHU8AE-fbJ.bmp'):
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
    assert status == 500  # статус кода 200, тест провален, заводим баг,
    # сервер дает загрузить картинку питомца в формате, не соответствующей документации


"""Проверяем можно ли добавить в поле "имя" символьные значения"""
def test_add_new_pet_with_invalid_1_animal_type(name='|\/!@#$%^&*()-_=+`~?"№;:[]{}', animal_type='Лох Типичный',
                                     age=str(random.randint(1, 20)), pet_photo='images/CcLUBXbWEAA_2Ly.jpg'):
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    assert status == 500 # статус кода 200, тест провален, заводим баг,сервер дает ввести не корректные данные


"""Проверяем можно ли добавить в поле "Вид животного" 257 буквенно-символьных значений"""
def test_add_new_pet_with_invalid_2_animal_type(name=fake.first_name(), animal_type='s82tepFRFbuxXmsCssp8L7ngmQC5Ni04hOk'
                                                                                  'xEIXh1tjxbdoqpHWkJTf2wdG0Uu0D0yAUOA8'
                                                                                  '54QFf2dd3c6LkJWbFhbD3r57X969XpRj96oC'
                                                                                  'TvUay2wGMC8XOfXrcmLkuyEwqZCZwUUMTMDx'
                                                                                  '8KNCbUpqvvhIgYSEwP8BNVMazHeCrjmNzS89'
                                                                                  'n8LHwD2RQSuJfN4htaceyozaB0J8ran1UHff'
                                                                                  'kq6tw2FPuz509nnR9aqn0fF6fZmsRQwsH7yU'
                                                                                  '2CMlB9',
                                     age=str(random.randint(1, 20)), pet_photo='images/C7oso59XwAASO3_.jpg'):
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    assert status == 500 # статус кода 200, тест провален, заводим баг,сервер дает ввести не корректные данные


"""Проверяем можно ли добавить в поле "Возраст" значения более 500"""
def test_add_new_pet_with_invalid_over_age(name=fake.first_name(), animal_type='Суслоберг',
                                     age=str(500), pet_photo='images/425346_original.jpg'):
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    assert status == 500 # статус кода 200, тест провален, заводим баг,сервер дает ввести отрицательный возраст


"""Проверяем можно ли добавить в поле "Возраст" отрицательные значения"""
def test_add_new_pet_with_invalid_minus_age(name=fake.first_name(), animal_type='Жырафег',
                                     age=str(-13), pet_photo='images/CPH7D_AXAAABOzk.jpg'):
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    assert status == 500 # статус кода 200, тест провален, заводим баг,сервер дает ввести отрицательный возраст


"""Проверяем можно ли добавить в поле "Возраст" буквенные значения"""
def test_add_new_pet_with_invalid_bukv_age(name=fake.first_name(), animal_type='Волосатик',
                                     age=str('的是不了人我在有他这为之大来以个中上们'), pet_photo='images/CGdSjRhVIAAlMKh.jpg'):

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    assert status == 500 # статус кода 200, тест провален, заводим баг,сервер дает ввести отрицательный возраст


"""Проверяем можно ли добавить питомца без заполнения полей информации о питомце"""
def test_create_pet_simple_with_empty_data(name='', animal_type='', age=''):
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.create_pet_simple(auth_key, name, animal_type, age)

    assert status == 500 # статус кода 200, тест провален, заводим баг,сервер дает создать питомца без данных


"""Проверяем, что нельзя обновить инфо о чужом питомце"""
def test_impossible_update_other_user_pet_info(name=fake.first_name(), animal_type='Лампогрыз',
                                               age=random.randint(1, 20)):
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, all_pets = pf.get_list_of_pets(auth_key, "")
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    if len(all_pets['pets']) > 0 and all_pets['pets'][15]['id'] != my_pets['pets'][0]['id']:
        status, result = pf.update_pet_info(auth_key, all_pets['pets'][15]['id'], name, animal_type, age)
        assert status == 500  # статус кода 200, тест провален, заводим баг, сервер дает обновить информацию по чужим питомцам
        assert result['name'] == name
    else:
        raise Exception("There are no pets")


"""Проверяем, что нельзя добавить фото чужому питомцу"""
def test_impossible_add_photo_of_other_user_pet(pet_photo="images/CG6J3EhWoAANJ17.jpg"):
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, all_pets = pf.get_list_of_pets(auth_key, "")
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
    pet_id_my_pets = my_pets['pets'][0]['id']
    pet_id = all_pets['pets'][0]['id']

    status, result = pf.add_photo_of_pet(auth_key, pet_id, pet_photo)
    if pet_id == pet_id_my_pets:
        assert status == 200  # если фото добавилось к питомцу из моего списка, ошибки нет
    else:
        assert status == 500  # если сервер не может обработать запрос, значит тест пройден
    print(status)


"""Проверяем, что нельзя удалить чужого питомца"""
def test_impossible_delete_other_user_pet():
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, all_pets = pf.get_list_of_pets(auth_key, "")
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
    pet_id = all_pets['pets'][0]['id']

    if all_pets['pets'][0]['id'] != my_pets['pets'][0]['id']:
        status, _ = pf.delete_pet(auth_key, pet_id)
        assert status == 500  # статус кода 200, тест провален, заводим баг, сервер дает удалить чужого питомца
    else:
        print('There is pet from my list')


# """Проверяем возможность удаления всех своих питомцев"""
# def test_successful_delete_all_user_pet():
#     _, auth_key = pf.get_api_key(valid_email, valid_password)
#     _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
#     if len(my_pets['pets']) == 0:
#         return
#     for pet in my_pets['pets']:
#         pet_id = pet['id']
#         status, _ = pf.delete_pet(auth_key, pet_id)
#         assert status == 200
#     _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
#     assert len(my_pets['pets']) == 0


# """Проверяем, что нельзя удалить всех питомцев со страницы"""
# def test_impossible_delete_all_pet():
#     _, auth_key = pf.get_api_key(valid_email, valid_password)
#     _, all_pets = pf.get_list_of_pets(auth_key, "")
#
#     if len(all_pets['pets']) == 0:
#         return
#     for pet in all_pets['pets']:
#         status, _ = pf.delete_pet(auth_key, pet['id'])
#         time.sleep(2)
#     _, all_pets = pf.get_list_of_pets(auth_key, "")
#     assert status == 500 # статус кода 200, тест провален, заводим баг, сервер дает удалить чужих питомцев
#     assert len(all_pets['pets']) == 0