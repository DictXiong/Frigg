from frigg import app
from frigg import var

@app.route('/')
def hello_world():
    return '<h1>Welcome to api.beardic.cn</h1>\n'


@app.route('/get-dfs-commit/')
def get_dfs_commit():
    dfs_commit = var.get_var('dfs-commit')
    return dfs_commit
    
