#!/usr/bin/env python3
"""
股票学习笔记本 - Flask 主应用
"""

from flask import Flask, render_template, jsonify, request
from datetime import datetime, timedelta
import baostock as bs
import models
import config

app = Flask(__name__)
app.config.from_object(config)

# 初始化数据库
models.init_db()

# ============== 页面路由 ==============

@app.route('/')
def index():
    """主页仪表盘"""
    portfolios = models.get_all_portfolios()
    watchlists = models.get_all_watchlists()
    recent_observations = models.get_observations(limit=10)
    return render_template(
        'index.html',
        portfolios=portfolios,
        watchlists=watchlists,
        observations=recent_observations
    )

@app.route('/learning')
def learning():
    """指标学习页面"""
    notes = models.get_all_notes()
    return render_template('learning.html', notes=notes)

@app.route('/portfolio')
def portfolio():
    """持仓管理页面"""
    portfolios = models.get_all_portfolios()
    watchlists = models.get_all_watchlists()
    return render_template(
        'portfolio.html',
        portfolios=portfolios,
        watchlists=watchlists
    )

@app.route('/stock/<code>')
def stock_detail(code):
    """个股详情页面"""
    observations = models.get_observations(stock_code=code, limit=30)
    is_watching = models.is_in_watchlist(code)
    return render_template(
        'stock.html',
        stock_code=code,
        observations=observations,
        is_watching=is_watching
    )

# ============== API 路由 ==============

@app.route('/api/notes', methods=['GET'])
def api_get_notes():
    notes = models.get_all_notes()
    return jsonify({'success': True, 'data': notes})

@app.route('/api/notes', methods=['POST'])
def api_add_note():
    data = request.json
    note_id = models.add_note(
        indicator_name=data.get('indicator_name', ''),
        meaning=data.get('meaning', ''),
        usage=data.get('usage', '')
    )
    return jsonify({'success': True, 'id': note_id})

@app.route('/api/notes/<int:id>', methods=['PUT'])
def api_update_note(id):
    data = request.json
    models.update_note(
        id=id,
        indicator_name=data.get('indicator_name', ''),
        meaning=data.get('meaning', ''),
        usage=data.get('usage', '')
    )
    return jsonify({'success': True})

@app.route('/api/notes/<int:id>', methods=['DELETE'])
def api_delete_note(id):
    models.delete_note(id)
    return jsonify({'success': True})

@app.route('/api/portfolios', methods=['GET'])
def api_get_portfolios():
    portfolios = models.get_all_portfolios()
    return jsonify({'success': True, 'data': portfolios})

@app.route('/api/portfolios', methods=['POST'])
def api_add_portfolio():
    data = request.json
    models.add_portfolio(
        stock_code=data.get('stock_code', ''),
        stock_name=data.get('stock_name', ''),
        shares=data.get('shares', 0),
        cost_price=data.get('cost_price', 0),
        notes=data.get('notes', '')
    )
    return jsonify({'success': True})

@app.route('/api/portfolios/<int:id>', methods=['PUT'])
def api_update_portfolio(id):
    data = request.json
    models.update_portfolio(
        id=id,
        shares=data.get('shares', 0),
        cost_price=data.get('cost_price', 0),
        notes=data.get('notes', '')
    )
    return jsonify({'success': True})

@app.route('/api/portfolios/<int:id>', methods=['DELETE'])
def api_delete_portfolio(id):
    models.delete_portfolio(id)
    return jsonify({'success': True})

@app.route('/api/watchlists', methods=['GET'])
def api_get_watchlists():
    watchlists = models.get_all_watchlists()
    return jsonify({'success': True, 'data': watchlists})

@app.route('/api/watchlists', methods=['POST'])
def api_add_watchlist():
    data = request.json
    models.add_watchlist(
        stock_code=data.get('stock_code', ''),
        stock_name=data.get('stock_name', '')
    )
    return jsonify({'success': True})

