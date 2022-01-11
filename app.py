from PIL import Image, ImageDraw
from flask import Flask, request, render_template, Response
import os
import io
from io import StringIO, BytesIO
import base64


app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 32 * 1000 * 1000
app.config["IMAGE_UPLOADS"] = os.path.dirname(__file__)


@app.route('/', methods=['GET', 'POST'])
def upload_image():
    if request.method == "POST":
        if request.files:
            image = request.files["image"]
            colors = request.values["colors"]
            width_emb = request.values["width_img"]
            height_emb = request.values["height_img"]
            result1, result2 = main(image, int(colors), int(width_emb), int(height_emb))
            upl1 = base64.b64encode(b''.join(serve_pil_image(result1).response)).decode('utf-8')
            upl2 = base64.b64encode(b''.join(serve_pil_image(result2).response)).decode('utf-8')
            palette_img = Image.new('RGB', (80 * int(colors), 300), (255, 255, 255))
            draw_pal = ImageDraw.Draw(palette_img)
            index = '0'
            color = (0, 0, 0)
            f = open('palette')
            lines = f.readlines()
            for i in range(2, int(colors) + 2):
                lines[i] = lines[i].split()
                index = lines[i][0]
                color = tuple([int(lines[i][1]), int(lines[i][2]), int(lines[i][3])])
                draw_pal.rectangle([(i * 16 * 4, 40), (i * 16 * 4 + 80, 180)], fill = color, outline = None)
                draw_pal.text((i * 16 * 4 + 15, 250), index, fill = (0, 0, 0))
            pal = base64.b64encode(b''.join(serve_pil_image(palette_img).response)).decode('utf-8')
            return render_template("index.html", uploaded_image1=upl1, uploaded_image2=upl2, uploaded_pal = pal)
    return render_template("index.html")

def changeSize(image, width, height, new_size_X, new_size_Y):
	width *= new_size_X
	width = int(width)
	height *= new_size_Y
	height = int(height)
	resized_image = image.resize((width, height))
	return (resized_image, width, height)

def Drawer(result, result_clear, width, height, i_pixels):
    draw_img = ImageDraw.Draw(result)
    draw_clear = ImageDraw.Draw(result_clear)
    for i in range(width):
        for j in range(height):
            draw_img.text((i * 16, j * 16), str(i_pixels[i, j]),  fill = (0, 0, 0))
            draw_clear.text((i * 16, j * 16), str(i_pixels[i, j]),  fill = (0, 0, 0))
    return result, result_clear

def main(image, quan, sizex, sizey):
    rawIO = io.BytesIO(image.read())
    rawIO.seek(0)
    image = Image.open(rawIO)
    width = image.size[0]
    height = image.size[1]
    resized_image, new_width, new_height = changeSize(image, width, height, sizex/width, sizey/height)
    quantized = resized_image.quantize(quan)
    i_pixels = quantized.load()
    for_result_w = new_width * 16
    for_result_h = new_height * 16
    quantized.palette.save('palette')
    resized_image = quantized.resize((for_result_w, for_result_h))
    result_clear = Image.new('RGB', (for_result_w, for_result_h), (255, 255, 255))
    return Drawer(resized_image, result_clear, new_width, new_height, i_pixels)

def serve_pil_image(pil_img):
    img_io = BytesIO()
    pil_img.save(img_io, 'PNG')
    img_io.seek(0)
    return Response(img_io.getvalue(), mimetype='image/png')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5222)