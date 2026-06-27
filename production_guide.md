# Production Launch Guide — Live Café Deployment

This guide outlines the steps to configure, deploy, secure, and operate the Café Ordering & Management System in a live, customer-facing environment.

---

## 1. Environment Configurations (`.env`)

Configure your café branding and settings inside the `.env` file at the root of the project. The system automatically reads these variables to customize page headers, print invoices, and compute tax rates.

```ini
# --- Database Configuration ---
# For SQLite (default):
DATABASE_URL=sqlite:///./hotel_management.db
# For MySQL:
# DATABASE_URL=mysql+pymysql://root:secure_mysql_password@db:3306/hotel_db

# --- Security Secrets ---
# The system automatically generates safe, random hex strings for these 
# on first startup if they are left as default.
JWT_SECRET=super-secret-jwt-key-2026-change-me-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
QR_SECRET=aero-cafe-secret-2026-change-this-to-something-random

# --- White-label Cafe Customization ---
CAFE_NAME=Cafe Mocha
CAFE_ADDRESS=Plot 12, High Street, Sector 5
CAFE_PHONE=+91 98765 43210
CAFE_GSTIN=27AAAAA1111A1Z1
CURRENCY_SYMBOL=₹
GST_PERCENTAGE=5.0
TOTAL_TABLES=8

# --- Employee/Admin Default Passwords ---
ADMIN_PASSWORD=admin_mocha_password
WAITER_PASSWORD=waiter_mocha_password
KITCHEN_PASSWORD=kitchen_mocha_password

# --- CORS Origin Restrictions ---
# In production, set this to your actual domain name to restrict access.
# Example: ALLOWED_ORIGINS=https://cafemocha.com,https://www.cafemocha.com
ALLOWED_ORIGINS=*
```

---

## 2. Docker Compose Production Deployment

The project contains a pre-configured `docker-compose.yml` that runs both the **FastAPI web server** and a **MySQL database** container.

### Step 2.1: Start the services
Run the following command to start both containers in detached mode:
```bash
docker-compose up -d --build
```

This starts:
- The MySQL database on port `3306`.
- The FastAPI application (which serves both backend endpoints and frontend HTML static files) on port `8000`.

### Step 2.2: Database Persistence
All database changes (orders, invoices, menu items, users) are persisted in the Docker Volume named `db_data`. They will **not** be lost if you restart the containers.

---

## 3. Reverse Proxy & HTTPS (SSL) Setup

For customers to scan QR codes and place orders securely using their mobile phones, your server must be accessible over the internet via `HTTPS` (secured with Let's Encrypt SSL).

### Step 3.1: Install Nginx and Certbot
On a Ubuntu VPS, run:
```bash
sudo apt update
sudo apt install nginx certbot python3-certbot-nginx -y
```

### Step 3.2: Configure Nginx Configuration
Create a site configuration under `/etc/nginx/sites-available/cafemocha` (replace `cafemocha.com` with your actual domain):
```nginx
server {
    listen 80;
    server_name cafemocha.com www.cafemocha.com;

    # Backend/Frontend redirect to FastAPI container
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable the configuration and reload Nginx:
```bash
sudo ln -s /etc/nginx/sites-available/cafemocha /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Step 3.3: Install SSL Certificate
Generate a free Let's Encrypt SSL certificate by executing:
```bash
sudo certbot --nginx -d cafemocha.com -d www.cafemocha.com
```
Certbot will automatically configure SSL redirects. All traffic to your site will now be secured via HTTPS.

---

## 4. QR Code Generation & Printing

Once the site is live at `https://cafemocha.com`, you are ready to print the QR codes for your tables.

1. Open your browser and navigate to:
   `https://cafemocha.com/qrcodes.html`
2. You will see a list of generated QR codes matching the `TOTAL_TABLES` configured in your `.env` file.
3. The page is styled using a dedicated print layout. Press **`Ctrl + P`** (or `Cmd + P` on Mac) to print.
4. Set margins to "Minimum" or "None" and print. The cards will print with dashed borders, ready to be cut and stuck to the respective tables.

> [!WARNING]
> QR signatures are securely cryptographically signed using the `QR_SECRET` token. If you ever change the `QR_SECRET` in your `.env`, previously printed QR codes will become invalid and must be printed again.

---

## 5. Regular Database Backups

It is recommended to schedule regular database backups to safeguard café transactions.

### For MySQL (Docker)
You can back up your database to a `.sql` file using `mysqldump` directly from the container:
```bash
docker-compose exec -T db mysqldump -u root -prootpassword hotel_db > backup.sql
```

### For SQLite (Default File Deployment)
Simply make a copy of the `hotel_management.db` file:
```bash
cp hotel_management.db backup_hotel_management.db
```
