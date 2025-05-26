#!/usr/bin/env python3
"""
KEBOOLA PYTHON TRANSFORMÁCIA - ČISTENIE DÁT CSV_INPUT
Tento script vyčistí problémové dáta v transakčnej tabuľke
"""

import pandas as pd
import numpy as np
import re
from datetime import datetime
import os

# Nastavenie pandas options pre lepšie spracovanie
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

# Načítanie dát z Keboola input
input_file = '/data/in/tables/csv_input.csv'
df = pd.read_csv(input_file, dtype=str)  # Načítanie všetkých stĺpcov ako string

print(f"Načítaných záznamov: {len(df)}")
print(f"Stĺpcov: {len(df.columns)}")

# Konverzia numerických stĺpcov
numeric_columns = ['Quantity', 'Price', 'TotalValue', 'PaymentAmount']
for col in numeric_columns:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

# =====================================================
# 1. ANALÝZA PROBLÉMOV
# =====================================================

def analyze_data_quality(df):
    """Analýza kvality dát"""
    issues = []
    total_records = len(df)
    
    # Chýbajúce kategórie
    missing_category = df['Category'].isna().sum() + (df['Category'] == '').sum()
    issues.append({
        'issue_type': 'Missing Category',
        'issue_count': missing_category,
        'percentage': round(missing_category * 100.0 / total_records, 2)
    })
    
    # Chýbajúce produkty
    missing_product = df['Product'].isna().sum() + (df['Product'] == '').sum()
    issues.append({
        'issue_type': 'Missing Product',
        'issue_count': missing_product,
        'percentage': round(missing_product * 100.0 / total_records, 2)
    })
    
    # Chýbajúce dátumy
    missing_date = df['TransactionDate'].isna().sum() + (df['TransactionDate'] == '').sum()
    issues.append({
        'issue_type': 'Missing Transaction Date',
        'issue_count': missing_date,
        'percentage': round(missing_date * 100.0 / total_records, 2)
    })
    
    # Neplatné emaily
    invalid_emails = ((df['Email'] == 'invalid_email') | 
                     (df['Email'] == 'not_an_email') | 
                     df['Email'].isna()).sum()
    issues.append({
        'issue_type': 'Invalid Email Addresses',
        'issue_count': invalid_emails,
        'percentage': round(invalid_emails * 100.0 / total_records, 2)
    })
    
    # Chýbajúce adresy
    missing_address = df['ShippingAddress'].isna().sum() + (df['ShippingAddress'] == '').sum()
    issues.append({
        'issue_type': 'Missing Shipping Address',
        'issue_count': missing_address,
        'percentage': round(missing_address * 100.0 / total_records, 2)
    })
    
    # Chýbajúce payment methods
    missing_payment = df['PaymentMethod'].isna().sum() + (df['PaymentMethod'] == '').sum()
    issues.append({
        'issue_type': 'Missing Payment Method',
        'issue_count': missing_payment,
        'percentage': round(missing_payment * 100.0 / total_records, 2)
    })
    
    # Chýbajúce ceny
    missing_price = df['Price'].isna().sum()
    issues.append({
        'issue_type': 'Missing Price',
        'issue_count': missing_price,
        'percentage': round(missing_price * 100.0 / total_records, 2)
    })
    
    return pd.DataFrame(issues).sort_values('issue_count', ascending=False)

# Vytvorenie tabuľky s problémami
quality_issues = analyze_data_quality(df)
print("\nIdentifikované problémy:")
print(quality_issues)

# =====================================================
# 2. ČISTENIE DÁT
# =====================================================

