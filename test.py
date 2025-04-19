import sqlite3

# Connect to SQLite database (creates db.sqlite3 if it doesn't exist)
conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()


# Sample computer parts data
computer_parts = [ ("Heroin", "Opioid", 1, 150.00, 3), ("Cocaine", "Stimulant", 1, 100.00, 3), ("Methamphetamine", "Stimulant", 1, 80.00, 3), ("Fentanyl", "Opioid", 1, 500.00, 3), ("LSD", "Hallucinogen", 1, 10000.00, 3), ("MDMA (Ecstasy)", "Stimulant/Hallucinogen", 1, 200.00, 3), ("Psilocybin (Magic Mushrooms)", "Hallucinogen", 1, 10.00, 3), ("PCP (Phencyclidine)", "Dissociative Anesthetic", 1, 25.00, 3), ("Ketamine (Illegal Use)", "Dissociative Anesthetic", 1, 150.00, 3), ("GHB", "Depressant", 1, 15.00, 3), ("Rohypnol", "Depressant", 1, 5000.00, 3), ("Crack Cocaine", "Stimulant", 1, 100.00, 3), ("Morphine (Illegal Use)", "Opioid", 1, 300.00, 3), ("Codeine (Illegal Use)", "Opioid", 1, 100.00, 3), ("Oxycodone (Illegal Use)", "Opioid", 1, 1333.33, 3), ("Hydrocodone (Illegal Use)", "Opioid", 1, 1500.00, 3), ("Hydromorphone", "Opioid", 1, 5000.00, 3), ("Meperidine", "Opioid", 1, 500.00, 3), ("Methadone (Illegal Use)", "Opioid", 1, 1000.00, 3), ("Amphetamine (Illegal Use)", "Stimulant", 1, 40.00, 3), ("DMT", "Hallucinogen", 1, 1000.00, 3), ("Ayahuasca", "Hallucinogen", 1, 10.00, 3), ("Mescaline", "Hallucinogen", 1, 120.00, 3), ("Synthetic Cannabinoids", "Cannabinoid", 1, 15.00, 3), ("Bath Salts (Cathinones)", "Stimulant", 1, 50.00, 3), ("Benzodiazepines (Illegal Use)", "Depressant", 1, 5000.00, 3), ("Salvia", "Hallucinogen", 1, 40.00, 3), ("Inhalants (e.g., Toluene)", "Inhalant", 1, 0.05, 3), ("Kratom (Illegal in Some Areas)", "Opioid-like", 1, 3.00, 3), ("NBOMe", "Hallucinogen", 1, 10000.00, 3) ]

# Insert data into inventory table
cursor.executemany('''
    INSERT INTO products_product(name, category, quantity, price, user_id)
    VALUES (?, ?, ?, ?, ?)
''', computer_parts)

# Commit changes and close connection
conn.commit()
conn.close()

print("db.sqlite3 file created and populated with computer parts inventory.")