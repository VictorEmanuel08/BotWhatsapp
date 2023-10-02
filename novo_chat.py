import asyncio
import time
from datetime import date, datetime
from playwright.async_api import Playwright, async_playwright, expect
import mysql.connector
# ----------------------------------------------------------------------
import acesso as cx
import status as st
import mensagens as msg


async def run(playwright: Playwright) -> None:
    browser = await playwright.chromium.launch(headless=False)
    context = await browser.new_context()

    # Open new page
    page = await context.new_page()

    # Indo para https://web.whatsapp.com/
    await page.goto("https://web.whatsapp.com/")

    # No Whatsapp
    # clica no botão de opções
    await page.locator('//*[@id="side"]/div[1]/div/button/div/span').click()
    # apenas não lidas selecionadas
    await page.locator('//*[@id="app"]/div/span[4]/div/ul/div/li[1]/div/div[2]').click()

    while page:  # Mantendo persistente
        time.sleep(5)  # espera 5s
        data_atual = date.today()  # data atual (hoje)
        try:
            await page.get_by_test_id("icon-unread-count").nth(0).click()
            time.sleep(3)  # espera 3s

            # Saber se a conta é pessoal ou comercial
            nome_real = "~"
            telefone = await page.locator('//*[@id="main"]/header/div[2]/div/div/span').all_text_contents()
            print(telefone)

            # ajustando telefone
            tel = telefone[0].replace(" ", "")  # Retirando o espaço vazio
            t = tel.replace("-", "")  # Retirando o espaço -

            # ajustado
            fone = t.replace("+", "")  # Retirando o espaço +
            print(fone)

            # ober ultima mensagem da conversa
            time.sleep(3)
            for i in range(1):
                count = await page.get_by_test_id("msg-container").count()
                # faz uma lista com as ultimsa 17 mensagens
                a = await page.get_by_test_id("msg-container").all_text_contents()

            print(a)
            texto = a[-1]  # extrai a ultima mensagem
            print(texto)
            # elimina os dados de horário (10 caracteres depois do texto)
            ultimamensagem = str(texto[0:-10])
            print(ultimamensagem)

            # ------------------------------------------------------

            # Aqui podemos colocar dados ao banco
            # Abrir conexão com o banco de dados para inserie dados, conversas
            conectar = mysql.connector.connect(
                host=cx.h, database=cx.d, user=cx.u, password=cx.p)
            dados = '('+'\''+str(nome_real)+'\''+',\''+str(fone) + \
                '\''+',\''+str(ultimamensagem)+'\''+')'
            comando = "INSERT INTO `atendimento` (`apoio`, `Telefone`,`Mensagem`) VALUES"
            sql = comando + dados

            print(sql)

            # popular dados
            try:
                cursor = conectar.cursor()
                # executar comando
                cursor.execute(sql)
                conectar.commit()
                conectar.close()
            except:
                conectar.close()

            # ------------------------------------------------------

            # Abrir conexão com o banco de dados para inserir dados, atendimento
            conectar = mysql.connector.connect(
                host=cx.h, database=cx.d, user=cx.u, password=cx.p)
            dados = '('+'\''+str(nome_real)+'\''+',\''+str(fone) + '\''+',\'' + \
                str(data_atual)+str(fone)+'\''+',\''+str('Aguardando')+'\''+')'
            comando = "INSERT INTO `atendimento` (`apoio`, `Telefone`,`ID`,`Status`) VALUES"
            sql = comando + dados

            print(sql)

            # popular dados
            try:
                cursor = conectar.cursor()
                # executar comando
                cursor.execute(sql)
                conectar.commit()
                conectar.close()
            except:
                conectar.close()

            # ------------------------------------------------------

            # Abrimos conexão com o banco de dados:
            conexao = mysql.connector.connect(
                host=cx.h, database=cx.d, user=cx.u, password=cx.p)
            # Cria um cursor:
            cursor = conexao.cursor()
            # Executa o comando:
            select = cursor.execute(
                "SELECT `apoio`,`Telefone`,`ID`,`Status`,`Nome_completo`,`Data_nascimento`,`CPF`,`email` from `processo_atendimento`")
            # Recupera o comando:
            resultado = cursor.fetchall()
            # Finaliza a conexão:
            conexao.close()

            for resultados in resultado:
                resultados[0]  # nome
                resultados[1]  # telefone
                resultados[2]  # ID
                resultados[3]  # Status
                resultados[4]  # Nome_completo
                resultados[5]  # Data_nascimento
                resultados[6]  # CPF
                resultados[7]  # Email

                # determinar a mensagem
                if str(resultados[3]) == 'Aguardando':  # saudação
                    mensagem = msg.menu_saudacao
                    atualizar1 = st.esperando_opcao
                    atualizar2 = ultimamensagem
                    atualizar3 = ultimamensagem

                    campo1 = 'Status'
                    campo2 = 'apoio'
                    campo3 = 'apoio2'

                # pergunta nome
                elif str(resultados[3]) == str(st.esperando_opcao) and str(ultimamensagem) == '1':
                    mensagem = msg.nomecompleto
                    atualizar1 = st.nome_completo
                    atualizar2 = ultimamensagem
                    atualizar3 = 'EP'

                    campo1 = 'Status'
                    campo2 = 'apoio'
                    campo3 = 'produto'

                # pergunta nome
                elif str(resultados[3]) == str(st.esperando_opcao) and str(ultimamensagem) == '3':
                    mensagem = msg.nomecompleto
                    atualizar1 = st.nome_completo
                    atualizar2 = ultimamensagem
                    atualizar3 = 'Outros'

                    campo1 = 'Status'
                    campo2 = 'apoio'
                    campo3 = 'produto'

                # pergunta data de nascimento e armazena nome
                elif str(resultados[3]) == str(st.nome_completo):
                    mensagem = msg.datanascimento
                    atualizar1 = st.data_nascimento
                    atualizar2 = ultimamensagem
                    atualizar3 = 'Outros'

                    campo1 = 'Status'
                    campo2 = 'Nome_completo'
                    campo3 = 'apoio2'

                # pergunta email e armazena data de nascimento
                elif str(resultados[3]) == str(st.data_nascimento):
                    mensagem = msg.emails
                    atualizar1 = st.email
                    atualizar2 = ultimamensagem

                    try:
                        dt: datetime.strptime(ultimamensagem, "%d/5m/%Y")
                    except:
                        dt = "200-01-01"
                    campo1 = 'Status'
                    campo2 = 'Data_nascimento'
                    campo3 = 'Data_nascimento_banco'

                # pergunta cpf e armazena email
                elif str(resultados[3]) == str(st.email):
                    mensagem = msg.CPF
                    atualizar1 = st.CPF_
                    atualizar2 = ultimamensagem
                    atualizar3 = ultimamensagem

                    campo1 = 'Status'
                    campo2 = 'email'
                    campo3 = 'apoio2'

                # confirma se todos os dados estão corretos e armazena CPF
                elif str(resultados[3]) == str(st.CPF):
                    mensagem = str(str(msg.Confirmar)+'\nNome completo: ' + str(resultados[4]) +
                                   '\n'+'Data de nascimento: ' + str(resultados[5]) +
                                   '\n'+'E-mail: ' + str(resultados[7]) +
                                   '\n'+'CPF: ' + str(resultados[6]))
                    atualizar1 = st.confirmando
                    atualizar2 = ultimamensagem
                    atualizar3 = ultimamensagem

                    campo1 = 'Status'
                    campo2 = 'CPF'
                    campo3 = 'apoio2'

                # se confirmado, agradece
                elif str(resultados[3]) == str(st.confirmando) and str(ultimamensagem) == '3':
                    mensagem = str(msg.Obrigado)
                    atualizar1 = st.finalizado
                    atualizar2 = ultimamensagem
                    atualizar3 = ultimamensagem

                    campo1 = 'Status'
                    campo2 = 'Confirmado'
                    campo3 = 'apoio2'

                # se houver algo incorreto, refaz a operação retornando
                elif str(resultados[3]) == str(st.confirmando) and str(ultimamensagem) == '4':
                    mensagem = str(msg.refazer)
                    atualizar1 = st.nome_completo
                    atualizar2 = ultimamensagem
                    atualizar3 = ultimamensagem

                    campo1 = 'Status'
                    campo2 = 'Confirmado'
                    campo3 = 'apoio2'

                # atendimento receptivo, pergunta dados e motivo
                elif str(resultados[3]) == str(st.esperando_opcao) and str(ultimamensagem) == '2':
                    mensagem = str(msg.atendimento)
                    atualizar1 = st.atendimento_finaliza
                    atualizar2 = ultimamensagem
                    atualizar3 = ultimamensagem

                    campo1 = 'Status'
                    campo2 = 'atendimento'
                    campo3 = 'apoio2'

                # finaliza atendimento e armazaena dados
                elif str(resultados[3]) == str(st.atendimento_finaliza):
                    mensagem = str(msg.atendimento)
                    atualizar1 = st.finalizado
                    atualizar2 = ultimamensagem
                    atualizar3 = ultimamensagem

                    campo1 = 'Status'
                    campo2 = 'atendimento'
                    campo3 = 'apoio2'

                # Se em qualquer momento for digitado REINICIAR, o atendimento é reiniciado
                # upper para deixar tudo em maiúsculo
                elif str(ultimamensagem).upper() == 'REINICIAR' or str(ultimamensagem).upper() == 'REINICIA':
                    mensagem = str(msg.menu_saudacao)
                    atualizar1 = st.esperando_saudacao
                    atualizar2 = ultimamensagem
                    atualizar3 = ultimamensagem

                    campo1 = 'Status'
                    campo2 = 'atendimento'
                    campo3 = 'apoio2'

                # Após finalizar o atendimento, se uma pergunta for realizada, questiona se deseja reiniciar
                elif str(resultados[3]) == str(st.finalizado):
                    mensagem = str(msg.reiniciar)
                    atualizar1 = '1'

                # ---------------------------------------------------------------------------------------------------------------------

                # Click p
                # digitando mensagem
                await page.locator("p").fill("Olá, " + str(mensagem))
                # Press Enter
                # enviando mensagem
                await page.locator("[data-testid=\"conversation-compose-box-input\"]").press("Enter")
                time.sleep(2)
                # Click [data-testid="conversation-menu-button"] [aria-label="Mais opções"]
                # indo em opções de contato
                await page.locator('//*[@id="main"]/header/div[3]/div/div[2]/div/div/span').click()
                # Click text=Fechar conversa
                # fechando a conversa
                await page.locator("text=Fechar conversa").click()

                # opções para selecionar apenas não lidas
                for i in range(2):
                    await page.locator('//*[@id="side"]/div[3]/div/button/div/span').click()

                # apenas não lidas selecionadas
                await page.locator('//*[@id="app"]/div/span[4]/div/ul/div/li[1]/div/div[2]').click()
                await page.locator('//*[@id="app"]/div/div/div[4]/div/div/div[2]/div[1]/div').click()

                if atualizar1 != str('1'):
                    # atualiza no banco resposta aqui
                    conectar = mysql.connector.connect(
                        host=cx.h, database=cx.d, user=cx.u, password=cx.p)

                    b = str(campo1) + "=" + '\'' + str(atualizar1)+'\','
                    c = str(campo2) + "=" + '\'' + str(atualizar2)+'\','
                    d = str(campo3) + "=" + '\'' + str(atualizar3)+'\''

                    declaracao = "UPDATE `processo_atendimento` SET"
                    filtro = "WHERE `ID` like " + \
                        '\'%' + str(resultados[2])+'%\''
                    sql = declaracao + str(b) + str(c) + str(d) + str(filtro)

                    print(sql)
                    # popular dados
                    try:
                        cursor = conectar.cursor()

                        # executar comando
                        cursor.execute(sql)
                        conectar.commit()
                        conectar.close()
                    except:
                        conectar.close()
                    continue
                else:  # se nenhuma condição for atendida, chat informa que não atendeu e sugere reinicio ou selecionar opçãoa anterior enviada.
                    print('entrando no else')
                    # click p
                    # digitando mensagem
                    await page.locator("p").fill(str(msg.elses))
                    # Press Enter
                    # enviando mensagem
                    await page.locator("[data-testid=\"conversation-compose-box-input\"]").press("Enter")
                    time.sleep(2)
                    # Click [data-testid="conversation-menu-button"] [aria-label="Mais opções"]
                    # indo em opções do contato
                    await page.locator('//*[@id="main]/header/div[3]/div/div[2]/div/div/span').click()
                    # Click text=Fechar conversa
                    # fechando conversa
                    await page.locator("text=Fechar conversa").click()

                    # opções para selecionar apenas não lidas
                    for i in range(2):
                        await page.locator('//*[@id="side]/div[1]/div/button/div/span').click()

                    # apenas não lidas selecionadas
                    await page.locator('//*[@id="app"]/div/span[4]/div/ul/div/li[1]/div/div[2]').click()
                    await page.locator('//*[@id="app"]/div/div/div[4]/div/div/div[2]/div[1]/h1').click()
        except:
            time.sleep(1)
            continue


async def main() -> None:
    async with async_playwright() as playwright:
        await run(playwright)
asyncio.run(main())
