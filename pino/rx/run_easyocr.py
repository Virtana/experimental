from easyocr import Reader
from pprint import pprint

reader = Reader(["en"])
image_filenames = ["advil_pm.jpg", "allegra.jpg", "tylenol.jpg", "nivea.jpg"]


results = dict()
for image_filename in image_filenames + [
    f"{image_filename.split('.')[0]}_cropped.jpg" for image_filename in image_filenames
]:
    image_path = (
        f"/home/pino/experimental/pino/rx/data/images/iphone12/{image_filename}"
    )

    results[image_filename] = reader.readtext(image_path, detail=0)

pprint(results)
