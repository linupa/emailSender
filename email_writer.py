import os
import jinja2

class EmailWriter():
  def __init__(self):
    self.template_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "text")

  def Render(self, template_name, context):
    return jinja2.Environment(
      loader=jinja2.FileSystemLoader(self.template_path)
    ).get_template(template_name).render(context)

  def Write(self, template_name, content):
    return self.Render(template_name, { 'content' : content })

