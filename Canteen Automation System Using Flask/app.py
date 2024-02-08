from flask import Flask, render_template, request, redirect, url_for,session,flash
import pymysql
from datetime import datetime
import uuid

cart=[]
app = Flask(__name__)
app.secret_key = "Canteen&Co"



@app.route('/')
def index():
    return render_template('index.html')


@app.route('/customerlogin',methods=['POST'])
def customerlogin():
    con = pymysql.connect(host='localhost',user='root',password='root',db='vthsem')
    login_id = request.form['login_id']
    password = request.form['password']
    usertype = 'customer'
    cur = con.cursor()
    sql = "SELECT COUNT(*) FROM login_data WHERE username = %s and password = %s and usertype = %s"
    val = (login_id,password,usertype)
    cur.execute(sql,val)
    data = cur.fetchall()
    cur.close()
    con.close()
    for item in data:
        if(item[0] == 1):
            session['username'] = login_id
            return render_template('customerindex.html')
        else:
            return render_template('unsuccessful.html')


@app.route('/adminlogin',methods=['POST'])
def adminlogin():
    con = pymysql.connect(host='localhost',user='root',password='root',db='vthsem')
    login_id = request.form['login_id']
    password = request.form['password']
    usertype = 'admin'
    cur = con.cursor()
    sql = "SELECT COUNT(*) FROM login_data WHERE username = %s and password = %s and usertype = %s"
    val = (login_id,password,usertype)
    cur.execute(sql,val)
    data = cur.fetchall()
    cur.close()
    con.close()
    for item in data:
        if(item[0] == 1):
            session['username'] = login_id
            return render_template('adminindex.html')
        else:
            
            return render_template('unsuccessful.html')
@app.route('/logout')
def logout():
    session.pop('username',None)
    return render_template('index.html')            


@app.route('/add-products',methods = ['POST'])
def addProducts():
    con = pymysql.connect(host='localhost',user='root',password='root',db='vthsem')
    productId = int(request.form['productId'])
    productName = request.form['productName']
    producturl = request.form['producturl']
    price = float(request.form['price'])
    category = request.form.get('category')
    status = request.form.get('Status')
    cur = con.cursor()
    try:
        print('Executing SQL')
        sql = "INSERT INTO item(id,img,name,price,category,status) VALUES (%s, %s,%s,%s,%s,%s)"
        val = (productId,producturl,productName,price,category,status)
        cur.execute(sql, val)
    except pymysql.InternalError as error:
        code, message = error.args
        print(">>>>>>>>>>>>>" +  str(code) +  str(message))
        cur.close()
        con.close()
        return render_template('unsuccessful.html')
    con.commit()
    cur.close()
    con.close()
    return render_template('successful.html')

@app.route('/form-add-products')
def formaddproducts():
    return render_template('add_item.html')


@app.route('/remove-product',methods = ['POST'])
def removeProduct():
    con = pymysql.connect(host='localhost',user='root',password='root',db='vthsem')
    productId = int(request.form['productId'])
    cur = con.cursor()
    try:
        sql = 'DELETE FROM item WHERE id = %s'
        val = (productId,)
        cur.execute(sql,val)
    except pymysql.InternalError as error:
        code, message = error.args
        print(">>>>>>>>>>>>>" +  str(code) +  str(message))
        cur.close()
        con.close()
        return render_template('unsuccessful.html')
    con.commit()
    cur.close()
    con.close()
    return render_template('successful.html')



@app.route('/form-remove-products')
def formremoveproducts():
    return render_template('remove_item.html')