@app.route('/api/watchlists/<int:id>', methods=['DELETE'])
def api_delete_watchlist(id):
    models.delete_watchlist(id)
    return jsonify({'success': True})

@app.route('/api/observations', methods=['GET'])
def api_get_observations():
    stock_code = request.args.get('stock_code')
    limit = int(request.args.get('limit', 50))
    observations = models.get_observations(stock_code=stock_code, limit=limit)
    return jsonify({'success': True, 'data': observations})

@app.route('/api/observations', methods=['POST'])
def api_add_observation():
    data = request.json
    models.add_observation(
        stock_code=data.get('stock_code', ''),
        observation_date=data.get('observation_date', ''),
        content=data.get('content', ''),
        tags=data.get('tags', '')
    )
    return jsonify({'success': True})

@app.route('/api/observations/<int:id>', methods=['PUT'])
def api_update_observation(id):
    data = request.json
    models.update_observation(
        id=id,
        content=data.get('content', ''),
        tags=data.get('tags', '')
    )
    return jsonify({'success': True})

@app.route('/api/observations/<int:id>', methods=['DELETE'])
def api_delete_observation(id):
    models.delete_observation(id)
    return jsonify({'success': True})

@app.route('/api/search')
def search_stock():
    """搜索股票 - 支持中文名称和代码搜索"""
    keyword = request.args.get('keyword', '')
    if not keyword:
        return jsonify({'data': []})

    results = []

    # 优先用 query_stock_basic 搜索中文名称
    rs = bs.query_stock_basic(code_name=keyword)
    while rs.next():
        row = rs.get_row_data()
        results.append({
            'code': row[1],
            'name': row[2],
            'type': row[4] if len(row) > 4 else ''
        })

    # 如果名称搜索无结果，且 keyword 是纯数字（疑似股票代码），尝试代码匹配
    # 注意：baostock 没有直接的代码搜索API，这里用模糊方式
    if not results and keyword.isdigit():
        # 尝试查询该代码的K线，如果能查到日期等信息，说明代码有效
        try:
            if keyword.startswith('6'):
                bs_code = 'sh.' + keyword
            else:
                bs_code = 'sz.' + keyword

            rs = bs.query_history_k_data_plus(
                bs_code, "date,code",
                start_date='2020-01-01', end_date='2020-01-02',
                frequency='d', adjustflag='2'
            )
            if rs.error_code == '0' and rs.next():
                row = rs.get_row_data()
                if len(row) >= 2:
                    results.append({
                        'code': keyword,
                        'name': row[1] if len(row) > 1 else keyword,  # K线数据不返回名称，用代码代替
                        'type': '1'
                    })
        except:
            pass

    return jsonify({'data': results[:20]})

@app.route('/api/kline')
def get_kline():
    code = request.args.get('code', '')
    period = request.args.get('period', 'd')
    adjust = request.args.get('adjust', '2')

    if not code:
        return jsonify({'error': 'code is required'}), 400

    # A 股格式转换
    if code.startswith('6'):
        bs_code = 'sh.' + code
    else:
        bs_code = 'sz.' + code

    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=365 * 3)).strftime('%Y-%m-%d')

    rs = bs.query_history_k_data_plus(
        bs_code,
        "date,open,high,low,close,volume",
        start_date=start_date,
        end_date=end_date,
        frequency=period,
        adjustflag=adjust
    )

    data = []
    while rs.next():
        row = rs.get_row_data()
        if row[1] and row[2] and row[3] and row[4]:
            data.append({
                'time': row[0].replace('-', ''),
                'date': row[0],
                'open': float(row[1]),
                'high': float(row[2]),
                'low': float(row[3]),
                'close': float(row[4]),
                'volume': int(row[5]) if row[5] else 0
            })

    return jsonify({'code': code, 'data': data})

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    return response

if __name__ == '__main__':
    # 登录 baostock
    bs.login()
    print("=" * 50)
    print("股票学习笔记本")
    print(f"访问地址: http://localhost:{config.PORT}")
    print("=" * 50)
    try:
        app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
    finally:
        bs.logout()
