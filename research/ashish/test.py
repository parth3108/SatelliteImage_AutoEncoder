from flask import Flask, request, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/compress', methods=['POST'])
def compress():
    method = request.form['method']
    if method == 'JPEG2000':
        # Compress with JPEG2000
        pass
    elif method == 'Pillow-SIMD':
        # Compress with Pillow-SIMD
        pass
    return "Image Compressed Successfully!"

if __name__ == '__main__':
    app.run(debug=True)
