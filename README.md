# 实验三 用户事件 号码分析与呼叫控制

本实验使用1001至1004四个虚拟用户，以事件驱动程序控制实验二的T/S交换网络。学生补全4个函数，完成摘机、收号、振铃、应答、通话及释放。实验70分、报告30分，PR自动触发评分。

[37人成绩实时跟踪表](https://github.com/jwentong/Experience03-Event-Analysis-Control/issues/1)显示完整姓名、学号和分项成绩。

## 教学材料
- [学生实验规范Word](materials/实验三_PRD_用户事件号码分析与呼叫控制.docx)
- [教师讲解PPT](materials/实验三_用户事件号码分析与呼叫控制_教师讲授版.pptx)
- [学生报告模板Word](materials/实验三_学生实验报告模板.docx)

## 1 环境与操作
在GitHub打开 https://github.com/jwentong/Experience03-Event-Analysis-Control ，Fork到自己账号，然后在PowerShell执行（将 YOUR_USERNAME 改为自己的GitHub用户名）：

```powershell
git clone https://github.com/YOUR_USERNAME/Experience03-Event-Analysis-Control.git
cd Experience03-Event-Analysis-Control
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

首次将REPORT_TEMPLATE.md复制为REPORT.md，将AI_LOG_TEMPLATE.md复制为AI_LOG.md。已有内容时不要覆盖。初始四个函数包含NotImplementedError，补全前测试失败属正常，不能删除测试来换取通过。

补全函数后运行：
```powershell
.\.venv\Scripts\python.exe -m pytest grading/test_hooks.py grading/test_numbering.py grading/test_control.py grading/test_timeouts.py -q
.\.venv\Scripts\python.exe -m src.run_experiment
.\.venv\Scripts\python.exe -m pytest grading student_tests -q
```

## 2 任务与接口
|任务|文件与函数|要求|
|---|---|---|
|摘挂机检测|src/hooks.py detect_hook_events(previous,current)|采样0为挂机，1为摘机；返回按号码排序的事件字典列表；相同采样不产生事件；非法值或用户集合不一致抛ValueError|
|号码分析|src/numbering.py analyze_number(digits,dial_plan,caller)|四位号码；合法前缀INCOMPLETE，完整合法号LOCAL，自己的号SELF_CALL，非法字符、无前缀或过长INVALID|
|呼叫控制|src/control.py handle_call_event(c,e,s,actions)|控制收号、忙、振铃、应答、释放；原地修改Call并通过服务调用真实话路|
|超时处理|src/timeouts.py handle_timeout(c,e,s,actions)|先校验token与timer_kind，再按状态处理超时；旧定时器直接忽略|

框架提供逻辑时钟、事件队列、Call、资源预留、实验二已实现的T/S模块和结果绘图。本实验学生不修改src/runtime.py、src/switch_*.py、grading和工作流；云端使用教师版本。可用AI辅助4个任务，但须自己验证。

## 3 模型与状态表
用户1001至1004分别绑定链路0的TS1至TS4。0为挂机，1为摘机。事件按(time_ms, sequence)依次处理，同一时间先入队先处理；不使用真实sleep或线程。收号总超时从摘机起5000ms，输入数字不重置；振铃超时从开始振铃起10000ms。

Call字段：call_id、caller、callee、state、digits、timer、timer_kind、reason。e字段：kind、user、value、call_id、token。OFFHOOK/ONHOOK由框架采样去重，DIGIT的value为一位字符，TIMEOUT的value为DIAL或RING。call_id和token用于定时器关联。

|当前状态|事件或条件|动作与下一状态|
|---|---|---|
|空闲用户|OFFHOOK|框架创建Call；发DIAL_TONE，arm DIAL 5000；COLLECTING|
|COLLECTING|主叫DIGIT且号码不完整|追加digits，STOP_DIAL_TONE，继续收号|
|COLLECTING|INVALID或SELF_CALL|finish对应原因，FAIL_TONE，ENDED|
|COLLECTING|完整号码但reserve失败|finish USER_BUSY，BUSY_TONE，ENDED|
|COLLECTING|完整号码且reserve成功|取消收号定时器，RINGING，arm RING 10000，RING和RINGBACK|
|RINGING|被叫OFFHOOK|取消定时器，activate成功则CONNECTED并STOP_RING、CONNECT；失败finish NETWORK_BUSY并FAIL_TONE|
|活动呼叫|ONHOOK|finish NORMAL_CLEAR（通话中）或CALLER_CANCEL（通话前），RELEASE，ENDED|
|COLLECTING|有效DIAL超时|finish DIAL_TIMEOUT，FAIL_TONE，ENDED|
|RINGING|有效RING超时|finish NO_ANSWER，STOP_RING、FAIL_TONE，ENDED|
|任何状态|旧token或不匹配类型的超时|保持状态、话路和资源不变|

框架finish自动释放双向话路、取消定时器、清除归属。仍摘机的相关用户进入WAIT_ONHOOK集合，只在真实ONHOOK后变为空闲；不能直接把hooks改为0。回铃音只表示正在呼叫，应答后activate成功才算接通。

## 4 服务调用与约束
- s.arm(c,kind,delay)：增加timer代次并排入超时事件。s.cancel(c)：使旧token失效。
- s.reserve(c,number)：被叫挂机、未占用且不在等待挂机集合时，预留被叫并设置callee；否则False。
- s.activate(c)：调用实验二connect_pair；成功建立双向T/S映射才返回True。
- s.finish(c,reason)：释放、取消定时器、写入结束原因并处理未挂机用户。
- s.action(actions,name,**fields)：追加动作字典；动作名按状态表。
- 控制函数原地更新，无返回值要求。ENDED状态与无关事件保持不变；DIGIT仅接受主叫在COLLECTING时输入。

## 5 预期结果与验收
正常示例：0ms主叫摘机，100/200/300/400ms拨1/0/0/2，800ms被叫应答，1000ms主叫挂机。状态为COLLECTING→RINGING→CONNECTED→ENDED。1002仍摘机，应等待挂机。帧0的TS1=3、TS2=6，应答后输出TS1=6、TS2=3，输出帧比输入帧晚一帧。释放后相关输出为0xD5。

无人接听示例：400ms开始振铃，到10400ms结束为NO_ANSWER；5000ms到达的旧收号超时必须忽略。正确日志应保留该事件但前后状态相同。

运行生成三个文件：
- results/call_sequence.png：正常释放和无人接听两条状态时序图。
- results/call_events.jsonl：逐行记录scenario、time_ms、event、call_id、before、after、actions、reason。
- results/scenario_results.json：scenarios的12个passed均为true，passed=12、total=12。

12场景：双向接通；主叫挂机；被叫挂机；号码错误；自呼；被叫忙；收号超时；无人接听；振铃取消；旧定时器；重复采样；释放后复用。其他公开测试还检查网络拒绝、配置驱动号码和同时间事件顺序。结果图形相似不等于代码正确，需逐条检查日志和实际字节。

## 6 GitHub提交
1. 在student_tests/test_my_case.py写至少一个自拟测试，实际调用任务函数或Exchange并含有效assert。
2. 填写REPORT.md四节：原理与手算、结果分析、反例与验证、局限。填写AI_LOG.md三节：需求、建议与采纳、验证证据。未用AI如实记录独立完成过程。
3. 生成本人结果，运行测试，然后提交：
```powershell
git add src/hooks.py src/numbering.py src/control.py src/timeouts.py REPORT.md AI_LOG.md student_tests/
git add -f results/call_sequence.png results/call_events.jsonl results/scenario_results.json
git commit -m "完成实验三呼叫控制与验证"
git push origin main
```
4. 在自己Fork点击Contribute / Open pull request，base选择教师仓库main，head选择自己Fork的main。PR标题严格填写：现代交换实验03-本人姓名-完整学号。
5. 姓名与完整学号须与班级名单一致。只Push到Fork不会触发教师评分，必须创建PR。后续在同一分支补交即可自动重评；不用重复创建PR。
6. 查看PR机器人评论、教师仓库Actions评分日志及成绩表。工作流绿色表示评分流程运行成功，不等于满分。身份未匹配时修改PR标题会自动重新关联。
7. Word报告可随PR上传，但自动评分读取REPORT.md与AI_LOG.md，必须同步内容。

## 7 评分
|部分|项目|分值|
|---|---|---:|
|实验|摘挂机检测|10|
|实验|号码分析|10|
|实验|呼叫控制|25|
|实验|超时处理|15|
|实验|集成场景与结果文件|5|
|实验|自拟测试|5|
|报告|原理与手算|6|
|报告|结果分析|6|
|报告|反例与验证|6|
|报告|局限|6|
|报告|AI记录|6|
|总分|实验70加报告30|100|

实验各项按通过用例数比例给分。报告结构与完整性自动检查：REPORT.md至少300字符；前3节去空白各至少60字符，局限至少40字符。AI_LOG.md至少120字符，3节各去空白至少20字符；不得保留TODO或待填写。报告分不等同教师对论述质量的评价。代码和报告中不要写口令、Token或无关个人信息。

## 8 课堂安排
0–15分钟理解模型与手算；15–35分钟摘挂机及号码分析；35–75分钟呼叫控制；75–95分钟超时与异常；95–110分钟运行场景、自拟测试；110–120分钟提交PR和查看反馈。报告分析可课后完善。