def clean_data(df):
    """Hlavná funkcia na čistenie dát"""
    df_clean = df.copy()
    
    # Sledovanie opráv
    df_clean['Category_Was_Fixed'] = 0
    df_clean['Product_Was_Fixed'] = 0
    df_clean['Date_Was_Missing'] = 0
    df_clean['Email_Was_Invalid'] = 0
    df_clean['Price_Was_Fixed'] = 0
    
    # 1. OPRAVA KATEGÓRIÍ
    def fix_category(row):
        if pd.isna(row['Category']) or row['Category'] == '':
            product = str(row['Product']).upper()
            if any(keyword in product for keyword in ['LAPTOP', 'SMARTPHONE', 'HEADPHONES']):
                return 'Electronics', 1
            elif any(keyword in product for keyword in ['DUMBBELLS', 'YOGA']):
                return 'Sports', 1
            elif any(keyword in product for keyword in ['SOFA', 'BLENDER']):
                return 'Home & Garden', 1
            elif any(keyword in product for keyword in ['BOARD GAME', 'ACTION FIGURE']):
                return 'Toys', 1
            elif any(keyword in product for keyword in ['PERFUME', 'SHAMPOO', 'FACE CREAM']):
                return 'Beauty', 1
            elif 'COOKBOOK' in product:
                return 'Books', 1
            elif any(keyword in product for keyword in ['THERMOMETER', 'VITAMINS']):
                return 'Health', 1
            elif 'JACKET' in product:
                return 'Fashion', 1
            else:
                return 'Uncategorized', 1
        return row['Category'], 0
    
    category_fixes = df_clean.apply(fix_category, axis=1, result_type='expand')
    df_clean['Category_Clean'] = category_fixes[0]
    df_clean['Category_Was_Fixed'] = category_fixes[1]
    
    # 2. OPRAVA PRODUKTOV
    def fix_product(row):
        if pd.isna(row['Product']) or row['Product'] == '':
            return 'Unknown Product', 1
        elif row['Product'] == 'InvalidProd2':
            return 'Product Name Correction Needed', 1
        return row['Product'], 0
    
    product_fixes = df_clean.apply(fix_product, axis=1, result_type='expand')
    df_clean['Product_Clean'] = product_fixes[0]
    df_clean['Product_Was_Fixed'] = product_fixes[1]
    
    # 3. OPRAVA DÁTUMOV
    def parse_date(date_str):
        if pd.isna(date_str) or date_str == '':
            return None, 1
        
        date_str = str(date_str).strip()
        
        # Formát YYYY-MM-DD
        if re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
            try:
                return pd.to_datetime(date_str, format='%Y-%m-%d'), 0
            except:
                pass
        
        # Formát DD-MM-YYYY s časom
        if re.match(r'^\d{2}-\d{2}-\d{4}', date_str):
            try:
                date_part = date_str.split(' ')[0]
                return pd.to_datetime(date_part, format='%d-%m-%Y'), 0
            except:
                pass
        
        # Pokus o automatické parsovanie
        try:
            return pd.to_datetime(date_str), 0
        except:
            return None, 1
    
    date_fixes = df_clean['TransactionDate'].apply(parse_date)
    df_clean['TransactionDate_Clean'] = [fix[0] for fix in date_fixes]
    df_clean['Date_Was_Missing'] = [fix[1] for fix in date_fixes]
    
    # 4. OPRAVA CIEN
    def fix_price(row):
        # Konverzia na numerické hodnoty
        try:
            price = pd.to_numeric(row['Price'], errors='coerce')
            total_value = pd.to_numeric(row['TotalValue'], errors='coerce')
            quantity = pd.to_numeric(row['Quantity'], errors='coerce')
        except:
            price = None
            total_value = None
            quantity = None
        
        if pd.isna(price):
            if not pd.isna(total_value) and not pd.isna(quantity) and quantity > 0:
                return total_value / quantity, 1
            else:
                return 0, 1
        return price, 0
    
    price_fixes = df_clean.apply(fix_price, axis=1, result_type='expand')
    df_clean['Price_Clean'] = price_fixes[0]
    df_clean['Price_Was_Fixed'] = price_fixes[1]
    
    # 5. OPRAVA PAYMENT METHODS
    def fix_payment_method(method):
        if pd.isna(method) or method == '':
            return 'Not Specified'
        elif method == 'UnsupportedMethod':
            return 'Method Verification Needed'
        return method
    
    df_clean['PaymentMethod_Clean'] = df_clean['PaymentMethod'].apply(fix_payment_method)
    
    # 6. OPRAVA ADRIES
    def fix_address(address):
        if pd.isna(address) or address == '':
            return 'Address Not Provided'
        elif address == 'UNKNOWN ADDRESS':
            return 'Address Verification Needed'
        return address
    
    df_clean['ShippingAddress_Clean'] = df_clean['ShippingAddress'].apply(fix_address)
    
    # 7. OPRAVA EMAILOV
    def fix_email(email):
        if pd.isna(email) or email in ['invalid_email', 'not_an_email']:
            return 'Email Not Provided', 1
        elif '@' not in str(email):
            return 'Invalid Email Format', 1
        return email, 0
    
    email_fixes = df_clean['Email'].apply(fix_email)
    df_clean['Email_Clean'] = [fix[0] for fix in email_fixes]
    df_clean['Email_Was_Invalid'] = [fix[1] for fix in email_fixes]
    
    # 8. OPRAVA ORDER STATUS
    def fix_order_status(status):
        if status == 'UnknownStatus':
            return 'Status Verification Needed'
        elif pd.isna(status):
            return 'Pending'
        return status
    
    df_clean['OrderStatus_Clean'] = df_clean['OrderStatus'].apply(fix_order_status)
    
    # 9. OPRAVA PAYMENT AMOUNTS
    def fix_payment_amount(row):
        try:
            payment_amount = pd.to_numeric(row['PaymentAmount'], errors='coerce')
            total_value = pd.to_numeric(row['TotalValue'], errors='coerce')
        except:
            return row['TotalValue'] if not pd.isna(row['TotalValue']) else 0
        
        if pd.isna(payment_amount):
            return total_value if not pd.isna(total_value) else 0
        
        if pd.isna(total_value):
            return payment_amount
            
        # Ak je rozdiel väčší ako 10%, použiť TotalValue
        if abs(payment_amount - total_value) > total_value * 0.1:
            return total_value
        return payment_amount
    
    df_clean['PaymentAmount_Clean'] = df_clean.apply(fix_payment_amount, axis=1)
    
    return df_clean

