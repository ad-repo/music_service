from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9111)
    #app.run(host='192.168.0.102', port=9111)
