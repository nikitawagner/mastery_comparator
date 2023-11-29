import web
import json

urls = (
    '/api', 'Index'
)

class Index:
    def POST(self):
        data = web.data()
        print(data)
        return json.dumps({"status": "success"})

if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()
