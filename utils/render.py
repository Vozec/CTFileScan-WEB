from flask import render_template
from pwnlib.util.safeeval import expr as Save_Eval
from os import path

from utils.utils_func import ConvertResult,Timestamp2date,Size,find

def Result_manager(result,CONFIG):
	config 	 = ConvertResult(result)
	res_scan = Save_Eval(config['result'])
	content  = Get_Content(res_scan,config,CONFIG)

	return render_template('result.html',
		filename=config['filename'].replace('_original',''),
		size=config['size'],
		magic=config['magic'],
		upload_count=config['upload_count'],
		first_up=Timestamp2date(config['first_up']),
		last_up=Timestamp2date(config['last_up']),
		passwords=str(config['all_password']),
		flags=str(config['flag'])
	).replace(r'7e84437f35fa24b76c7898ca87f636d0',content)

def Get_Content(results,config,CONFIG):
	content = ''
	models  = Load_all_model()
	id_ = 0
	for module,res in results.items():
		if (type(res['path']) == str):
			html,id_ = HTML_1(id_,models,module,res,config,CONFIG)	
			content += html
		else:
			html,id_ = HTML_2(id_,models,module,res,config,CONFIG)	
			content += html
	return content


def HTML_2(id_mod,models,module,res,config,CONFIG):
	def preview_possible(res):
		txt = []
		for x in res['path']:
			for ext in ['json','txt']:
				if x.endswith(ext):
					txt.append(x)
					break
		return len(txt) == len(res['content'])
	content = ''
	id_ 	= id_mod
	preview_id = 0
	preview_on = preview_possible(res)
	for i in range(len(res['path'])):
		file = res['path'][i]
		if not preview_on:
			content += render_template(models['multi_nopreview'],
				content='%s %s'%(Name(file),Get_size(file,config,CONFIG)),
				link=file,
				id = id_)
			id_ += 1
		else:
			cnt = res['content'][preview_id] if preview_id < len(res['content']) else ''

			template = models['multi_preview_text']
			if isimage(file):
				template = models['multi_preview_img']
				id_ += 1
			elif cnt != '':
				template = models['multi_preview_text']
				id_ += 1
				preview_id += 1

			content += render_template(template,
					content='%s %s'%(Name(file),Get_size(file,config,CONFIG)),
					link=file,
					id = id_,
					preview=cnt)

	return render_template('result/multi_base.html',
		module=module,
		content='%s files'%len(res['path']),
		id = id_mod,
	).replace(r'7e84437f35fa24b76c7898ca87f636d0',content),id_

def HTML_1(id_,models,module,res,config,CONFIG):
	template = models['simple_nopreview']
	if isimage(res['path']):
		template = models['simple_preview_img']
		id_ += 1
	elif res['content'] != '':
		template = models['simple_preview_text']
		id_ += 1

	return render_template(template,
			module=module,
			content='%s %s'%(Name(res['path']),Get_size(res['path'],config,CONFIG)),
			link=res['path'],
			id = id_,
			preview=res['content']), id_

def Load_all_model():
	return {
		'simple_nopreview' : 'result/simple_nopreview.html',
		'simple_preview_text' : 'result/simple_preview_text.html',
		'simple_preview_img' : 'result/simple_preview_img.html',
		'multi_nopreview' : 'result/multi_nopreview.html',
		'multi_preview_img' : 'result/multi_preview_img.html',
		'multi_preview_text' : 'result/multi_preview_text.html',
	}

def isimage(file):
	for x in ['png','jpeg','jpg','bmp','gif']:
		if file.endswith(x):
			return True
	return False

def Name(file):
	return path.basename(file)

def Path(file):
	return path.dirname(file)

def Get_size(file,config,CONFIG):
	directory   = '%s/%s'%(CONFIG['dwnl_dir'],config['hash'])
	found_dir,found_file = find(Name(file),directory)
	if found_file != '':
		return '(%s)'%Size('%s/%s'%(found_dir,found_file))
	return ''