@app.route('/add-to-cart',methods=['POST'])
def addtocart():
    item_id=int(request.form['item_id'])
    quantity=int(request.form['quantity'])
    category=request.form['category']
    con = pymysql.connect(host='localhost',user='root',password='root',db='vthsem')
    cur = con.cursor()
    sql="SELECT * FROM item WHERE id = %s"
    val = (item_id,)
    cur.execute(sql,val)
    data = cur.fetchone()
    sql="SELECT * FROM cart WHERE id = %s"
    val = (item_id,)
    cur.execute(sql,val)
    item = cur.fetchone()
    if item:
        q = item[5] + quantity
        st1 = data[4] * q
        sql = "UPDATE cart SET quantity = %s,subtotal = %s WHERE id = %s"
        val = (q,st1,item_id)
        cur.execute(sql,val)
    else:
        st = data[4] * quantity
        sql = "INSERT INTO cart (id,name,img,price,quantity,subtotal) VALUES(%s,%s,%s,%s,%s,%s)"
        val = (item_id,data[3],data[2],data[4],quantity,st)
        cur.execute(sql,val)
    con.commit()
    cur.close()
    con.close()
    flash(f'Add { quantity }  { data[3] } to the cart','success') 
    if category == 'tiffin':
        return redirect(url_for('tiffinmenu'))
    if category == 'maincourse':
        return redirect(url_for('maincoursemenu'))
    if category == 'snack':
        return redirect(url_for('snackmenu'))
    if category == 'jucie':
        return redirect(url_for('juicemenu'))
    
@app.route('/view_cart')
def view_cart():
    con = pymysql.connect(host='localhost',user='root',password='root',db='vthsem')
    cur = con.cursor()
    tp=0
    cur.execute("SELECT * FROM cart")
    cart_items = cur.fetchall()
    for i in cart_items:
        tp+=i[6]
    return render_template('view_cart.html',cart_items=cart_items,tp=tp)


@app.route('/remove_from_cart',methods=['POST'])
def remove_from_cart():
    item_id=int(request.form['item_id'])
    tp=0
    con = pymysql.connect(host='localhost',user='root',password='root',db='vthsem')
    cur = con.cursor()
    sql = "DELETE FROM cart WHERE id = %s"
    val = (item_id,)
    cur.execute(sql,val)
    con.commit()
    cur.execute("SELECT * FROM cart")
    cart_items = cur.fetchall()
    for i in cart_items:
        tp+=i[6]
    con.commit()
    cur.close()
    con.close()
    return render_template('view_cart.html',cart_items=cart_items,tp=tp)


@app.route('/place_order', methods=['POST'])
def place_order():
    tp=request.form['tp']
    con = pymysql.connect(host='localhost',user='root',password='root',db='vthsem')
    cur = con.cursor()
    userid = session.get('username')
    date = datetime.now().date()
    status = 'pending'
    cur.execute('SELECT * FROM cart')
    cart_items = cur.fetchall()
    for item in cart_items:
        d=str(uuid.uuid4())
        order_id=d[:6]
        cur.execute('INSERT INTO order_item (user_id,order_id,name,amount,date, quantity,status) VALUES (%s, %s, %s, %s, %s, %s, %s)',
                       (userid, order_id, item[2], item[6], date, item[5], status))


    for item in cart_items:
        cur.execute('DELETE FROM cart where id = %s',(item[1],))

    
    con.commit()

    flash('Order placed successfully!', 'success')
    return redirect(url_for('customerindex'))
    return render_template('customerindex.html')


@app.route('/view_order')
def view_order():
    userid = session.get('username')
    con = pymysql.connect(host='localhost',user='root',password='root',db='vthsem')
    cur = con.cursor()
    cur.execute('SELECT * FROM order_item where user_id = %s order by id DESC' ,(userid,))
    items = cur.fetchall()
    cur.close()
    con.close()
    return render_template('customerorder.html',items=items)


@app.route('/update_status',methods=['POST'])
def status_update():
    order_id = request.form.get('order_id')
    new_status = request.form.get('new_status')
    con = pymysql.connect(host='localhost',user='root',password='root',db='vthsem')
    cur = con.cursor()
    sql = "UPDATE order_item SET status = %s where order_id = %s AND status!= 'delivered'"
    val = (new_status,order_id)
    cur.execute(sql,val)
    data = cur.fetchall()
    con.commit()
    cur.close()
    con.close()
    return redirect(url_for('admin_view_order'))


