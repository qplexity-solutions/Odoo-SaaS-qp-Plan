# Copyright (C) 2023 Artem Shurshilov <shurshilov.a@yandex.ru>
# License OPL-1.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Login/authentication with photo",
    "summary": """Adds functional auth by photo
    Odoo login/sign in with face recognition login face login photo login sign in  photo sign in
    signin photo signin login image login images login sign in image sign in
    login picture login auth photo auth image auth photo authorize image authorize photo
    login using Face Recognition face auth face authentication face authentication photo authentication
    user authentication face authentication picture""",
    "author": "EURO ODOO, Shurshilov Artem",
    "maintainer": "EURO ODOO",
    "website": "https://eurodoo.com",
    # Categories can be used to filter modules in modules listing
    "category": "Tools",
    "version": "16.1.0.1",
    # any module necessary for this one to work correctly
    "depends": ["base", "base_setup", "web", "web_image_webcam"],
    "external_dependencies": {
        "python": ["numpy"],
    },
    "license": "OPL-1",
    "price": 179,
    "currency": "EUR",
    # always loaded
    "images": [
        "static/description/work.gif",
        "static/description/login.png",
        "static/description/settings.png",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/form_image_preview_templates.xml",
        "views/res_users.xml",
        "views/res_users_image.xml",
        "views/res_users_log.xml",
        "views/res_config_settings_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "auth_faceid/static/src/js/res_users_kanban_face_recognition.js",
        ],
        "web.assets_common": [
            "auth_faceid/static/src/js/lib/sweetalert2.min.css",
            "auth_faceid/static/src/js/lib/sweetalert2.all.min.js",
            "auth_faceid/static/src/js/lib/human.js",
        ],
        "web.assets_frontend": [
            "auth_faceid/static/src/js/lib/sweetalert2.min.css",
            "auth_faceid/static/src/js/lib/sweetalert2.all.min.js",
            "auth_faceid/static/src/js/lib/human.js",
            "auth_faceid/static/src/css/lightbox.css",
            "auth_faceid/static/src/js/faceid_dialog.js",
            "auth_faceid/static/src/js/faceid_base.js",
            "auth_faceid/static/src/xml/FaceRecognitionAuthDialog.xml",
        ],
    },
    "installable": True,
    "application": False,
    # If it's True, the modules will be auto-installed when all dependencies
    # are installed
    "auto_install": False,
}
