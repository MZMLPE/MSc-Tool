from fileinput import filename
import time
import xlsxwriter
from datetime import datetime
from .source import fuso_horario, main_source
from .log import WARNING, LOG


def threaded_task(app_context, folder, iqa_exec, db):
    tab_name = folder
    LOG(f'{iqa_exec}')
    app_context.push()
    result_name = '{}_{}_results_FV.xlsx'.format(folder, datetime.now().astimezone(fuso_horario).strftime('%d%m%Y_%H%M'))
    workbook = xlsxwriter.Workbook('app/results/{}'.format(result_name))
    folder_path = 'app/images/' + folder
    try:
        main_source(folder_path, workbook, tab_name)
        iqa_exec.progress = 100
        iqa_exec.result_filename = result_name
    except Exception as e:
        print(e)
    workbook.close()
    if iqa_exec.progress != 100:
        iqa_exec.progress = 0
    db.session.add(iqa_exec)
    db.session.commit()