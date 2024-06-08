import json
from collections import OrderedDict

def ConvertJSON(mealObject: dict) -> dict:
    """
    !ISSUE!; 인코딩 상태에 문제 있을 수 있음, 한번에 하나씩만 처리함
    Parameters : JSON menuWithAllergy
    return : JSON menuWithAllergy
    """
    convertedMealObject = dict()

    if mealObject["MMEAL_SC_NM"] == "중식":
        convertedMealObject["isLunch"] = True
    else :
        convertedMealObject["isLunch"] = False
    
    convertedMealObject["date"] = mealObject["MLSV_YMD"]
    
    menus = mealObject["DDISH_NM"].split('<br/>')

    menuJSONList = list()

    for menu in menus:
        menu = menu.replace('*', '')
        menuWithAllergy = dict()
        menuWithAllergy["name"] = menu.split(' ', 1)[0].replace('1', '').replace('(완)', '')

        allergyList = list()

        if(menu.find('(')):
            menu = menu.replace('(', '')
            menu = menu.replace(')', '')
            menu = menu.split(' ')[1]
            allergyList = menu.split('.')

        i = 0

        for _ in allergyList:
            try:
                allergyList[i] = int(allergyList[i])
            except:
                allergyList = list()
            i += 1

        menuWithAllergy["allergies"] = allergyList
        menuJSONList.append(menuWithAllergy)
    
    convertedMealObject["menu"] = menuJSONList

    return convertedMealObject

def BatchConvertJSON(mealObject: list) -> list:
    """
    JSON List를 입력으로 받으면 전부 변환하여 바꿔줌
    Parameter : JSON List
    return JSON List
    """
    mealJSONList = list()

    for JSON in mealObject:
        mealJSONList.append(ConvertJSON(JSON))

    return mealJSONList
