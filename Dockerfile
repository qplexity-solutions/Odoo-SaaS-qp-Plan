# Use the official Odoo image from Docker Hub as the base image
FROM qplexity/odoo:latest

# Copy custom addons
COPY custom_addons /mnt/extra-addons

# Copy custom configuration files or modules
COPY odoo.conf /etc/odoo/


# Expose Odoo services
EXPOSE 8069 8071 8072


# Command to run Odoo
CMD ["odoo", "--config=/etc/odoo/odoo.conf"]

