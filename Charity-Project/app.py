from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('donation_form.html')

@app.route('/donate', methods=['POST'])
def donate():
    name = request.form['name']
    amount = request.form['amount']
    # اینجا می‌توانید کد مربوط به ذخیره اطلاعات کمک را اضافه کنید
    return f"متشکریم {name}، شما {amount} تومان کمک کردید!"

if __name__ == '__main__':
    app.run(debug=True)