# Vyčistenie dát
df_cleaned = clean_data(df)

print(f"\nOpravy vykonané:")
print(f"- Kategórie opravené: {df_cleaned['Category_Was_Fixed'].sum()}")
print(f"- Produkty opravené: {df_cleaned['Product_Was_Fixed'].sum()}")
print(f"- Chýbajúce dátumy: {df_cleaned['Date_Was_Missing'].sum()}")
print(f"- Neplatné emaily opravené: {df_cleaned['Email_Was_Invalid'].sum()}")
print(f"- Ceny opravené: {df_cleaned['Price_Was_Fixed'].sum()}")

# =====================================================
# 3. VYTVORENIE ANALYTICS-READY TABUĽKY
# =====================================================

def create_analytics_table(df_clean):
    """Vytvorenie tabuľky pripravenej na analýzu"""
    # Filtrovanie záznamov s platným dátumom
    df_analytics = df_clean[df_clean['TransactionDate_Clean'].notna()].copy()
    
    # Pridanie odvodených stĺpcov
    df_analytics['Transaction_Year'] = df_analytics['TransactionDate_Clean'].dt.year
    df_analytics['Transaction_Month'] = df_analytics['TransactionDate_Clean'].dt.month
    df_analytics['Transaction_Quarter'] = df_analytics['TransactionDate_Clean'].dt.quarter
    
    # Business metriky
    df_analytics['Had_Discount'] = (~df_analytics['DiscountCode'].isna() & 
                                   (df_analytics['DiscountCode'] != '')).astype(int)
    
    def categorize_transaction_value(total_value):
        try:
            value = pd.to_numeric(total_value, errors='coerce')
            if pd.isna(value):
                return 'Unknown Value'
            elif value >= 1000:
                return 'High Value'
            elif value >= 500:
                return 'Medium Value'
            else:
                return 'Low Value'
        except:
            return 'Unknown Value'
    
    df_analytics['Transaction_Value_Category'] = df_analytics['TotalValue'].apply(categorize_transaction_value)
    
    # Indikátor kvality dát
    df_analytics['Had_Data_Quality_Issues'] = ((df_analytics['Category_Was_Fixed'] == 1) |
                                              (df_analytics['Product_Was_Fixed'] == 1) |
                                              (df_analytics['Date_Was_Missing'] == 1) |
                                              (df_analytics['Email_Was_Invalid'] == 1)).astype(int)
    
    # Výber finálnych stĺpcov
    final_columns = [
        'TransactionID', 'Category_Clean', 'Product_Clean', 'TransactionDate_Clean',
        'Transaction_Year', 'Transaction_Month', 'Transaction_Quarter',
        'Quantity', 'Price_Clean', 'TotalValue', 'CustomerID',
        'PaymentMethod_Clean', 'OrderStatus_Clean', 'PaymentAmount_Clean',
        'DiscountCode', 'Had_Discount', 'Transaction_Value_Category',
        'Had_Data_Quality_Issues'
    ]
    
    # Premenovanie stĺpcov
    column_mapping = {
        'Category_Clean': 'Category',
        'Product_Clean': 'Product',
        'TransactionDate_Clean': 'TransactionDate',
        'Price_Clean': 'Price',
        'PaymentMethod_Clean': 'PaymentMethod',
        'OrderStatus_Clean': 'OrderStatus',
        'PaymentAmount_Clean': 'PaymentAmount'
    }
    
    df_final = df_analytics[final_columns].rename(columns=column_mapping)
    
    return df_final.sort_values('TransactionDate', ascending=False)

