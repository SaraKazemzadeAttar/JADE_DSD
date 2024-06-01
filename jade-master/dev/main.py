from flask import Flask

app = Flask(__name__, 
            template_folder='../', 
            static_url_path='', 
            static_folder='../')
