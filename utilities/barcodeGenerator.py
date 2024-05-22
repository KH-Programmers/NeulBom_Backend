from barcode import Code39
from barcode.writer import SVGWriter
import barcode


async def GenerateBarcode(stringInput):
    """
    Parameters : stringInput
    return : anImage - File-like SVG image Object
    Demonstration :
    입력으로 문자열 stringInput을 받아 Code39 포맷으로 SVG 이미지 반환
    """

    barcode.base.Barcode.default_writer_options["write_text"] = False
    barcode.base.Barcode.default_writer_options["background"] = "transparent"

    anImage = Code39(stringInput, add_checksum=False)
    anImage = anImage.render()
    return anImage
