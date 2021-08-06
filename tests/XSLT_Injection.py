from lxml import etree

xml = StringIO.StringIO(request.POST['xml'])
xslt = StringIO.StringIO(request.POST['xslt'])

xslt_root = etree.XML(xslt)
transform = etree.XSLT(xslt_root)
result_tree = transform(xml)
return render_to_response(template_name, {'result': etree.tostring(result_tree)})