# Vytvorenie analytics tabuľky
df_analytics = create_analytics_table(df_cleaned)

# =====================================================
# 4. VYTVORENIE VALIDAČNEJ TABUĽKY
# =====================================================

validation_data = [
    {'metric': 'Original Records', 'count': len(df)},
    {'metric': 'Cleaned Records', 'count': len(df_cleaned)},
    {'metric': 'Analytics Ready Records', 'count': len(df_analytics)},
    {'metric': 'Records with Category Fixed', 'count': df_cleaned['Category_Was_Fixed'].sum()},
    {'metric': 'Records with Product Fixed', 'count': df_cleaned['Product_Was_Fixed'].sum()},
    {'metric': 'Records with Missing Date', 'count': df_cleaned['Date_Was_Missing'].sum()},
    {'metric': 'Records with Invalid Email Fixed', 'count': df_cleaned['Email_Was_Invalid'].sum()},
    {'metric': 'Records with Price Fixed', 'count': df_cleaned['Price_Was_Fixed'].sum()}
]

validation_summary = pd.DataFrame(validation_data)

# =====================================================
# 5. ULOŽENIE VÝSTUPOV
# =====================================================

# Vytvorenie output adresára ak neexistuje
os.makedirs('/data/out/tables', exist_ok=True)

# Uloženie tabuliek
quality_issues.to_csv('/data/out/tables/data_quality_issues.csv', index=False)
df_cleaned.to_csv('/data/out/tables/cleaned_transactions.csv', index=False)
validation_summary.to_csv('/data/out/tables/validation_summary.csv', index=False)
df_analytics.to_csv('/data/out/tables/analytics_ready.csv', index=False)

print(f"\n=== SÚHRN TRANSFORMÁCIE ===")
print(f"Vytvorené výstupné tabuľky:")
print(f"1. data_quality_issues.csv - {len(quality_issues)} problémov identifikovaných")
print(f"2. cleaned_transactions.csv - {len(df_cleaned)} vyčistených záznamov")
print(f"3. validation_summary.csv - {len(validation_summary)} validačných metrík")
print(f"4. analytics_ready.csv - {len(df_analytics)} záznamov pripravených na analýzu")

print(f"\nTransformácia úspešne dokončená!")

# Zobrazenie prehľadu výsledkov
print(f"\n=== PREHĽAD VÝSLEDKOV ===")
print(f"Najčastejšie kategórie po čistení:")
print(df_analytics['Category'].value_counts().head())

print(f"\nDistribúcia podľa hodnoty transakcií:")
print(df_analytics['Transaction_Value_Category'].value_counts())

print(f"\nPočet transakcií s problémami kvality dát: {df_analytics['Had_Data_Quality_Issues'].sum()}")