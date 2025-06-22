import csv
import mysql.connector
from datetime import datetime

DB_CONFIG = {
	'host': '192.168.112.132',
	'user': 'user',
	'password': '123',
	'database': 'Fund'
}

def get_db_connection():
	return mysql.connector.connect(**DB_CONFIG)

def get_funds():
	try:
		connection = get_db_connection()
		cursor = connection.cursor(dictionary=True)
		query = "SELECT * FROM fund_list"
		cursor.execute(query)
		result = cursor.fetchall()
		cursor.close()
		connection.close()
		return result
	except Exception as e:
		raise e

def get_transactions_by_code(fund_code):
	try:
		connection = get_db_connection()
		cursor = connection.cursor(dictionary=True)
		query = """
			SELECT * FROM transactions 
			WHERE code = %s 
			ORDER BY date DESC
		"""
		cursor.execute(query, (fund_code,))
		result = cursor.fetchall()
		cursor.close()
		connection.close()
		return result
	except Exception as e:
		raise e

def get_transactions_all():
	try:
		connection = get_db_connection()
		cursor = connection.cursor(dictionary=True)
		query = "SELECT * FROM transactions"
		cursor.execute(query)
		result = cursor.fetchall()
		cursor.close()
		connection.close()
		return result
	except Exception as e:
		raise e

def import_csv(file):
	try:
		content = file.read().decode('utf-8').splitlines()
		reader = csv.DictReader(content)
		connection = get_db_connection()
		cursor = connection.cursor()
		if 'id' in reader.fieldnames and 'name' in reader.fieldnames:
			for row in reader:
				query = """
					INSERT INTO fund_list (id, name, type, manager, established_date)
					VALUES (%s, %s, %s, %s, %s)
					ON DUPLICATE KEY UPDATE 
						name = VALUES(name),
						type = VALUES(type),
						manager = VALUES(manager),
						established_date = VALUES(established_date)
				"""
				cursor.execute(query, (
					row['id'],
					row['name'],
					row.get('type', None),
					row.get('manager', None),
					row.get('established_date', None)
				))
		else:
			for row in reader:
				query = """
					INSERT INTO transactions 
					(code, type, date, money, num, g, price, value, commission, is_valid)
					VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
					ON DUPLICATE KEY UPDATE 
						type = VALUES(type),
						date = VALUES(date),
						money = VALUES(money),
						num = VALUES(num),
						g = VALUES(g),
						price = VALUES(price),
						value = VALUES(value),
						commission = VALUES(commission),
						is_valid = VALUES(is_valid)
				"""
				cursor.execute(query, (
					row['code'],
					row['type'],
					row['date'],
					row['money'],
					float(row['num']) if row['num'] else None,
					float(row['g']) if row['g'] else None,
					float(row['price']) if row['price'] else None,
					float(row['value']) if row['value'] else None,
					float(row['commission']) if row['commission'] else None,
					int(row.get('is_valid', 1))
				))
		connection.commit()
		cursor.close()
		connection.close()
		return True
	except Exception as e:
		connection.rollback()
		raise e

def add_transaction(keys, nums, values):
	try:
		connection = get_db_connection()
		cursor = connection.cursor()
		query = f"INSERT INTO transactions ({keys}) VALUES ({nums})"
		print(query, values)
		cursor.execute(query, values)
		connection.commit()
		cursor.close()
		connection.close()
		return True
	except Exception as e:
		connection.rollback()
		raise e

def del_transaction(id):
	try:
		connection = get_db_connection()
		cursor = connection.cursor()
		query = f"DELETE FROM transactions WHERE id = %s"
		cursor.execute(query, (id,))
		connection.commit()
		cursor.close()
		connection.close()
		return True
	except Exception as e:
		connection.rollback()
		raise e
	
def update_transaction(id, keys, values):
	try:
		connection = get_db_connection()
		cursor = connection.cursor()
		set_pattern = ', '.join([f"{key} = %s" for key in keys])
		query = f"UPDATE transactions SET {set_pattern} WHERE id=%s"
		print(query)
		cursor.execute(query, values+[id])
		connection.commit()
		cursor.close()
		connection.close()
		return True
	except Exception as e:
		connection.rollback()
		raise e
	