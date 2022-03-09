
from flask import (
    Flask,
    render_template,
    request,
    jsonify,
)
from hello import ph
from qlu_lib import book_in,nowtime,get_code,login,get_time,query
import requests

# render_template , 直接会在templates里边找xx.html文件

def get_args(headers,check_code):

    global session
    ## 先登录吧，再查询，避免登录的时间内座位被抢
    # 创建session对象
    
    # 手动输入验证码，或许可以用神经网络？有空再说吧
    login_info = login(session, headers, check_code)

    print(login_info.json()['msg'])

    if login_info.json()['status']==1:
        stu_info=login_info.json()['data']['list']
        print('{}的{}生\n{}，你好！'.format(stu_info['deptName'],stu_info['roleName'],stu_info['name']))

        # 获得access_token
        userid=login_info.json()['data']['list']['id']
        access_token=login_info.json()['data']['_hash_']['access_token']


        return stu_info['deptName'],stu_info['roleName'],stu_info['name'],userid,access_token





app = Flask(__name__)

@app.route("/")
def index():
    global session
    session = requests.Session()
    dt,hm=get_time()

    headers = dict(request.headers)
    code_path=get_code(session, headers)
    #code_path="https://cdn2.jianshu.io/assets/default_avatar/3-9a2bcc21a5d89e21dafc73b39dc5f582.jpg"

    #查询总的空座信息
    av_seat_list,un_seat_list=query(get_time())
    return render_template("index.html",dt=dt,hm=hm,code_path=code_path,av_seat_list=av_seat_list,un_seat_list=un_seat_list)




@app.route("/get")
def get():
    #data["url"] = request.url
    # get方法获取到的参数
    #name = request.args.get('name','zhangsan')

    #request.args
    #data["remote_addr"] = request.remote_addr

    return render_template("index.html")
    






@app.route("/post", methods=["POST"])
def post():
    global session,userid,access_token,addday

    headers = dict(request.headers)
    headers={ "Referer": "http://yuyue.lib.qlu.edu.cn","User-Agent":headers["User-Agent"]}



    data = {}
    # data["headers"] = headers
    # data["url"] = request.url
    data["form"] = request.form
   
    # data["remote_addr"] = request.remote_addr
    try:
        deptName,roleName,name,userid,access_token=get_args(headers,data["form"]["check_code"])
    except:
        dt,hm=nowtime()
        headers = dict(request.headers)
        code_path=get_code(session, headers)
        #查询总的空座信息
        av_seat_list,un_seat_list=query(get_time())
        return render_template("index.html",dt=dt,hm=hm,code_path=code_path,av_seat_list=av_seat_list,un_seat_list=un_seat_list)

    if data["form"]["day"]:
        addday=1
    else:
        addday=0

    dt,hm=get_time(addday)
    #查询总的空座信息
    av_seat_list,un_seat_list=query(get_time(addday))


    return render_template("area.html",deptName=deptName,roleName=roleName,name=name,av_seat_list=av_seat_list,un_seat_list=un_seat_list,dt=dt)




@app.route("/book", methods=["POST"])
def book():
    global session,userid,access_token,addday
    #更新headers
    headers = dict(request.headers)
    headers={ "Referer": "http://yuyue.lib.qlu.edu.cn","User-Agent":headers["User-Agent"]}
    
    area_dict = dict(request.form)
    area_id_list=area_dict['area_id_list']
    print("*"*50,area_id_list)
   
    
    book_result_status=book_in(session,area_id_list,userid,access_token,headers,addday)
    if book_result_status=="当前没有余座，继续检测":
        return render_template("bookresult.html",seat_name="OH NO!",book_result=book_result_status,pos_img_url="https://img1.baidu.com/it/u=3192771932,2132972328&fm=224&fmt=auto&gp=0.jpg",Refresh="true")
    else:
        seat_name,book_result,pos_img_url=book_result_status
        return render_template("bookresult.html",seat_name=seat_name,book_result=book_result,pos_img_url=pos_img_url,Refresh="False")

    
if __name__ == '__main__':
    app.run(debug=True) # 修改代码会立即生效
