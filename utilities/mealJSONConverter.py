import json
from collections import OrderedDict

def ConvertJSON(aJSON):
    """
    !ISSUE!; 인코딩 상태에 문제 있을 수 있음, 한번에 하나씩만 처리함
    Parameters : JSON file
    return : JSON file
    """
    anOutputFile = OrderedDict()

    if aJSON["MMEAL_SC_NM"] == "중식":
        anOutputFile["isLunch"] = True
    else :
        anOutputFile["isLunch"] = False
    
    anOutputFile["date"] = aJSON["MLSV_YMD"]
    
    strings = aJSON["DDISH_NM"].split('<br/>')

    smallJSONList = list()

    for string in strings:
        string = string.replace('*', '')
        file = OrderedDict()
        file["name"] = string.split(' ', 1)[0]

        allergyList = list()

        if(string.find('(')):
            string = string.replace('(', '')
            string = string.replace(')', '')
            string = string.split(' ')[1]
            allergyList = string.split('.')

        i = 0

        for text in allergyList:
            try:
                allergyList[i] = int(allergyList[i])
            except:
                allergyList = list()
            i += 1

        file["allergies"] = allergyList
        smallJSONList.append(file)

    anOutputFile = OrderedDict()

    anOutputFile["isLunch"] = False
    anOutputFile["menu"] = smallJSONList

    return anOutputFile