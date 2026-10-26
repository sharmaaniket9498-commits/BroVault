# BROVAULT — Gifts for Him

**Tagline:** Small Gifts. Big Impression.

BroVault is a Flask + Jinja2 + vanilla JavaScript + MySQL men's gifting store adapted from the supplied Giftora project architecture. The project includes product browsing/search/filtering/sorting, registration/login, cart, wishlist, coupons, Gift Finder, a 2–4 item gift-box builder, COD checkout, a UPI QR demo flow, customer orders, inventory management, admin product/category/coupon/order management, Chart.js dashboard/report views and CSV export.

## Requirements

- Windows 10/11
- Python 3.10+
- MySQL Server 8+ and MySQL Workbench (or a MySQL client)

## First-time setup

1. Extract the `BroVault` folder somewhere convenient.
2. Start MySQL Server.
3. Open MySQL Workbench and run the complete `database/schema.sql` script. It creates `brovault_db` and its tables. Do not drop or clear an existing database.
4. Double-click `run.bat`. The launcher works from its own folder, creates `.venv` only if it does not exist, installs dependencies, and starts Flask.
5. On first run, `run.bat` copies `.env.example` to `.env` if `.env` does not exist. Edit `.env` with your local MySQL credentials, then run `run.bat` again.
6. Open http://127.0.0.1:5000.

### PowerShell alternative

```powershell
cd path\to\BroVault
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
copy .env.example .env
# Edit .env with your MySQL password, then:
.\.venv\Scripts\python.exe app.py
```

Do not copy `.env.example` over an existing `.env`; that would overwrite your settings.

## Demo admin login

- Email: `admin@brovault.local`
- Initial password: value of `ADMIN_PASSWORD` in `.env` (default `ChangeMe@123`)

Change the default password before using the app beyond a local demonstration. If an admin account already exists, startup does not reset its password.

## Catalogue and database safety

- On startup, the app seeds 10 categories and 26 sample products only when the corresponding tables are empty.
- Startup does not drop tables or clear existing users, orders, or products.
- A small additive migration adds `orders.checkout_token` when it is missing. It does not delete data.
- `database/seed_data.sql` can add categories and the `VAULT10` coupon. Product sample data is inserted by the application only when the products table is empty.
- `VAULT10` is a 10% demo coupon.

## Payment notes

Cash on Delivery is available. **Scan QR & Pay is a demo/manual-verification flow, not a payment gateway.** Set `UPI_ID` to your own UPI ID to generate an order-specific QR. The app records payment as submitted/unverified and does not claim to verify bank receipt automatically.

## Current limitations

- Contact form email delivery is not configured; the page explicitly says so.
- PDF export is not included; CSV order export is available.
- Product artwork included in this ZIP is locally stored custom SVG illustration, not third-party product photography.
- Test the app against your own running MySQL server and verify local configuration before production use. This project is intended as a local/demo application and needs additional production hardening before public deployment.

## Troubleshooting

- **MySQL connection error:** check MySQL is running and `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`, `MYSQL_PASSWORD`, and `MYSQL_DATABASE` in `.env`.
- **Unknown database/table:** run `database/schema.sql` in MySQL Workbench.
- **Address already in use:** stop the other Flask process or change the port at the bottom of `app.py`.
- **QR missing:** configure `UPI_ID` in `.env`; QR payment remains unverified even after the user submits it.
