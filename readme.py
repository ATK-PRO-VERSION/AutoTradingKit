
#pip install pypandoc_binary
import pypandoc


output = pypandoc.convert_file('README.md', 'docx', outputfile='readme.docx')