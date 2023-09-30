import win32com.client as win32

# Inicia o Outlookdd

outlook = win32.Dispatch('outlook.application')

email = outlook.CreateItem(0)

email.To = 'enviar@para.com.br'  # para

email.Subject = 'Teste'  # assunto

anexo = "caminho//arquivo.tipo"  # caminho

email.Attachments.Add(anexo)

# texto

conteudo = f""" Bom dia """

# estilização

css = "<style> .email p { font-size: 20px; font-family: Arial, Helvetica, sans-serif;}</style>"

# Estrutura HTML

email.HTMLBody = f"""<head> <meta charset="utf-8"> <meta http-equiv="X-UA-Compatible" content="IE=edge"> <meta name="viewport" content="width=device-width, initial-scale=1"> {css} </head> <body> <section class="email"> {conteudo} </section> </body> </html>"""
email.Send()
