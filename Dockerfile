# Use the official Odoo image from Docker Hub as the base image
FROM odoo:16.0



# Install additional packages or dependencies from requirements.txt
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt


# Copy custom addons
COPY custom_addons /mnt/extra-addons

# Copy custom configuration files or modules
COPY odoo.conf /etc/odoo/


# Expose Odoo services
EXPOSE 8069 8071 8072


# Command to run Odoo
CMD ["odoo", "--config=/etc/odoo/odoo.conf"]

