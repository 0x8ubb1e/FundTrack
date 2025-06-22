import os
from flask import request, jsonify

from database import *

def init_api(app):
	@app.route('/api/funds', methods=['GET'])
	def funds():
		try:
			result = get_funds()
			return jsonify({'success': True, 'data': result})
		except Exception as e:
			return jsonify({'success': False, 'error': str(e)})

	@app.route('/api/transactions/<fund_code>', methods=['GET'])
	def transactions(fund_code):
		try:
			result = get_transactions_by_code(fund_code)
			return jsonify({'success': True, 'data': result})
		except Exception as e:
			return jsonify({'success': False, 'error': str(e)})

	@app.route('/api/add_transaction', methods=['POST'])
	def add():
		try:
			data = request.json
			columns = ', '.join(data.keys())
			nums = ', '.join(['%s'] * len(data))
			values = list(data.values())
			if add_transaction(columns, nums, values):
				return jsonify({'success': True, 'message': 'Transaction added successfully'})
			else:
				return jsonify({'success': False, 'error': 'Failed to add transaction'})
		except Exception as e:
			return jsonify({'success': False, 'error': str(e)})
		
	@app.route('/api/del_transaction', methods=['POST'])
	def delete():
		try:
			data = request.json
			id = data.get("id")
			if del_transaction(id):
				return jsonify({'success': True, 'message': 'Transaction deleted successfully'})
		except Exception as e:
			return jsonify({'success': False, 'error': str(e)})
	
	@app.route('/api/update_transaction_date', methods=['GET'])
	def update_date():
		try:
			result = get_transactions_all()
			for r in result:
				# app.logger.info(r)
				year, month, day = r['year'], r['month'], r['day']
				hour, minute, second = r['hour'], r['minute'], r['second']
				date = f"{year}-{month}-{day} {hour}:{minute}:{second}"
				# app.logger.info(date)
				id = r['id']
				update_transaction(id=id, key="date", value=date)
				# break
			result = get_transactions_all()
			list = []
			list.append(['date', 'ymd', 'true'])
			for r in result:
				a = r['date']
				b = f"{r['year']}-{r['month']}-{r['day']} {r['hour']}:{r['minute']}:{r['second']}"
				c = 'true' if a == b else 'false'
				list.append([a, b, c])
			return jsonify({'success': True, 'data': list})
		except Exception as e:
			return jsonify({'success': False, 'error': str(e)})
		
	@app.route('/api/update_transaction_symbol', methods=['GET'])
	def update_symbol():
		try:
			result = get_transactions_all()
			app.logger.info("get transactions all")
			list = []
			for r in result:
				tmp = []
				app.logger.info(r)
				type, money, num = r['type'], r['money'], r['num']
				g, price = r['g'], r['price']
				tmp.append([type, money, num, g, price])
				

				symbol = '-' if type in ['1', '3'] else ''  # 卖出 或者 分红

				# 将浮点数转换为字符串，并去除负号
				money = float(str(money).replace('-', '')) if money else money
				num = float(str(num).replace('-', '')) if num else num
				g = float(str(g).replace('-', '')) if g else g
				price = float(str(price).replace('-', '')) if price else price

				keys, values = [], []
				if money and money != r['money']:
					keys.append('money')
					values.append(money)
				if num and num != r['num']:
					keys.append('num')
					values.append(num)
				if g and g != r['g']:
					keys.append('g')
					values.append(g)
				if price and price != r['price']:
					keys.append('price')
					values.append(price)

				if len(keys) > 0:
					tmp.append([type, money, num, g, price])
					app.logger.info(tmp[0])
					app.logger.info(tmp[1])
					list.append(tmp)

					update_transaction(r['id'], keys, values)
			app.logger.info(list)

			return jsonify({'success': True, 'data': list})
		except Exception as e:
			return jsonify({'success': False, 'error': str(e)})
		
	@app.route('/api/toggle_validity', methods=['POST'])
	def toggle_validity():
		data = request.json
		try:
			id = data.get('id')
			is_valid = data.get('is_valid')
			# app.logger.info(id, is_valid, 1 - is_valid)
			result = update_transaction(id, "is_valid", 1 - is_valid)
			return jsonify({'success': True, 'data': result})
		except Exception as e:
			return jsonify({'success': False, 'error': str(e)})

	@app.route('/api/import_csv', methods=['POST'])
	def import_csv_route():
		if 'file' not in request.files:
			return jsonify({'success': False, 'error': 'No file uploaded'})
		file = request.files['file']
		if file.filename == '':
			return jsonify({'success': False, 'error': 'No selected file'})
		if not file.filename.endswith('.csv'):
			return jsonify({'success': False, 'error': 'Only CSV files are supported'})
		try:
			if import_csv(file):
				return jsonify({'success': True, 'message': 'Data imported successfully'})
			else:
				return jsonify({'success': False, 'error': 'Import failed'})
		except Exception as e:
				return jsonify({'success': False, 'error': str(e)})

