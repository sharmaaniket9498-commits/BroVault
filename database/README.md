# BroVault database setup

1. Open MySQL Workbench and connect to your local MySQL Server.
2. Open and execute `schema.sql`. It creates the `brovault_db` database and required tables without dropping existing data.
3. Configure the connection in the project `.env` file.
4. Start the app with `run.bat`. The application seeds sample categories/products only when those tables are empty and creates the demo administrator only when the configured admin email is absent.

`seed_data.sql` adds the category list and the `VAULT10` coupon for a fresh database. Product samples are inserted by `app.py` only when the products table is empty.

The app uses `Pending`, `Confirmed`, `Processing`, `Shipped`, `Delivered`, and `Cancelled` as order statuses. QR payment submission is stored in the separate `orders.payment` field and remains unverified until manually checked.
