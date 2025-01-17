# Copyright (C) 2019-2022 Artem Shurshilov <shurshilov.a@yandex.ru>
# License OPL-1.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Editor photo, pictures, image",
    "summary": "Out of box image, picture, photo editor \
(Crop, Flip, Rotation, Drawing, Shape, Icon, Text, Mask Filter, Image Filter raw,download,upload,undo,redo,reset,delete Object(Shape, Line, Mask Image...)) \
and filter(Grayscale, Invert, Sepia, Blur Sharpen, Emboss, Remove White, Brightness, Noise, Pixelate, Color Filter, Tint, Multiply, Blend) \
edit images edit editor images editor management images management text images text drawing images drawing draw images draw filter images filter \
mask images mask icon images icon crop images crop rotation images rotation flip images flip edit pictures edit photos edit filters \
photos filters crop photos crop text photos text drawing photos drawing draw photos draw mask photos mask managment photos managment \
flip photos flip rotation photos rotation pictures rotation crop pictures crop pictures draw pictures drawing pictures editor pictures \
filters pictures filters image editor photos editor resizer \
",
    "author": "EURO ODOO, Shurshilov Artem",
    "maintainer": "EURO ODOO",
    "website": "https://eurodoo.com",
    "live_test_url": "https://eurodoo.com/login_employee?login=demo1&amp;password=demo1",
    # Categories can be used to filter modules in modules listing
    "category": "Extra Tools",
    "version": "16.1.1.3",
    # any module necessary for this one to work correctly
    "depends": ["web", "field_image_preview"],
    "license": "OPL-1",
    "price": 49,
    "currency": "EUR",
    "images": [
        "static/description/giphy.gif",
        "static/description/img.png",
        "static/description/img2.png",
        "static/description/img3.png",
    ],
    # 'data': [
    #     'views/assets.xml',
    # ],
    # 'qweb': [ 'static/src/xml/image.xml', ],
    "installable": True,
    "application": False,
    # If it's True, the modules will be auto-installed when all dependencies
    # are installed
    "auto_install": False,
    "cloc_exclude": [
        "static/src/lib/**/*",  # exclude a single folder
    ],
    "assets": {
        "web.assets_backend": [
            "field_image_editor/static/src/lib/tui/fabric.min.js",
            "field_image_editor/static/src/lib/tui/tui-code-snippet.min.js",
            "field_image_editor/static/src/lib/tui/tui-color-picker.css",
            "field_image_editor/static/src/lib/tui/tui-color-picker.js",
            "field_image_editor/static/src/lib/tui/tui.image-editor/dist/tui-image-editor.css",
            "field_image_editor/static/src/lib/tui/tui.image-editor/dist/tui-image-editor.js",
            "field_image_editor/static/src/lib/tui/tui.image-editor/examples/js/theme/black-theme.js",
            "field_image_editor/static/src/component/image_field.xml",
            "field_image_editor/static/src/component/image_field.js",
        ],
    },
}
