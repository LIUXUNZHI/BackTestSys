import pymysql

Trading_CONN = pymysql.connect(
    host='10.0.0.111',
    user='root',
    passwd='RH123@fi',
    db='maintain',
    charset='utf8',
    autocommit=1
)
