import web
import json

urls = (
    '/api', 'Index'
)

class Index:
    def OPTIONS(self):
        # OPTIONS method is used to handle CORS preflight requests
        # You should include this if your frontend makes use of preflight requests
        web.header('Access-Control-Allow-Origin', '*')
        web.header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        web.header('Access-Control-Allow-Headers', 'Content-Type')
        return
    
    def POST(self):
        web.header('Access-Control-Allow-Origin', '*')  
        data = web.data()
        print(data)
        return json.dumps({"status": "success"})

if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()