@app.route('/admin_view_order')
def admin_view_order():
    date = datetime.now().date()
    userid = session.get('username')

    con = pymysql.connect(host='localhost',user='root',password='root',db='vthsem')
    cur = con.cursor()
    
    cur.execute('SELECT * FROM order_item where date = %s AND status != "delivered" AND status !="rejected" order by id DESC',(date,))
    data = cur.fetchall()
    cur.close()
    con.close()
    return render_template('adminorder.html',data=data)


@app.route('/view_all_order')
def view_all_order():
    con = pymysql.connect(host='localhost',user='root',password='root',db='vthsem')
    cur = con.cursor()
    cur.execute('SELECT * FROM order_item order by id DESC')
    data = cur.fetchall()
    return render_template('allorder.html',data=data)


@app.route('/customer-index')
def customerindex():
    return render_template('customerindex.html')


@app.route('/adminindex')
def adminindex():
    return render_template('adminindex.html')


@app.route('/update-products',methods = ['POST'])
def updateProducts():
    con = pymysql.connect(host='localhost',user='root',password='root',db='vthsem')
    productId = int(request.form['productId'])
    productName = request.form['productName']
    price = int(request.form['price'])
    status = request.form['Status']
    cur = con.cursor()
    try:
        print('Executing SQL')
        sql = "UPDATE item SET  name=%s, price=%s, status=%s WHERE id=%s"
        val = (productName,price,status,productId)
        cur.execute(sql, val)
    except pymysql.InternalError as error:
        code, message = error.args
        print(">>>>>>>>>>>>>" +  str(code) +  str(message))
        cur.close()
        con.close()
        return render_template('unsuccessful.html')
    con.commit()
    cur.close()
    con.close()
    return render_template('successful.html')


@app.route('/form-update-products')
def formupdateproducts():
    return render_template('update_item.html')



@app.route('/admin-menu')
def adminmenu():
    con = pymysql.connect(host='localhost',user='root',password='root',db='vthsem')
    cur=con.cursor()
    sql="SELECT img,name,id,price FROM item WHERE status='available'"
    cur.execute(sql)
    adata = cur.fetchall()
    sql="SELECT img,name,id,price FROM item WHERE status='notavailable'"
    cur.execute(sql)
    nadata = cur.fetchall()
    cur.close()
    con.close()
    return render_template('adminmenu.html',adata=adata,nadata=nadata)

@app.route('/tiffinmenu')
def tiffinmenu():
    con = pymysql.connect(host='localhost',user='root',password='root',db='vthsem')
    cur=con.cursor()
    sql="SELECT img,name,id,price,category FROM item WHERE status='available' and category='tiffin'"
    cur.execute(sql)
    data = cur.fetchall()
    cur.close()
    con.close()
    return render_template('tiffinmenu.html',data=data)



@app.route('/maincoursemenu')
def maincoursemenu():
    con = pymysql.connect(host='localhost',user='root',password='root',db='vthsem')
    cur=con.cursor()
    sql="SELECT img,name,id,price,category FROM item WHERE status='available' and category='maincourse'"
    cur.execute(sql)
    data = cur.fetchall()
    cur.close()
    con.close()
    return render_template('maincoursemenu.html',data=data)


@app.route('/snackmenu')
def snackmenu():
    con = pymysql.connect(host='localhost',user='root',password='root',db='vthsem')
    cur=con.cursor()
    sql="SELECT img,name,id,price,category FROM item WHERE status='available' and category='snack'"
    cur.execute(sql)
    data = cur.fetchall()
    cur.close()
    con.close()
    return render_template('snackmenu.html',data=data)

@app.route('/juicemenu')
def juicemenu():
    con = pymysql.connect(host='localhost',user='root',password='root',db='vthsem')
    cur=con.cursor()
    sql="SELECT img,name,id,price,category FROM item WHERE status='available' and category='jucie'"
    cur.execute(sql)
    data = cur.fetchall()
    cur.close()
    con.close()
    return render_template('juicemenu.html',data=data)


if __name__ == '__main__':
    app.run(debug=True)
