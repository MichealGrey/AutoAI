import win32com.client

def ControlSchedule(logger,state):
    '''state:[True]开启,[False]关闭'''
    TASK_ENUM_HIDDEN = 1
    isOpen = ''
    TASK_STATE = {0: 'Unknown',
                1: 'Disabled',
                2: 'Queued',
                3: 'Ready',
                4: 'Running'}

    scheduler = win32com.client.Dispatch('Schedule.Service')
    scheduler.Connect()

    n = 0
    folders = [scheduler.GetFolder('\\')]
    while folders:
        folder = folders.pop(0)
        folders += list(folder.GetFolders(0))
        tasks = list(folder.GetTasks(TASK_ENUM_HIDDEN))
        n += len(tasks)
        for task in tasks:
            # print('Task: %s' % task.Definition.Triggers[0].StartBoundary)
            settings = task.Definition.Settings
            if task.Path == r'\定时出库' and state == False:
                task.Stop(0)
                task.Enabled = state
                isOpen = 'Close'
                break

            if task.Path == r'\定时出库' and state == True:
                task.Enabled = state
                isOpen = 'Open'
                break
    
    if isOpen == 'Close':
        logger.info("计划任务：定时出库关闭并禁用")
    if isOpen == 'Open':
        logger.info("计划任务：定时出库启用")
        # task.Enabled = True # True表示啟用，False表示停用
        # task.Run('VT_NULL')
        # status = task.Stop(0) # 0表示立即停止
        # print('Stop status: %s\n' % status)
        
