from flask import Flask, render_template

app = Flask(__name__)
app.static_folder = 'static'


@app.route('/')
def home():
    header_image_src = "/static/shop.jpg"  # Путь к изображению заголовка (одинаков для всех страниц)
    return render_template('base.html', header_image_src=header_image_src)


@app.route('/clothing/')
def clothing():
    header_image_src = "/static/shop.jpg"  # Путь к изображению заголовка (одинаков для всех страниц)
    footer_image_src = "/static/clothing.jpg"  # Путь к изображению нижнего фото, относящемуся одежде
    return render_template('clothing.html', header_image_src=header_image_src,
                           footer_image_src=footer_image_src)


@app.route('/shoes/')
def shoes():
    header_image_src = "/static/shop.jpg"  # Путь к изображению заголовка (одинаков для всех страниц)
    footer_image_src = "/static/shoes.jpg"  # Путь к изображению нижнего фото, относящемуся обуви
    return render_template('shoes.html', header_image_src=header_image_src,
                           footer_image_src=footer_image_src)


@app.route('/product/')
def product():
    header_image_src = "/static/shop.jpg"  # Путь к изображению заголовка (одинаков для всех страниц)
    footer_image_src = "/static/product.jpg"  # Путь к изображению нижнего фото, относящемуся к товарам
    product_info = {
        'name': 'Образец продукта',
        'description': 'Пример описания продукта.',
        'price': 199.99,
    }
    return render_template('product.html', header_image_src=header_image_src,
                           footer_image_src=footer_image_src, product=product_info)


if __name__ == '__main__':
    app.run(debug=True)
