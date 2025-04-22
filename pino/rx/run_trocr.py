from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from PIL import Image
from pprint import pprint

processor = TrOCRProcessor.from_pretrained("microsoft/trocr-base-handwritten")
model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-base-handwritten")

image_filenames = ["advil_pm.jpg", "allegra.jpg", "tylenol.jpg", "nivea.jpg"]

results = dict()
for image_filename in image_filenames + [f"{image_filename.split('.')[0]}_cropped.jpg" for image_filename in image_filenames]:
    image_path = f"/home/pino/experimental/pino/rx/data/images/iphone12/{image_filename}"
    image = Image.open(image_path)

    pixel_values = processor(image, return_tensors="pt").pixel_values
    generated_ids = model.generate(pixel_values)
    generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]

    results[image_filename] = generated_text



pprint(results)
