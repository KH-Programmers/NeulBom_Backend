import re
from typing import List


class Menu:
    def __init__(self, data: str):
        self._name = "".join(
            list(
                filter(
                    lambda x: x.isalpha() or x == " ",
                    re.sub(r"\([^)]*\)", "", data).strip(),
                )
            )
        )
        self._allergy = list(
            map(
                int,
                filter(
                    lambda x: x != "" and x.isdigit(),
                    str(
                        ""
                        if len(re.findall(r"\([^)]*\)", data)) == 0
                        else re.findall(r"\([^)]*\)", data)[0]
                    )
                    .replace("(", "")
                    .replace(")", "")
                    .split("."),
                ),
            )
        )

    @property
    def name(self) -> str:
        return self._name

    @property
    def allergy(self) -> List[int]:
        return self._allergy


class Meal:
    def __init__(self, mealData: list):
        self.mealData = mealData
        self.menu = [[], []]
        for meal in mealData:
            for menu in meal.split("<br/>"):
                if menu != "":
                    self.menu[mealData.index(meal)].append(
                        Menu(
                            data=menu,
                        )
                    )

    def ToDict(self) -> list:
        data = []
        for meal in self.menu:
            for menu in meal:
                data.append(
                    {
                        "name": menu.name,
                        "allergy": menu.allergy,
                    }
                )
        return data
