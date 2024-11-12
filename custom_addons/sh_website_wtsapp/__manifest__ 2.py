# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    "name": "WhatsApp Live Chat",
    "author": "Softhealer Technologies",
    "website": "https://www.softhealer.com",
    "support": "support@softhealer.com",
    "category": "Website",
    "license": "OPL-1",
    
    "summary": """Whatsapp Live Chat app Customer Whatsapp Whatsup Live Chat on Whatsup Chat Odoo Whatsapp Chat by Odoo Website Client Whatsup Chat Module Live Chat on WhatsApp Live Chat via WhatsApp Live Chat via Whatsup Chat on WhatsApp from the Odoo Website Chat on WhatsApp from the Website Messaging app Customers through WhatsApp Customers Chat through WhatsApp Website Customers through WhatsApp Website Customers Chat through WhatsApp Chat by Odoo Ecommerce Webpage Whatsapp Chat by Odoo E-commerce Webpage Whatsapp Chat by Odoo eCommerce Webpage Ecommerce Customers through WhatsApp Ecommerce Customers Chat through WhatsApp E-commerce Customers through WhatsApp E-commerce Customers Chat through WhatsApp eCommerce Customers through WhatsApp eCommerce Customers Chat through WhatsApp""",
    
    "description": """Chat with your customers through WhatsApp, the most popular messaging app. Vital extension for your odoo website, which allows you to create stronger relationships with your customers by guiding and advising them in their purchases in real-time.
Now your customers can chat with you on WhatsApp, directly from your odoo website to your mobile!! No need to add your mobile phone number to the mobile address book.
An online chat system provides customers with immediate access to help. Wait times are often much less than in a call centre, and customers can easily multi-task while waiting.
This extension allows you to create a WhatsApp chat button, highly configurable, to show it in different parts of your site to chat with your customers through WhatsApp, the most popular messaging app.""",
    "version": "0.0.1",
    "depends": ["website", "portal"],
    "application": True,
    "data": [
        "data/res_config_settings_data.xml",
        "views/sh_website_wtsapp_templates.xml",
        "views/res_config_settings_views.xml",
        "views/website_views.xml",
    ],
    'assets': {
        'web.assets_frontend': [
            'sh_website_wtsapp/static/src/js/detect_mobile.js',
            'sh_website_wtsapp/static/src/css/sh_website_wtsapp.css'
        ],
    },
    "images": ["static/description/background.png", ],
    "auto_install": False,
    "installable": True,
    "price": 25,
    "currency": "EUR"
}
