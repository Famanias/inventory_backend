import sqlite3

# Connect to SQLite database (creates db.sqlite3 if it doesn't exist)
conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()


# Sample computer parts data
computer_parts = [
    ("Intel Core i9-12900K", "CPU", 20, 549.99),
    ("AMD Ryzen 7 5800X3D", "CPU", 18, 429.99),
    ("NVIDIA RTX 4070 Ti", "GPU", 8, 899.99),
    ("AMD Radeon RX 7900 XT", "GPU", 10, 799.99),
    ("Kingston Fury Beast 16GB DDR4", "RAM", 40, 79.99),
    ("Corsair Dominator Platinum 32GB DDR5", "RAM", 15, 199.99),
    ("Crucial P3 Plus 2TB NVMe", "Storage", 25, 159.99),
    ("Seagate Barracuda 8TB HDD", "Storage", 30, 139.99),
    ("HyperX Pulsefire Haste Mouse", "Peripherals", 50, 59.99),
    ("SteelSeries Apex Pro Keyboard", "Peripherals", 20, 199.99),
    ("MSI MPG B650 Tomahawk Motherboard", "Motherboard", 12, 219.99),
    ("Noctua NH-U12S Cooler", "Cooling", 35, 69.99),
    ("Corsair RM850x PSU", "Power Supply", 18, 149.99),
    ("Lian Li Lancool 205 Mesh Case", "Case", 10, 99.99),
    ("Dell UltraSharp 32-inch 4K Monitor", "Monitor", 8, 799.99),
    ("Intel Core i5-13600K", "CPU", 22, 319.99),
    ("AMD Ryzen 5 7600X", "CPU", 25, 299.99),
    ("NVIDIA RTX 4060", "GPU", 15, 399.99),
    ("Sapphire Pulse RX 7600", "GPU", 20, 269.99),
    ("TeamGroup T-Force 16GB DDR5", "RAM", 30, 109.99),
    ("Patriot Viper Steel 64GB DDR4", "RAM", 10, 229.99),
    ("WD Black SN850X 1TB NVMe", "Storage", 28, 139.99),
    ("Toshiba X300 6TB HDD", "Storage", 15, 119.99),
    ("Logitech MX Master 3S Mouse", "Peripherals", 45, 99.99),
    ("Keychron K8 Pro Keyboard", "Peripherals", 25, 89.99),
    ("Gigabyte Z790 Aorus Elite Motherboard", "Motherboard", 14, 249.99),
    ("be quiet! Pure Rock 2 Cooler", "Cooling", 40, 49.99),
    ("Seasonic Focus GX-650 PSU", "Power Supply", 20, 109.99),
    ("Fractal Design Meshify C Case", "Case", 12, 89.99),
    ("LG 27GN950-B 27-inch 4K Monitor", "Monitor", 10, 699.99),
    ("Intel Core i3-13100", "CPU", 30, 149.99),
    ("AMD Ryzen 3 5300G", "CPU", 35, 129.99),
    ("ASUS TUF Gaming RTX 3090", "GPU", 5, 999.99),
    ("Zotac Gaming RTX 3050", "GPU", 18, 249.99),
    ("Corsair Vengeance LPX 8GB DDR4", "RAM", 60, 49.99)
]

# Insert data into inventory table
cursor.executemany('''
    INSERT INTO products_product (name, category, quantity, price)
    VALUES (?, ?, ?, ?)
''', computer_parts)

# Commit changes and close connection
conn.commit()
conn.close()

print("db.sqlite3 file created and populated with computer parts inventory.")